/**
 * Apex controller for the rlmContractedPricingLineEditor LWC — a grouped, read-only tree view of a
 * Quote's lines with editing of Discount %, Start date, and End date per line (rate-card
 * negotiation).
 *
 * Mutations persist via direct DML (`update`/`delete as user`) because that is the only path that
 * reliably writes both standard and custom fields — notably DL_FareCodes__c and CustomProductName,
 * which a PST PATCH silently drops (PST's PATCH is a pricing operation, not a general field-writer).
 * Direct DML does NOT run the pricing procedure, though, so the platform stamps
 * Quote.ValidationResult = TransactionIncomplete and leaves prices stale. Each mutation therefore ends
 * with a best-effort RLM_DeltaPlaceSalesTransaction.revalidate(quoteId) — a header-only PST reprice
 * that clears the flag and recomputes totals over the just-persisted state without touching the
 * custom fields (live-verified 2026-07-20 on Delta). See that helper for the full rationale.
 *
 * House conventions: JSON-in/JSON-out @AuraEnabled methods; Id.valueOf guarded; WITH USER_MODE
 * reads / `update as user` DML; aggregate COUNT()/GROUP BY for counts; no SOQL/DML in loops.
 */
public with sharing class RLM_DeltaLineController {
    public class LineEditorException extends Exception {}

    // Stable SKU that marks a Term root — the only line type whose name is inline-editable.
    @TestVisible private static final String TERM_SKU = 'DL-TERM';
    // Platform max length for QuoteLineItem.CustomProductName.
    @TestVisible private static final Integer CUSTOM_PRODUCT_NAME_MAX = 80;

    /**
     * Nested tree of the quote's groups + lines (mirrors RLM_SetUpQuoteInvocable.getQuoteHierarchy).
     * cacheable=true so the LWC can @wire it and refreshApex after edits/adds.
     * Returns { isSuccess, groups:[{ id, name, parentId, lineCount, lines:[...], children:[...] }],
     * ungrouped:[{ ...line }] }.
     */
    @AuraEnabled(cacheable=true)
    public static String getQuoteLines(String quoteId) {
        try {
            Id qId = parseId(quoteId, 'quoteId');

            List<QuoteLineGroup> groups = [
                SELECT Id, Name, ParentQuoteLineGroupId, SortOrder
                FROM QuoteLineGroup
                WHERE QuoteId = :qId
                WITH USER_MODE
                ORDER BY ParentQuoteLineGroupId NULLS FIRST, SortOrder NULLS LAST, Name
            ];

            // All lines for the quote in one query. ParentQuoteLineItemId drives the LWC's bundle
            // indentation; Product2Id / Product2.BasedOnId feed the bulk editable-attribute probe.
            List<QuoteLineItem> allLines = [
                SELECT Id, QuoteLineGroupId, ParentQuoteLineItemId, Product2Id, Product2.Name,
                       Product2.ProductCode, Product2.StockKeepingUnit, Product2.BasedOnId,
                       CustomProductName, PricingContractId, Discount, DL_PriorDiscount__c,
                       StartDate, EndDate, NetUnitPrice, DL_FareCodes__c
                FROM QuoteLineItem
                WHERE QuoteId = :qId
                WITH USER_MODE
                ORDER BY QuoteLineGroupId NULLS FIRST, SortOrder NULLS LAST, Id
            ];

            // Bulk: which lines have at least one editable informational attribute (so the LWC can hide
            // the per-row Attributes action on lines with nothing to edit). One pass, no SOQL in loops.
            Map<Id, Boolean> editableByLine = computeEditableByLine(allLines);

            // Fallback child→parent map from QuoteLineRelationship: a bundle child (e.g. a fare under a
            // Term) is often linked only by the relationship, with ParentQuoteLineItemId left unstamped.
            // One query keyed by the quote's line ids; used to resolve parentLineId when it's null.
            Map<Id, Id> rootByChild = buildRelationshipParentMap(allLines);

            // Lines grouped in memory by their QuoteLineGroupId (null = ungrouped).
            Map<Id, List<Map<String, Object>>> linesByGroup = new Map<Id, List<Map<String, Object>>>();
            List<Map<String, Object>> ungrouped = new List<Map<String, Object>>();
            for (QuoteLineItem qli : allLines) {
                Map<String, Object> dto = lineDto(qli, editableByLine.get(qli.Id) == true, rootByChild.get(qli.Id));
                if (qli.QuoteLineGroupId == null) {
                    ungrouped.add(dto);
                } else {
                    if (!linesByGroup.containsKey(qli.QuoteLineGroupId)) {
                        linesByGroup.put(qli.QuoteLineGroupId, new List<Map<String, Object>>());
                    }
                    linesByGroup.get(qli.QuoteLineGroupId).add(dto);
                }
            }

            Map<Id, List<QuoteLineGroup>> childrenByParent = new Map<Id, List<QuoteLineGroup>>();
            List<QuoteLineGroup> roots = new List<QuoteLineGroup>();
            for (QuoteLineGroup g : groups) {
                if (g.ParentQuoteLineGroupId == null) {
                    roots.add(g);
                } else {
                    if (!childrenByParent.containsKey(g.ParentQuoteLineGroupId)) {
                        childrenByParent.put(g.ParentQuoteLineGroupId, new List<QuoteLineGroup>());
                    }
                    childrenByParent.get(g.ParentQuoteLineGroupId).add(g);
                }
            }

            List<Object> rootNodes = new List<Object>();
            for (QuoteLineGroup g : roots) {
                rootNodes.add(buildGroupNode(g, childrenByParent, linesByGroup));
            }
            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'groups' => rootNodes,
                'ungrouped' => ungrouped
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Bulk-update Discount %, Start date, End date for the given lines.
     * Input: { quoteId, lines:[{ id, discount, startDate, endDate }] }.
     * Fail-closed ownership guard: every requested id must belong to the quote, else the whole
     * request is rejected. All values validated before any DML; one bulk `update as user`.
     */
    @AuraEnabled(cacheable=false)
    public static String updateLineDiscountAndDates(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id qId = parseId(asString(in0.get('quoteId')), 'quoteId');

            List<Object> lineObjs = (in0.get('lines') instanceof List<Object>) ? (List<Object>) in0.get('lines') : null;
            if (lineObjs == null || lineObjs.isEmpty()) {
                throw new LineEditorException('No lines to update.');
            }

            // Index requested edits by line id (last write wins for a duplicated id).
            Map<Id, Map<String, Object>> editsById = new Map<Id, Map<String, Object>>();
            for (Object o : lineObjs) {
                Map<String, Object> edit = (Map<String, Object>) o;
                Id lineId = parseId(asString(edit.get('id')), 'line id');
                editsById.put(lineId, edit);
            }

            // Ownership guard (fail-closed): every requested id must be on this quote. Also load the
            // product name + SKU + current custom name so a fare-code edit can auto-name the fare line.
            Map<Id, QuoteLineItem> ownedById = new Map<Id, QuoteLineItem>([
                SELECT Id, CustomProductName, Product2.Name, Product2.ProductCode, Product2.StockKeepingUnit
                FROM QuoteLineItem WHERE QuoteId = :qId AND Id IN :editsById.keySet() WITH USER_MODE
            ]);
            for (Id requestedId : editsById.keySet()) {
                if (!ownedById.containsKey(requestedId)) {
                    throw new LineEditorException('Line ' + requestedId + ' does not belong to this quote.');
                }
            }

            // Validate all edits before any DML.
            List<QuoteLineItem> toUpdate = new List<QuoteLineItem>();
            for (Id lineId : editsById.keySet()) {
                Map<String, Object> edit = editsById.get(lineId);
                Decimal discount = asDecimal(edit.get('discount'));
                Date startDate = asDate(edit.get('startDate'));
                Date endDate = asDate(edit.get('endDate'));
                if (discount != null && (discount < 0 || discount > 100)) {
                    throw new LineEditorException('Discount must be between 0 and 100 (line ' + lineId + ').');
                }
                if (startDate != null && endDate != null && endDate < startDate) {
                    throw new LineEditorException('End date must be on or after start date (line ' + lineId + ').');
                }
                QuoteLineItem qli = new QuoteLineItem(Id = lineId);
                // Only stamp fields the client actually supplied, so partial edits don't clobber.
                if (edit.containsKey('discount')) {
                    qli.Discount = discount;
                }
                if (edit.containsKey('startDate')) {
                    qli.StartDate = startDate;
                }
                if (edit.containsKey('endDate')) {
                    qli.EndDate = endDate;
                }
                if (edit.containsKey('fareCodes')) {
                    // Fare codes arrive as a list; store as the ';'-delimited multipicklist value
                    // (empty list ⇒ null, clearing the field).
                    List<String> codes = normalizeFareCodes(edit.get('fareCodes'));
                    qli.DL_FareCodes__c = codes.isEmpty() ? null : String.join(codes, ';');
                    // Auto-name a fare line to reflect its selected codes, e.g. "Comfort (W S J)".
                    // Terms are never fare lines and keep their (separately-editable) custom name, so
                    // this only decorates non-Term rows. Clearing all codes reverts to the base name.
                    QuoteLineItem owned = ownedById.get(lineId);
                    if (owned != null && !isTermSku(owned)) {
                        qli.CustomProductName = buildFareDisplayName(owned, codes);
                    }
                }
                toUpdate.add(qli);
            }

            update as user toUpdate;

            // Direct DML persisted the fields but skipped pricing, stamping ValidationResult =
            // TransactionIncomplete. Reprice through PST to clear it (best-effort; the edits are
            // already committed either way).
            RLM_DeltaPlaceSalesTransaction.revalidate(qId);

            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'updatedCount' => toUpdate.size(),
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Delete one or more lines from a quote.
     * Input: { quoteId, lineIds:[...] }.
     * Fail-closed ownership guard: every requested id must belong to the quote, else the whole
     * request is rejected. All values validated before any DML; one bulk `delete as user`.
     */
    @AuraEnabled(cacheable=false)
    public static String deleteLines(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id qId = parseId(asString(in0.get('quoteId')), 'quoteId');

            List<Object> idObjs = (in0.get('lineIds') instanceof List<Object>) ? (List<Object>) in0.get('lineIds') : null;
            if (idObjs == null || idObjs.isEmpty()) {
                throw new LineEditorException('No lines to delete.');
            }
            Set<Id> requestedIds = new Set<Id>();
            for (Object o : idObjs) {
                requestedIds.add(parseId(asString(o), 'line id'));
            }

            // Ownership guard (fail-closed): every requested id must be on this quote.
            Map<Id, QuoteLineItem> ownedById = new Map<Id, QuoteLineItem>([
                SELECT Id FROM QuoteLineItem WHERE QuoteId = :qId AND Id IN :requestedIds WITH USER_MODE
            ]);
            for (Id requestedId : requestedIds) {
                if (!ownedById.containsKey(requestedId)) {
                    throw new LineEditorException('Line ' + requestedId + ' does not belong to this quote.');
                }
            }

            delete as user ownedById.values();

            // Removing lines outside the pricing flow also stamps ValidationResult; reprice the
            // remaining quote to clear it (best-effort — safe even when the quote is now empty).
            RLM_DeltaPlaceSalesTransaction.revalidate(qId);

            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'deletedCount' => ownedById.size(),
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Rename a Term root's CustomProductName. Input: { quoteId, lineId, customProductName }.
     * Fail-closed: the line must belong to the quote AND be a DL-TERM root (only Term rows are
     * renameable). A blank value clears the custom name (reverting the grid to the Product2.Name
     * fallback). The platform max is 80 chars. One record `update as user`.
     * Returns { isSuccess, customProductName, errorMessage }.
     */
    @AuraEnabled(cacheable=false)
    public static String updateTermName(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id qId = parseId(asString(in0.get('quoteId')), 'quoteId');
            Id lineId = parseId(asString(in0.get('lineId')), 'lineId');

            String newName = asString(in0.get('customProductName'));
            newName = (newName == null) ? null : newName.trim();
            if (String.isNotBlank(newName) && newName.length() > CUSTOM_PRODUCT_NAME_MAX) {
                throw new LineEditorException('Term name must be ' + CUSTOM_PRODUCT_NAME_MAX + ' characters or fewer.');
            }

            // Ownership + Term guard (fail-closed): the line must be on this quote and be a DL-TERM.
            List<QuoteLineItem> lines = [
                SELECT Id, Product2.ProductCode, Product2.StockKeepingUnit
                FROM QuoteLineItem
                WHERE Id = :lineId AND QuoteId = :qId
                WITH USER_MODE
                LIMIT 1
            ];
            if (lines.isEmpty()) {
                throw new LineEditorException('Line ' + lineId + ' does not belong to this quote.');
            }
            if (!isTermSku(lines[0])) {
                throw new LineEditorException('Only a Term (' + TERM_SKU + ') can be renamed.');
            }

            QuoteLineItem qli = new QuoteLineItem(Id = lineId);
            qli.CustomProductName = String.isBlank(newName) ? null : newName;
            update as user qli;

            // The rename is a direct-DML edit, so clear the resulting TransactionIncomplete stamp
            // with a best-effort reprice (CustomProductName is untouched by the header-only pass).
            RLM_DeltaPlaceSalesTransaction.revalidate(qId);

            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'customProductName' => qli.CustomProductName,
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    // ---------- helpers ----------

    private static Map<String, Object> buildGroupNode(QuoteLineGroup g, Map<Id, List<QuoteLineGroup>> childrenByParent, Map<Id, List<Map<String, Object>>> linesByGroup) {
        List<Map<String, Object>> lines = linesByGroup.containsKey(g.Id) ? linesByGroup.get(g.Id) : new List<Map<String, Object>>();
        List<Object> children = new List<Object>();
        if (childrenByParent.containsKey(g.Id)) {
            for (QuoteLineGroup c : childrenByParent.get(g.Id)) {
                children.add(buildGroupNode(c, childrenByParent, linesByGroup));
            }
        }
        return new Map<String, Object>{
            'id' => g.Id,
            'name' => String.isNotBlank(g.Name) ? g.Name : ('Group ' + g.Id),
            'parentId' => g.ParentQuoteLineGroupId,
            'lineCount' => lines.size(),
            'lines' => lines,
            'children' => children
        };
    }

    /**
     * child line id → its Term root, from QuoteLineRelationship. Lets getQuoteLines resolve a
     * parentLineId for bundle children whose ParentQuoteLineItemId the platform left unstamped
     * (mirrors the fallback in RLM_DeltaTermBuilderController.getBuilderState). Keyed on the quote's
     * own line ids so it's one query with no unbounded scan. RootQuoteLineId is preferred (the Term);
     * MainQuoteLineId is the same as Root in this app's single-level bundles.
     */
    private static Map<Id, Id> buildRelationshipParentMap(List<QuoteLineItem> lines) {
        Map<Id, Id> rootByChild = new Map<Id, Id>();
        Set<Id> lineIds = new Set<Id>();
        for (QuoteLineItem qli : lines) {
            lineIds.add(qli.Id);
        }
        if (lineIds.isEmpty()) {
            return rootByChild;
        }
        for (QuoteLineRelationship r : [
            SELECT AssociatedQuoteLineId, RootQuoteLineId, MainQuoteLineId
            FROM QuoteLineRelationship
            WHERE AssociatedQuoteLineId IN :lineIds AND AssociatedQuoteLineId != null
            WITH USER_MODE
        ]) {
            Id parentId = (r.RootQuoteLineId != null) ? r.RootQuoteLineId : r.MainQuoteLineId;
            // Never map a line to itself; only keep parents that are lines on this quote.
            if (parentId != null && parentId != r.AssociatedQuoteLineId && lineIds.contains(parentId)) {
                rootByChild.put(r.AssociatedQuoteLineId, parentId);
            }
        }
        return rootByChild;
    }

    private static Map<String, Object> lineDto(QuoteLineItem qli, Boolean hasEditableAttributes, Id resolvedParentLineId) {
        Boolean isTerm = isTermSku(qli);
        String productName = (qli.Product2 != null) ? qli.Product2.Name : null;
        return new Map<String, Object>{
            'id' => qli.Id,
            // Prefer the platform-stamped parent; fall back to the QuoteLineRelationship root so a
            // fare linked to its Term only via the relationship (ParentQuoteLineItemId unstamped)
            // still nests under — and stays inside the scoped view of — its Term.
            'parentLineId' => (qli.ParentQuoteLineItemId != null) ? qli.ParentQuoteLineItemId : resolvedParentLineId,
            // Product2.Name fallback; the LWC prefers customProductName when populated.
            'productName' => String.isNotBlank(qli.CustomProductName) ? qli.CustomProductName : productName,
            'customProductName' => qli.CustomProductName,
            'catalogProductName' => productName,
            'productCode' => (qli.Product2 != null) ? qli.Product2.ProductCode : null,
            // Term roots (DL-TERM) are the only rows whose name may be inline-edited.
            'isTerm' => isTerm,
            'isContracted' => (qli.PricingContractId != null),
            'discount' => qli.Discount,
            // Frozen snapshot of the previous contract line's discount (renewal lines only; null
            // otherwise). Read-only in the grid — shown next to the editable Discount for comparison.
            'priorDiscount' => qli.DL_PriorDiscount__c,
            'startDate' => (qli.StartDate != null) ? String.valueOf(qli.StartDate) : null,
            'endDate' => (qli.EndDate != null) ? String.valueOf(qli.EndDate) : null,
            'netUnitPrice' => qli.NetUnitPrice,
            // Per-line fare codes (multipicklist, ';'-delimited on the record) as a list; edited only
            // on fare (non-Term) rows via the grid's dual-listbox.
            'fareCodes' => splitFareCodes(qli.DL_FareCodes__c),
            'hasEditableAttributes' => (hasEditableAttributes == true)
        };
    }

    /** A multipicklist value (';'-delimited) → its list of codes; blank ⇒ empty list. */
    private static List<String> splitFareCodes(String raw) {
        List<String> out = new List<String>();
        if (String.isBlank(raw)) {
            return out;
        }
        for (String part : raw.split(';')) {
            String code = part.trim();
            if (String.isNotBlank(code)) {
                out.add(code);
            }
        }
        return out;
    }

    /** A client-supplied fare-code payload → an ordered, trimmed, blank-free list of codes. */
    private static List<String> normalizeFareCodes(Object raw) {
        List<String> codes = new List<String>();
        if (!(raw instanceof List<Object>)) {
            return codes;
        }
        for (Object o : (List<Object>) raw) {
            String code = (o == null) ? null : String.valueOf(o).trim();
            if (String.isNotBlank(code)) {
                codes.add(code);
            }
        }
        return codes;
    }

    /**
     * Auto-derived display name for a fare line from its selected codes, e.g. "Comfort (W S J)".
     * With no codes selected (or no resolvable base product name) the custom name is cleared (null)
     * so the grid reverts to the product's catalog name. Truncated to the CustomProductName platform
     * max (80 chars) — the base name alone is well under it, so only pathological inputs truncate.
     */
    private static String buildFareDisplayName(QuoteLineItem line, List<String> codes) {
        String baseName = (line.Product2 != null && String.isNotBlank(line.Product2.Name)) ? line.Product2.Name : null;
        if (codes == null || codes.isEmpty() || baseName == null) {
            return null;
        }
        String name = baseName + ' (' + String.join(codes, ' ') + ')';
        return (name.length() > CUSTOM_PRODUCT_NAME_MAX) ? name.substring(0, CUSTOM_PRODUCT_NAME_MAX) : name;
    }

    /** A Term root is a line whose product ProductCode or StockKeepingUnit is DL-TERM. */
    private static Boolean isTermSku(QuoteLineItem qli) {
        if (qli.Product2 == null) {
            return false;
        }
        return TERM_SKU.equals(qli.Product2.ProductCode) || TERM_SKU.equals(qli.Product2.StockKeepingUnit);
    }

    /**
     * Bulk-decide which lines expose at least one editable informational attribute — the exact set the
     * rlmLineAttributePicker would render, so the LWC can hide its per-row Attributes action on lines
     * with nothing to edit. Mirrors RLM_DeltaCatalogController.discoverLineAttributes'
     * eligibility filter (informational = non-hidden AND non-price-impacting AND non-read-only, joined
     * to an ACTIVE AttributeDefinition) but over ALL lines at once: two junction queries keyed by the
     * quote's distinct products/classifications, then a single active-definition query — no SOQL in
     * loops. A line is editable iff any of its product's (or inherited classification's) attribute
     * definitions survives the filter.
     */
    private static Map<Id, Boolean> computeEditableByLine(List<QuoteLineItem> lines) {
        Map<Id, Boolean> result = new Map<Id, Boolean>();
        Set<Id> productIds = new Set<Id>();
        Set<Id> classificationIds = new Set<Id>();
        for (QuoteLineItem qli : lines) {
            result.put(qli.Id, false);
            if (qli.Product2Id != null) {
                productIds.add(qli.Product2Id);
            }
            if (qli.Product2 != null && qli.Product2.BasedOnId != null) {
                classificationIds.add(qli.Product2.BasedOnId);
            }
        }
        if (productIds.isEmpty() && classificationIds.isEmpty()) {
            return result;
        }

        // Per-owner junction eligibility, kept separate so precedence can be resolved per line:
        // productId → (defId → editable?) and classificationId → (defId → editable?). Editable here =
        // informational AND non-read-only (isEditableJunction). Product-specific junction wins over the
        // inherited classification for the SAME defId on the SAME line (matches discoverLineAttributes).
        Map<Id, Map<Id, Boolean>> prodEligible = new Map<Id, Map<Id, Boolean>>();
        Map<Id, Map<Id, Boolean>> clsEligible = new Map<Id, Map<Id, Boolean>>();
        Set<Id> candidateDefIds = new Set<Id>();

        if (!classificationIds.isEmpty()) {
            for (ProductClassificationAttr pca : [
                SELECT ProductClassificationId, AttributeDefinitionId, IsHidden, IsPriceImpacting, IsReadOnly
                FROM ProductClassificationAttr
                WHERE ProductClassificationId IN :classificationIds AND AttributeDefinitionId != null
                WITH USER_MODE
            ]) {
                if (!clsEligible.containsKey(pca.ProductClassificationId)) {
                    clsEligible.put(pca.ProductClassificationId, new Map<Id, Boolean>());
                }
                clsEligible.get(pca.ProductClassificationId).put(pca.AttributeDefinitionId,
                    isEditableJunction(pca.IsHidden, pca.IsPriceImpacting, pca.IsReadOnly));
                candidateDefIds.add(pca.AttributeDefinitionId);
            }
        }
        if (!productIds.isEmpty()) {
            for (ProductAttributeDefinition pad : [
                SELECT Product2Id, AttributeDefinitionId, IsHidden, IsPriceImpacting, IsReadOnly
                FROM ProductAttributeDefinition
                WHERE Product2Id IN :productIds AND AttributeDefinitionId != null
                WITH USER_MODE
            ]) {
                if (!prodEligible.containsKey(pad.Product2Id)) {
                    prodEligible.put(pad.Product2Id, new Map<Id, Boolean>());
                }
                prodEligible.get(pad.Product2Id).put(pad.AttributeDefinitionId,
                    isEditableJunction(pad.IsHidden, pad.IsPriceImpacting, pad.IsReadOnly));
                candidateDefIds.add(pad.AttributeDefinitionId);
            }
        }
        if (candidateDefIds.isEmpty()) {
            return result;
        }

        // Only ACTIVE definitions count (the picker joins IsActive = true).
        Set<Id> activeDefIds = new Set<Id>();
        for (AttributeDefinition ad : [
            SELECT Id FROM AttributeDefinition WHERE Id IN :candidateDefIds AND IsActive = true WITH USER_MODE
        ]) {
            activeDefIds.add(ad.Id);
        }
        if (activeDefIds.isEmpty()) {
            return result;
        }

        // A line is editable iff any of its candidate def ids is active and, with product-over-
        // classification precedence resolved for THIS line, passes the junction filter.
        for (QuoteLineItem qli : lines) {
            Map<Id, Boolean> prodMap = (qli.Product2Id != null) ? prodEligible.get(qli.Product2Id) : null;
            Id basedOnId = (qli.Product2 != null) ? qli.Product2.BasedOnId : null;
            Map<Id, Boolean> clsMap = (basedOnId != null) ? clsEligible.get(basedOnId) : null;

            Set<Id> defIds = new Set<Id>();
            if (prodMap != null) {
                defIds.addAll(prodMap.keySet());
            }
            if (clsMap != null) {
                defIds.addAll(clsMap.keySet());
            }
            for (Id defId : defIds) {
                if (!activeDefIds.contains(defId)) {
                    continue;
                }
                // Product junction wins when it defines this attribute for the line's product.
                Boolean eligible = (prodMap != null && prodMap.containsKey(defId))
                    ? prodMap.get(defId)
                    : (clsMap != null ? clsMap.get(defId) : false);
                if (eligible == true) {
                    result.put(qli.Id, true);
                    break;
                }
            }
        }
        return result;
    }

    private static Boolean isEditableJunction(Boolean isHidden, Boolean isPriceImpacting, Boolean isReadOnly) {
        return isHidden != true && isPriceImpacting != true && isReadOnly != true;
    }

    private static Map<String, Object> parseInput(String inputJson) {
        if (String.isBlank(inputJson)) {
            throw new LineEditorException('Request body is required.');
        }
        try {
            return (Map<String, Object>) JSON.deserializeUntyped(inputJson);
        } catch (Exception e) {
            throw new LineEditorException('Invalid request: malformed JSON.');
        }
    }

    private static Id parseId(String raw, String label) {
        if (String.isBlank(raw)) {
            throw new LineEditorException(label + ' is required.');
        }
        try {
            return Id.valueOf(raw.trim());
        } catch (Exception e) {
            throw new LineEditorException('Invalid ' + label + '.');
        }
    }

    private static String asString(Object o) {
        return (o == null) ? null : String.valueOf(o);
    }

    private static Decimal asDecimal(Object o) {
        if (o == null || String.isBlank(String.valueOf(o))) return null;
        try {
            if (o instanceof Decimal) return (Decimal) o;
            if (o instanceof Integer) return (Decimal) ((Integer) o);
            if (o instanceof Long) return (Decimal) ((Long) o);
            if (o instanceof Double) return Decimal.valueOf((Double) o);
            return Decimal.valueOf(String.valueOf(o));
        } catch (Exception e) {
            throw new LineEditorException('Invalid number: ' + o);
        }
    }

    private static Date asDate(Object o) {
        if (o == null || String.isBlank(String.valueOf(o))) return null;
        String s = String.valueOf(o).trim();
        try {
            // Accept ISO date (yyyy-MM-dd) or full datetime; take the date part.
            if (s.length() >= 10) {
                return Date.valueOf(s.substring(0, 10));
            }
            return Date.valueOf(s);
        } catch (Exception e) {
            throw new LineEditorException('Invalid date: ' + o);
        }
    }

    private static String errorResult(String message) {
        return JSON.serialize(new Map<String, Object>{ 'isSuccess' => false, 'errorMessage' => message });
    }
}
