public with sharing class RLM_MFG_OrderToServiceContract {

    private static final String SERVICE_CONTRACT_TOKEN = 'Service Contract';
    private static final String MAINTENANCE_VISIT_TOKEN = 'Maintenance Visit';
    private static final Integer ENTITLEMENT_NAME_MAX = 80;

    @InvocableMethod(label='Create Service Contracts from Order' description='Creates one service contract with entitlements and a contract line item per covered-asset parent quote line on the related quote' category='Service Contract')
    public static List<Result> createServiceContracts(List<Request> requests) {
        if (requests == null || requests.isEmpty() || requests[0].orderId == null) {
            throw new RLM_MFG_OrderToServiceContractException('No order id was provided.');
        }

        Request req = requests[0];
        Id orderId = toId(req.orderId, 'order id');

        // ── Order + account + quote context ───────────────────────────────────────
        List<Order> orders = [
            SELECT Id, AccountId, QuoteId, Pricebook2Id, Quote.ContactId,
                   Account.BillingStreet, Account.BillingCity, Account.BillingState,
                   Account.BillingPostalCode, Account.BillingCountry,
                   Account.ShippingStreet, Account.ShippingCity, Account.ShippingState,
                   Account.ShippingPostalCode, Account.ShippingCountry
            FROM Order WHERE Id = :orderId WITH USER_MODE LIMIT 1
        ];
        if (orders.isEmpty()) {
            throw new RLM_MFG_OrderToServiceContractException('Order not found: ' + orderId);
        }
        Order ord = orders[0];
        if (ord.QuoteId == null) {
            throw new RLM_MFG_OrderToServiceContractException('Order ' + orderId + ' has no related quote.');
        }

        // ── All covered-asset service-contract parent quote lines for the quote ───
        List<QuoteLineItem> parentQLs = [
            SELECT Id, QuoteId, Product2Id, ProductSellingModelId, StartDate, EndDate,
                   Quantity, ListPrice, NetUnitPrice,
                   RLM_MFG_Covered_Asset__c, RLM_MFG_Covered_Asset__r.Name,
                   RLM_MFG_Covered_Asset__r.Product2Id, RLM_MFG_Product_Name_formula__c
            FROM QuoteLineItem
            WHERE QuoteId = :ord.QuoteId
              AND RLM_MFG_Product_Name_formula__c LIKE :('%' + SERVICE_CONTRACT_TOKEN + '%')
            WITH USER_MODE
        ];
        if (parentQLs.isEmpty()) {
            throw new RLM_MFG_OrderToServiceContractException(
                'No service contract quote lines found on quote ' + ord.QuoteId + '.');
        }

        Set<Id> parentIds = new Set<Id>();
        Set<Id> parentProductIds = new Set<Id>();
        for (QuoteLineItem p : parentQLs) {
            parentIds.add(p.Id);
            if (p.Product2Id != null) parentProductIds.add(p.Product2Id);
        }

        // ── Child entitlement quote lines, grouped by parent ──────────────────────
        Map<Id, List<QuoteLineItem>> childrenByParent = new Map<Id, List<QuoteLineItem>>();
        for (QuoteLineItem child : [
            SELECT Id, ParentQuoteLineItemId, Quantity, StartDate, EndDate,
                   RLM_MFG_Product_Name_formula__c
            FROM QuoteLineItem
            WHERE QuoteId = :ord.QuoteId AND ParentQuoteLineItemId IN :parentIds
            WITH USER_MODE
        ]) {
            if (!childrenByParent.containsKey(child.ParentQuoteLineItemId)) {
                childrenByParent.put(child.ParentQuoteLineItemId, new List<QuoteLineItem>());
            }
            childrenByParent.get(child.ParentQuoteLineItemId).add(child);
        }

        // ── Pricebook entries for the parent products (for the contract line item) ─
        // A product can have multiple PricebookEntries in one pricebook, one per selling
        // model, so key by Product2Id + ProductSellingModelId to select the entry that
        // matches the quote line's selling model rather than letting an arbitrary row win.
        Map<String, Id> pbeByProductAndModel = new Map<String, Id>();
        if (ord.Pricebook2Id != null && !parentProductIds.isEmpty()) {
            for (PricebookEntry pbe : [
                SELECT Id, Product2Id, ProductSellingModelId
                FROM PricebookEntry
                WHERE Pricebook2Id = :ord.Pricebook2Id AND Product2Id IN :parentProductIds
                WITH USER_MODE
            ]) {
                pbeByProductAndModel.put(pbeKey(pbe.Product2Id, pbe.ProductSellingModelId), pbe.Id);
            }
        }

        Boolean single = parentQLs.size() == 1;
        Id effAccountId = req.accountId != null ? toId(req.accountId, 'account id') : ord.AccountId;
        Id effContactId = req.contactId != null ? toId(req.contactId, 'contact id') : ord.Quote.ContactId;

        // ── Build service contracts (one per parent line) ─────────────────────────
        // Retain each contract's effective start/end by parent QL so the contract line
        // item can inherit the same dates instead of recomputing a divergent range.
        Map<Id, Date> effStartByParent = new Map<Id, Date>();
        Map<Id, Date> effEndByParent   = new Map<Id, Date>();
        List<ServiceContract> contracts = new List<ServiceContract>();
        for (QuoteLineItem p : parentQLs) {
            String assetName = (p.RLM_MFG_Covered_Asset__r != null && p.RLM_MFG_Covered_Asset__r.Name != null)
                ? p.RLM_MFG_Covered_Asset__r.Name : '';
            String autoName = (assetName + ' Service Contract').trim();

            ServiceContract sc = new ServiceContract();
            sc.Name = (single && String.isNotBlank(req.serviceContractName)) ? req.serviceContractName : autoName;
            sc.AccountId = effAccountId;
            sc.ContactId = effContactId;
            sc.Pricebook2Id = ord.Pricebook2Id;
            sc.RLM_MFG_Quote__c = ord.QuoteId;
            sc.Description = req.description;
            // Use today as the start date so Status auto-calculates to Active immediately.
            // The screen override is still honoured for single-asset cases.
            Date effStart = (single && req.startDateOverride != null) ? req.startDateOverride : Date.today();
            Date effEnd   = (single && req.endDateOverride != null)   ? req.endDateOverride
                          : (p.EndDate != null ? p.EndDate : Date.today().addYears(1));
            sc.StartDate = effStart;
            sc.EndDate   = effEnd;
            effStartByParent.put(p.Id, effStart);
            effEndByParent.put(p.Id, effEnd);

            if (ord.Account != null) {
                sc.BillingStreet     = ord.Account.BillingStreet;
                sc.BillingCity       = ord.Account.BillingCity;
                sc.BillingState      = ord.Account.BillingState;
                sc.BillingPostalCode = ord.Account.BillingPostalCode;
                sc.BillingCountry    = ord.Account.BillingCountry;
                sc.ShippingStreet     = ord.Account.ShippingStreet;
                sc.ShippingCity       = ord.Account.ShippingCity;
                sc.ShippingState      = ord.Account.ShippingState;
                sc.ShippingPostalCode = ord.Account.ShippingPostalCode;
                sc.ShippingCountry    = ord.Account.ShippingCountry;
            }
            contracts.add(sc);
        }
        insert as user contracts;

        // Map parent QL -> its new service contract (positional, same order as parentQLs)
        Map<Id, Id> contractByParent = new Map<Id, Id>();
        for (Integer i = 0; i < parentQLs.size(); i++) {
            contractByParent.put(parentQLs[i].Id, contracts[i].Id);
        }

        // ── Build entitlements (per child line; maintenance lines expand by qty) ──
        List<Entitlement> entitlements = new List<Entitlement>();
        for (QuoteLineItem p : parentQLs) {
            Id contractId = contractByParent.get(p.Id);
            List<QuoteLineItem> kids = childrenByParent.get(p.Id);
            if (kids == null) continue;

            for (QuoteLineItem child : kids) {
                // Counter starts fresh for every child line (fixes never-reset bug)
                Integer copies = copiesForChild(child);
                for (Integer c = 0; c < copies; c++) {
                    entitlements.add(buildEntitlement(child, contractId, effAccountId));
                }
            }
        }
        if (!entitlements.isEmpty()) {
            insert as user entitlements;
        }

        // ── Build one contract line item per parent line ──────────────────────────
        List<ContractLineItem> contractLines = new List<ContractLineItem>();
        for (QuoteLineItem p : parentQLs) {
            // PricebookEntryId is required on ContractLineItem; Product2Id and ListPrice
            // are then derived from it by the platform. If the parent product has no
            // PricebookEntry in the order's pricebook (or the order has no pricebook),
            // fail with a friendly error rather than a raw REQUIRED_FIELD_MISSING on insert.
            Id pbeId = pbeByProductAndModel.get(pbeKey(p.Product2Id, p.ProductSellingModelId));
            if (pbeId == null) {
                throw new RLM_MFG_OrderToServiceContractException(
                    'No PricebookEntry found for product ' + p.Product2Id + ' (selling model '
                    + p.ProductSellingModelId + ') in the order pricebook ' + ord.Pricebook2Id
                    + '. A contract line item cannot be created without one.');
            }
            ContractLineItem cli = new ContractLineItem();
            cli.ServiceContractId = contractByParent.get(p.Id);
            // Inherit the parent service contract's effective dates so the line item
            // cannot diverge from its contract (e.g. an overridden/future contract).
            cli.StartDate = effStartByParent.get(p.Id);
            cli.EndDate   = effEndByParent.get(p.Id);
            cli.AssetId = p.RLM_MFG_Covered_Asset__c;
            cli.Quantity = p.Quantity;
            cli.UnitPrice = p.NetUnitPrice;
            cli.PricebookEntryId = pbeId;
            contractLines.add(cli);
        }
        if (!contractLines.isEmpty()) {
            insert as user contractLines;
        }

        List<Result> results = new List<Result>();
        Result r = new Result();
        r.serviceContractIds = new List<String>();
        for (ServiceContract sc : contracts) {
            r.serviceContractIds.add(sc.Id);
        }
        r.primaryServiceContractId = contracts[0].Id;
        results.add(r);
        return results;
    }

    // Composite key for the PricebookEntry lookup: a product may have one entry per
    // selling model in the same pricebook, so both parts identify the correct entry.
    private static String pbeKey(Id productId, Id sellingModelId) {
        return String.valueOf(productId) + ';' + String.valueOf(sellingModelId);
    }

    // Validates a String invocable input as an Id, converting a malformed value into a
    // friendly, catchable error instead of a raw System.StringException on the cast.
    private static Id toId(String value, String label) {
        try {
            return Id.valueOf(value);
        } catch (Exception e) {
            throw new RLM_MFG_OrderToServiceContractException('Invalid ' + label + ': ' + value);
        }
    }

    // Maintenance-visit lines expand into one entitlement per unit of quantity;
    // every other line yields exactly one. Counter is implicit (per call), so it
    // can never leak across child lines.
    @TestVisible
    private static Integer copiesForChild(QuoteLineItem child) {
        String name = child.RLM_MFG_Product_Name_formula__c;
        Boolean isMaintenance = name != null && name.contains(MAINTENANCE_VISIT_TOKEN);
        if (!isMaintenance) {
            return 1;
        }
        Integer qty = (child.Quantity != null) ? child.Quantity.intValue() : 1;
        return Math.max(qty, 1);
    }

    private static Entitlement buildEntitlement(QuoteLineItem child, Id contractId, Id accountId) {
        // Entitlement.Status is a platform-calculated field (derived from Start/End dates)
        Entitlement e = new Entitlement();
        e.AccountId = accountId;
        e.ServiceContractId = contractId;
        // Honour the quoted entitlement dates; fall back to today / +1yr only when null.
        e.StartDate = (child.StartDate != null ? child.StartDate : Date.today());
        e.EndDate   = (child.EndDate != null ? child.EndDate : Date.today().addYears(1));
        String name = child.RLM_MFG_Product_Name_formula__c;
        if (name != null && name.length() > ENTITLEMENT_NAME_MAX) {
            name = name.substring(0, ENTITLEMENT_NAME_MAX);
        }
        e.Name = name;
        return e;
    }

    public class Request {
        @InvocableVariable(required=true label='Order Id')
        public String orderId;

        @InvocableVariable(label='Service Contract Name (single-asset override)')
        public String serviceContractName;

        @InvocableVariable(label='Description')
        public String description;

        @InvocableVariable(label='Start Date (single-asset override)')
        public Date startDateOverride;

        @InvocableVariable(label='End Date (single-asset override)')
        public Date endDateOverride;

        @InvocableVariable(label='Account Id')
        public String accountId;

        @InvocableVariable(label='Contact Id')
        public String contactId;
    }

    public class Result {
        @InvocableVariable(label='Created Service Contract Ids')
        public List<String> serviceContractIds;

        @InvocableVariable(label='Primary Service Contract Id')
        public String primaryServiceContractId;
    }

    public class RLM_MFG_OrderToServiceContractException extends Exception {}
}
