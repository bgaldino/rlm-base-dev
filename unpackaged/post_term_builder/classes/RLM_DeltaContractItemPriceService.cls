public with sharing class RLM_DeltaContractItemPriceService {

    private static final String OPTION_NET_UNIT_PRICE_ONLY = 'NET_UNIT_PRICE_ONLY';
    private static final String OPTION_DISCOUNT_ONLY = 'DISCOUNT_ONLY';

    public class Request {
        @InvocableVariable(required=true)
        public Id contractId;
        @InvocableVariable(required=true)
        public Id quoteId;
        @InvocableVariable(required=true)
        public String pricingOption;
    }

    public class Response {
        @InvocableVariable
        public Boolean isSuccess;
        @InvocableVariable
        public Integer createdCount;
        @InvocableVariable
        public String errorMessage;
    }

    @InvocableMethod(label='Create Contract Item Prices From Quote (Delta)' description='Creates ContractItemPrice records (with attribute-set hash and lineage) for each eligible line on a Quote.')
    public static List<Response> createContractItemPrices(List<Request> requests) {
        List<Response> responses = new List<Response>();
        for (Request req : requests) {
            responses.add(createForOneQuote(req));
        }
        return responses;
    }

    private static Response createForOneQuote(Request req) {
        Response res = new Response();
        try {
            res.createdCount = process(req);
            res.isSuccess = true;
            res.errorMessage = null;
        } catch (Exception e) {
            res.isSuccess = false;
            res.createdCount = 0;
            res.errorMessage = e.getMessage();
            throw e;
        }
        return res;
    }

    private static Integer process(Request req) {
        List<QuoteLineItem> lines = queryEligibleLines(req.quoteId, req.pricingOption);
        if (lines.isEmpty()) {
            return 0;
        }

        Date contractStartDate = queryContractStartDate(req.contractId);
        Map<Id, List<QuoteLineItemAttribute>> attrsByLineId = queryAttributesByLineId(lines);

        List<ContractItemPrice> cips = new List<ContractItemPrice>();
        Map<Integer, List<QuoteLineItemAttribute>> attrGroupsByLineIndex = new Map<Integer, List<QuoteLineItemAttribute>>();

        for (Integer i = 0; i < lines.size(); i++) {
            QuoteLineItem line = lines[i];
            List<QuoteLineItemAttribute> lineAttrs = attrsByLineId.containsKey(line.Id)
                ? attrsByLineId.get(line.Id)
                : new List<QuoteLineItemAttribute>();
            attrGroupsByLineIndex.put(i, lineAttrs);

            Date lineStartDate = clampToContractStart(line.StartDate, contractStartDate);
            ContractItemPrice cip = new ContractItemPrice(
                ContractId = req.contractId,
                ItemId = line.Product2Id,
                ProductSellingModelId = line.ProductSellingModelId,
                DL_Attribute_Set_Hash__c = RLM_DeltaAttributeSetHashUtil.computeHash(lineAttrs),
                DL_Source_Quote_Line_Item__c = line.Id,
                DL_Custom_Product_Name__c = line.CustomProductName,
                StartDate = toStartOfDay(lineStartDate),
                EndDate = toEndOfDay(line.EndDate)
            );

            if (req.pricingOption == OPTION_NET_UNIT_PRICE_ONLY) {
                cip.Price = line.NetUnitPrice;
            } else if (req.pricingOption == OPTION_DISCOUNT_ONLY) {
                if (line.Discount != null) {
                    cip.DiscountType = 'AdjustmentPercentage';
                    cip.DiscountValue = line.Discount;
                } else if (line.DiscountAmount != null) {
                    cip.DiscountType = 'AdjustmentAmount';
                    cip.DiscountValue = line.DiscountAmount;
                }
            }

            cips.add(cip);
        }

        List<DL_Contract_Item_Price_Attribute__c> childRows = new List<DL_Contract_Item_Price_Attribute__c>();
        for (Integer i = 0; i < cips.size(); i++) {
            for (QuoteLineItemAttribute attr : attrGroupsByLineIndex.get(i)) {
                RLM_DeltaAttributeSetHashUtil.ResolvedAttribute resolved = RLM_DeltaAttributeSetHashUtil.resolve(attr);
                DL_Contract_Item_Price_Attribute__c childRow = new DL_Contract_Item_Price_Attribute__c(
                    DL_Attribute_Definition__c = resolved.attributeDefinitionId
                );
                if (resolved.isPicklist) {
                    childRow.DL_Attribute_Picklist_Value__c = resolved.picklistValueId;
                } else {
                    childRow.DL_Attribute_Value__c = resolved.freeTextValue;
                }
                childRows.add(childRow);
            }
        }

        Savepoint sp = Database.setSavepoint();
        try {
            insert as user cips;

            assignChildRowParents(cips, attrGroupsByLineIndex, childRows);

            if (!childRows.isEmpty()) {
                insert as user childRows;
            }

            // Second pass: mirror the source Quote's bundle structure onto the CIPs. The
            // self-lookup needs the inserted parent's Id, so it cannot be set before insert.
            List<ContractItemPrice> reparented = linkBundleParents(cips, lines);
            if (!reparented.isEmpty()) {
                update as user reparented;
            }
        } catch (Exception e) {
            Database.rollback(sp);
            throw e;
        }

        return cips.size();
    }

    /**
     * Stamps DL_Parent_Contract_Item_Price__c on each CIP whose source QuoteLineItem is a bundle
     * child, mirroring the Quote's Term→fare structure. Parent resolution matches
     * RLM_DeltaTermBuilderController.getBuilderState: ParentQuoteLineItemId first, then the
     * QuoteLineRelationship root fallback for children the platform left unstamped. Returns only
     * the CIPs that were changed (so the caller can skip a no-op DML).
     */
    private static List<ContractItemPrice> linkBundleParents(List<ContractItemPrice> cips, List<QuoteLineItem> lines) {
        // Map each generated CIP back to its source QuoteLineItem.
        Map<Id, ContractItemPrice> cipBySourceQli = new Map<Id, ContractItemPrice>();
        for (ContractItemPrice cip : cips) {
            if (cip.DL_Source_Quote_Line_Item__c != null) {
                cipBySourceQli.put(cip.DL_Source_Quote_Line_Item__c, cip);
            }
        }

        // Fallback child→root map for lines whose ParentQuoteLineItemId was never stamped.
        Set<Id> lineIds = new Set<Id>();
        for (QuoteLineItem line : lines) {
            lineIds.add(line.Id);
        }
        Map<Id, Id> rootByChild = queryRootByChild(lineIds);

        List<ContractItemPrice> reparented = new List<ContractItemPrice>();
        for (QuoteLineItem line : lines) {
            Id parentQliId = (line.ParentQuoteLineItemId != null)
                ? line.ParentQuoteLineItemId
                : rootByChild.get(line.Id);
            if (parentQliId == null) {
                continue;
            }
            // Guard: only link when the parent line also produced a CIP (in practice always true,
            // since every bundle member — including 0%-discount lines — is eligible).
            ContractItemPrice parentCip = cipBySourceQli.get(parentQliId);
            ContractItemPrice childCip = cipBySourceQli.get(line.Id);
            if (parentCip == null || childCip == null || parentCip.Id == childCip.Id) {
                continue;
            }
            // Update via a minimal Id-only shell carrying ONLY the parent field. Re-updating the
            // fully-populated inserted CIP would make `update as user` enforce update-access on
            // every dirty field, including ContractId (createable but NOT updateable) — which
            // throws "fields being inaccessible on Sobject ContractItemPrice" in USER_MODE.
            reparented.add(new ContractItemPrice(
                Id = childCip.Id,
                DL_Parent_Contract_Item_Price__c = parentCip.Id
            ));
        }
        return reparented;
    }

    private static Map<Id, Id> queryRootByChild(Set<Id> lineIds) {
        Map<Id, Id> rootByChild = new Map<Id, Id>();
        if (lineIds.isEmpty()) {
            return rootByChild;
        }
        for (QuoteLineRelationship r : [
            SELECT AssociatedQuoteLineId, RootQuoteLineId
            FROM QuoteLineRelationship
            WHERE AssociatedQuoteLineId IN :lineIds AND RootQuoteLineId != null
            WITH USER_MODE
        ]) {
            if (r.AssociatedQuoteLineId != null && r.RootQuoteLineId != null
                && r.AssociatedQuoteLineId != r.RootQuoteLineId) {
                rootByChild.put(r.AssociatedQuoteLineId, r.RootQuoteLineId);
            }
        }
        return rootByChild;
    }

    private static void assignChildRowParents(
        List<ContractItemPrice> cips,
        Map<Integer, List<QuoteLineItemAttribute>> attrGroupsByLineIndex,
        List<DL_Contract_Item_Price_Attribute__c> childRows
    ) {
        Integer childRowIndex = 0;
        for (Integer i = 0; i < cips.size(); i++) {
            Integer attrCount = attrGroupsByLineIndex.get(i).size();
            for (Integer j = 0; j < attrCount; j++) {
                childRows[childRowIndex].DL_Contract_Item_Price__c = cips[i].Id;
                childRowIndex++;
            }
        }
    }

    private static List<QuoteLineItem> queryEligibleLines(Id quoteId, String pricingOption) {
        String whereClause = (pricingOption == OPTION_NET_UNIT_PRICE_ONLY)
            ? 'NetUnitPrice != null'
            : 'Discount != null OR DiscountAmount != null';

        return Database.query(
            'SELECT Id, ParentQuoteLineItemId, Product2Id, ProductSellingModelId, CustomProductName, NetUnitPrice, Discount, DiscountAmount, StartDate, EndDate ' +
            'FROM QuoteLineItem ' +
            'WHERE QuoteId = :quoteId AND (' + whereClause + ') ' +
            'WITH USER_MODE'
        );
    }

    private static Map<Id, List<QuoteLineItemAttribute>> queryAttributesByLineId(List<QuoteLineItem> lines) {
        Set<Id> lineIds = new Set<Id>();
        for (QuoteLineItem line : lines) {
            lineIds.add(line.Id);
        }

        Map<Id, List<QuoteLineItemAttribute>> byLineId = new Map<Id, List<QuoteLineItemAttribute>>();
        List<QuoteLineItemAttribute> allAttrs = [
            SELECT QuoteLineItemId, AttributeDefinitionId, AttributePicklistValueId, AttributeValue
            FROM QuoteLineItemAttribute
            WHERE QuoteLineItemId IN :lineIds
            WITH USER_MODE
        ];
        for (QuoteLineItemAttribute attr : allAttrs) {
            if (!byLineId.containsKey(attr.QuoteLineItemId)) {
                byLineId.put(attr.QuoteLineItemId, new List<QuoteLineItemAttribute>());
            }
            byLineId.get(attr.QuoteLineItemId).add(attr);
        }
        return byLineId;
    }

    private static Date queryContractStartDate(Id contractId) {
        List<Contract> contracts = [SELECT StartDate FROM Contract WHERE Id = :contractId WITH USER_MODE];
        return contracts.isEmpty() ? null : contracts[0].StartDate;
    }

    /**
     * The platform rejects a ContractItemPrice.StartDate that precedes its parent Contract's own
     * StartDate. Term/fare QuoteLineItem.StartDate is seeded independently at line-add time (see
     * RLM_DeltaTermBuilderController.buildTermLineFields/buildFareLineFields) and can predate the
     * Contract's StartDate, which createContract sets separately (defaulting to today when the
     * source Quote's standard StartDate is null) — so clamp up to the Contract's StartDate here,
     * the same floor the platform already applies for a null line StartDate.
     */
    private static Date clampToContractStart(Date lineStartDate, Date contractStartDate) {
        if (contractStartDate == null || lineStartDate == null) {
            return lineStartDate;
        }
        return (lineStartDate < contractStartDate) ? contractStartDate : lineStartDate;
    }

    // GMT-anchored, matching RLM_DeltaTermBuilderController.isoTimestamp: DateTime.newInstance()
    // constructs the instant in the running user's local timezone, so a non-UTC user (e.g.
    // Europe/London in BST) shifts midnight local back into the PREVIOUS UTC day — enough to fail
    // the platform's "StartDate on or after the Contract's StartDate" check even when the calendar
    // dates otherwise match.
    private static DateTime toStartOfDay(Date d) {
        return d == null ? null : DateTime.newInstanceGmt(d, Time.newInstance(0, 0, 0, 0));
    }

    private static DateTime toEndOfDay(Date d) {
        return d == null ? null : DateTime.newInstanceGmt(d, Time.newInstance(23, 59, 59, 0));
    }
}
