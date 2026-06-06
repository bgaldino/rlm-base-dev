/**
 * Invocable for "Set Up Quote" flow: create or modify quote, set Large Deal,
 * create top-level + nested groups (max 5 levels), add products per group (DemoInvocableAction product set).
 * Modify + empty hierarchyJson parents + csvImportLineItemsJson: add CSV lines only (no QuoteLineGroup; flat QuoteLineItems).
 */
public with sharing class RLM_SetUpQuoteInvocable {

    private static final Integer MAX_TOP_LEVEL = 20;
    private static final Integer MAX_NESTED_PER_TOP = 10;

    private static final Map<String, String> PRICING_TERM_TO_BILLING_FREQUENCY = new Map<String, String>{
        'Months' => 'Monthly', 'Annual' => 'Annual', 'Quarterly' => 'Quarterly', 'Semi-Annual' => 'Semi-Annual'
    };

    public class Input {
        @InvocableVariable(required=true label='Create new quote (true) or modify existing (false)')
        public Boolean isCreate;
        @InvocableVariable(label='Existing Quote Id (for modify)')
        public String quoteId;
        @InvocableVariable(label='New quote name (for create)')
        public String newQuoteName;
        @InvocableVariable(label='Mark as Large Deal')
        public Boolean largeDeal;
        // Tree structure (new flow): parent names, subgroup names per parent (CSV each), product counts per parent (CSV: parent then subgroups)
        @InvocableVariable(label='Parent group names (use for new parent/subgroup flow)')
        public List<String> parentGroupNames;
        @InvocableVariable(label='Subgroup names per parent (comma-separated per parent; same order as parent group names)')
        public List<String> subgroupNamesPerParent;
        @InvocableVariable(label='Product counts per parent (comma-separated: parent count then each subgroup; same order as parents)')
        public List<String> productCountsPerParent;
        // LWC hierarchy (5-level tree + counts)
        @InvocableVariable(label='Hierarchy JSON (from LWC: { parents: [ { name, path, children: [...] } ] }). Use {"parents":[]} when modifying a quote with csvImportLineItemsJson only (no QuoteLineGroup rows; flat lines).')
        public String hierarchyJson;
        @InvocableVariable(label='Product counts JSON (from LWC: { "0": 2, "0-0": 1, ... })')
        public String productCountsJson;
        @InvocableVariable(label='Ungrouped product count (quote-level lines, no QuoteLineGroup)')
        public Integer ungroupedProductCount;
        @InvocableVariable(label='Product set mode for count-based setup quote paths')
        public String productSetMode;
        /** CSV import: JSON array of { "path": "0-0", "productIdentifier": "QB-NETSECURE-10G", "quantity": 2 }. When set, used instead of productCountsJson (resolve by ProductCode then Name; PBE order OneTime→Evergreen→TermDefined; skip row if not found). */
        @InvocableVariable(label='CSV import line items JSON (array of path, productIdentifier, quantity)')
        public String csvImportLineItemsJson;
        /** When modifying: JSON array of QuoteLineGroup Ids to delete (group + descendants + line items). */
        @InvocableVariable(label='Group IDs to delete (modify only; JSON array of QuoteLineGroup Ids)')
        public String groupsToDeleteJson;
        /** When modifying: JSON object { "groupId": "newName", ... } to rename groups. */
        @InvocableVariable(label='Group renames (modify only; JSON object groupId -> new name)')
        public String groupRenamesJson;
        /** When modifying: JSON array [ { "parentGroupId", "name", "tempId" }, ... ] for new subgroups under existing. */
        @InvocableVariable(label='New subgroups under existing (modify only; JSON array)')
        public String newSubgroupsJson;
        /** When modifying: JSON object { "groupId": count, "tempId": count, ... } for existing groups and new subgroups. */
        @InvocableVariable(label='Product counts for existing groups (modify only; JSON object)')
        public String existingGroupCountsJson;
        /** Repeat-buy assignment payload (create previous-quotes mode). */
        @InvocableVariable(label='Repeat-buy line assignments JSON')
        public String repeatBuyAssignmentsJson;
        /** Repeat-buy selected account id; used to set target quote account linkage. */
        @InvocableVariable(label='Repeat-buy account Id')
        public String repeatBuyAccountId;
        /** Account action context; used to link newly created quotes to the source Account. */
        @InvocableVariable(label='Quote Account Id')
        public String quoteAccountId;
        // Legacy flat structure (old flow)
        @InvocableVariable(label='Number of top-level groups (legacy)')
        public Integer numTopLevel;
        @InvocableVariable(label='Number of nested groups under each top-level (legacy)')
        public Integer numNestedPerTop;
        @InvocableVariable(label='Product counts per group comma-separated (legacy)')
        public String productCountsCSV;
        /** When true, PST skips configuration so groups and line items persist even if org configuration (e.g. CPQ) would fail. Use for CSV import when you see "Configuration failed" and no QLIs. */
        @InvocableVariable(label='Skip configuration (PST)')
        public Boolean skipConfiguration;
        /**
         * DeveloperName of a TransactionProcessingType record (e.g. RLM_SUQ_PriceAndTax,
         * RLM_SUQ_SkipPriceAndTax). Selects the pricing/tax/rate permutation for the PST
         * call. Blank or unknown keeps the default: run pricing (Force) and run tax. The
         * name is also stamped on the Quote's TransactionType field for downstream re-pricing.
         */
        @InvocableVariable(label='Transaction Processing Type (DeveloperName)')
        public String transactionType;
    }

    public class Output {
        @InvocableVariable(label='Quote Id')
        public String quoteId;
        @InvocableVariable(label='Success')
        public Boolean success;
        @InvocableVariable(label='Error message')
        public String errorMessage;
        /** When CSV import was used and 0 line items were added (e.g. products not found). */
        @InvocableVariable(label='Warning message')
        public String warningMessage;
    }

    @InvocableMethod(label='Set Up Quote' description='Create or modify quote, set Large Deal, create groups and nested groups, add products.')
    public static List<Output> execute(List<Input> inputs) {
        List<Output> results = new List<Output>();
        if (inputs == null || inputs.isEmpty()) {
            results.add(fail(null, 'No input'));
            return results;
        }
        Input in0 = inputs[0];
        Boolean useHier = useHierarchyJsonInput(in0);
        Boolean useTree = useTreeInput(in0);
        try {
            List<Integer> csvLinesAddedOut = new List<Integer>();
            String qId;
            if (useHier) qId = runFromHierarchyJson(in0, csvLinesAddedOut);
            else if (useTree) qId = runTree(in0);
            else qId = run(in0);
            Output o = new Output();
            o.quoteId = qId;
            o.success = true;
            o.errorMessage = null;
            if (!csvLinesAddedOut.isEmpty() && csvLinesAddedOut[0] != null && csvLinesAddedOut[0] == 0) {
                o.warningMessage = 'No quote line items were added from the CSV. Check that each product (Product or Bundle Product column) exists in your org with that Product Code or Name and has an active Pricebook Entry on the Standard Price Book.';
            }
            results.add(o);
        } catch (Exception e) {
            String msg = e.getMessage();
            if (String.isBlank(msg)) msg = e.getTypeName();
            results.add(fail(null, 'Quote creation failed: ' + msg));
        }
        return results;
    }

    /**
     * Aura-enabled entry point for LWC (e.g. Set Up Quote wizard modal).
     * Calls execute() directly so PST runs in Apex context and persists quote/groups/lines.
     * (When invoked via Flow, PST defaults persist to SKIP and the quote is empty.)
     * Pass a JSON object with same keys as Input; returns JSON with quoteId, success, errorMessage.
     */
    @AuraEnabled(cacheable=false)
    public static String runSetUpQuoteFromLWC(String inputJson) {
        if (String.isBlank(inputJson)) {
            return JSON.serialize(new Map<String, Object>{
                'quoteId' => null, 'success' => false, 'errorMessage' => 'No input'
            });
        }
        // Call invocable directly so PST runs in Apex context; when run via Flow, PST defaults
        // persist to SKIP and the quote is empty. Same code path as run-set-up-quote-invocable.apex.
        // Parse inside the try so malformed JSON returns a structured error, not an unhandled exception.
        try {
            Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(inputJson);
            Input in0 = inputFromMap(m);
            List<Output> outs = execute(new List<Input>{ in0 });
            if (outs.isEmpty()) {
                return JSON.serialize(new Map<String, Object>{
                    'quoteId' => null, 'success' => false, 'errorMessage' => 'No output from Set Up Quote'
                });
            }
            Output o = outs[0];
            return JSON.serialize(new Map<String, Object>{
                'quoteId' => o.quoteId, 'success' => o.success != null && o.success, 'errorMessage' => o.errorMessage, 'warningMessage' => o.warningMessage
            });
        } catch (Exception e) {
            String msg = e.getMessage();
            if (String.isBlank(msg)) msg = e.getTypeName();
            return JSON.serialize(new Map<String, Object>{
                'quoteId' => null, 'success' => false, 'errorMessage' => 'Quote creation failed: ' + msg
            });
        }
    }

    @AuraEnabled(cacheable=false)
    public static String getSetUpQuoteUiConfig() {
        Boolean showProductSetSelector = false;
        try {
            RLM_Set_Up_Quote_Settings__c settings = RLM_Set_Up_Quote_Settings__c.getOrgDefaults();
            showProductSetSelector = settings != null && settings.RLM_Show_Product_Set_Selector__c == true;
        } catch (Exception e) {
            showProductSetSelector = false;
        }
        // Selectable pricing/tax permutations for the Set Up Quote wizard. Only the builder's
        // canonical TransactionProcessingType records (the ones shipped in post_large_stx) are
        // offered — an explicit allowlist keeps org-only/test artifacts out of the dropdown.
        List<Map<String, Object>> transactionTypes = new List<Map<String, Object>>();
        try {
            for (TransactionProcessingType t : [
                SELECT DeveloperName, MasterLabel FROM TransactionProcessingType ORDER BY MasterLabel
            ]) {
                if (t.DeveloperName != null && SELECTABLE_TRANSACTION_TYPES.contains(t.DeveloperName)) {
                    transactionTypes.add(new Map<String, Object>{
                        'value' => t.DeveloperName,
                        'label' => String.isNotBlank(t.MasterLabel) ? t.MasterLabel : t.DeveloperName
                    });
                }
            }
        } catch (Exception e) {
            // Leave the list empty; the wizard hides the selector when no types are available.
        }
        return JSON.serialize(new Map<String, Object>{
            'showProductSetSelector' => showProductSetSelector,
            'transactionTypes' => transactionTypes,
            'defaultTransactionType' => DEFAULT_TRANSACTION_TYPE
        });
    }

    /** Default permutation the wizard preselects: run pricing and tax (full path). */
    @TestVisible
    private static final String DEFAULT_TRANSACTION_TYPE = 'RLM_SUQ_PriceAndTax';

    /** Canonical permutations shipped in post_large_stx — the only types offered in the wizard. */
    @TestVisible
    private static final Set<String> SELECTABLE_TRANSACTION_TYPES = new Set<String>{
        'RLM_SUQ_PriceAndTax',
        'RLM_SUQ_PriceSkipTax',
        'RLM_SUQ_SkipPriceRunTax',
        'RLM_SUQ_SkipPriceAndTax',
        'RLM_SUQ_PriceTaxFetchRates',
        'RLM_SUQ_PriceTaxStdConfig'
    };

    /**
     * Lightweight polling endpoint for the LWC Large Deal two-step path.
     * Large Deal PST hydration can report success before groups/lines are query-visible.
     */
    @AuraEnabled(cacheable=false)
    public static String getSetUpQuoteStatus(String quoteId) {
        if (String.isBlank(quoteId)) {
            return JSON.serialize(new Map<String, Object>{
                'success' => false,
                'errorMessage' => 'Quote Id is required'
            });
        }
        try {
            Id qId = Id.valueOf(quoteId);
            Quote q = [
                SELECT Id, Name, IsLargeDeal, LineItemCount, CalculationStatus
                FROM Quote
                WHERE Id = :qId
                LIMIT 1
            ];
            Integer groupCount = [SELECT COUNT() FROM QuoteLineGroup WHERE QuoteId = :qId];
            Integer qliCount = [SELECT COUNT() FROM QuoteLineItem WHERE QuoteId = :qId];
            Integer errorCount = [SELECT COUNT() FROM RevenueTransactionErrorLog WHERE PrimaryRecordId = :qId];
            // Scope pending async strictly to this quote. PST trackers carry the quote
            // in ReferenceEntityId (the failedAsyncCount query below relies on the same),
            // so a broader CreatedById/JobType clause only risks counting unrelated PST
            // jobs from the user's other transactions and hanging the poller.
            Integer pendingAsyncCount = [
                SELECT COUNT()
                FROM AsyncOperationTracker
                WHERE ReferenceEntityId = :qId
                AND Status NOT IN ('Completed', 'Failed', 'Failure', 'Canceled')
            ];
            Integer failedAsyncCount = [
                SELECT COUNT()
                FROM AsyncOperationTracker
                WHERE ReferenceEntityId = :qId
                AND Status IN ('Failed', 'Failure', 'Canceled')
            ];
            return JSON.serialize(new Map<String, Object>{
                'success' => true,
                'quoteId' => String.valueOf(q.Id),
                'name' => q.Name,
                'isLargeDeal' => q.IsLargeDeal,
                'lineItemCount' => q.LineItemCount,
                'calculationStatus' => q.CalculationStatus,
                'groupCount' => groupCount,
                'qliCount' => qliCount,
                'revenueErrorCount' => errorCount,
                'pendingAsyncCount' => pendingAsyncCount,
                'failedAsyncCount' => failedAsyncCount
            });
        } catch (Exception e) {
            String msg = e.getMessage();
            if (String.isBlank(msg)) msg = e.getTypeName();
            return JSON.serialize(new Map<String, Object>{
                'success' => false,
                'quoteId' => quoteId,
                'errorMessage' => msg
            });
        }
    }

    /**
     * Returns a list of quotes for the Modify flow: Id, Name, QuoteNumber, IsLargeDeal.
     * Used by Set Up Quote wizard to show a dropdown and to hide the Large Deal step when the selected quote already has Large Deal set.
     */
    @AuraEnabled(cacheable=false)
    public static List<Map<String, String>> getQuotesForModify() {
        List<Map<String, String>> options = new List<Map<String, String>>();
        for (Quote q : [SELECT Id, Name, QuoteNumber, IsLargeDeal FROM Quote ORDER BY LastModifiedDate DESC LIMIT 100]) {
            Map<String, String> opt = new Map<String, String>();
            opt.put('value', q.Id);
            opt.put('label', (String.isNotBlank(q.Name) ? q.Name : q.QuoteNumber) + ' (' + q.QuoteNumber + ')');
            opt.put('isLargeDeal', q.IsLargeDeal == true ? 'true' : 'false');
            options.add(opt);
        }
        return options;
    }

    @AuraEnabled(cacheable=false)
    public static String detectQuoteProductSetMode(String quoteId) {
        if (String.isBlank(quoteId)) {
            return RLM_SetUpQuoteProductSets.PRODUCT_SET_QUANTUMBIT;
        }
        Set<String> siemensIdentifiers = RLM_SetUpQuoteProductSets.siemensProductIdentifierSet();
        Integer totalLines = 0;
        Integer siemensLines = 0;
        try {
            Id qId = Id.valueOf(quoteId);
            // Aggregate counts avoid materializing every QLI (no 5000-row cap),
            // so detection stays accurate and cheap on large quotes.
            totalLines = [SELECT COUNT() FROM QuoteLineItem WHERE QuoteId = :qId];
            siemensLines = [
                SELECT COUNT()
                FROM QuoteLineItem
                WHERE QuoteId = :qId
                  AND Product2.ProductCode IN :siemensIdentifiers
            ];
        } catch (Exception e) {
            return RLM_SetUpQuoteProductSets.PRODUCT_SET_QUANTUMBIT;
        }
        if (totalLines > 0 && totalLines == siemensLines) {
            return RLM_SetUpQuoteProductSets.PRODUCT_SET_SIEMENS;
        }
        return RLM_SetUpQuoteProductSets.PRODUCT_SET_QUANTUMBIT;
    }

    /**
     * Returns existing quote line group hierarchy for the given quote (modify flow).
     * Structure: { parents: [ { id, name, lineItemCount, children: [ ... ] } ] } with root groups first, children by SortOrder.
     */
    @AuraEnabled(cacheable=false)
    public static String getQuoteHierarchy(String quoteId) {
        final String emptyResult = JSON.serialize(new Map<String, Object>{ 'parents' => new List<Object>() });
        if (String.isBlank(quoteId)) return emptyResult;
        Id qId;
        try {
            qId = Id.valueOf(quoteId);
        } catch (Exception e) {
            return emptyResult;
        }
        List<QuoteLineGroup> groups = [SELECT Id, Name, ParentQuoteLineGroupId, SortOrder FROM QuoteLineGroup WHERE QuoteId = :qId ORDER BY ParentQuoteLineGroupId NULLS FIRST, SortOrder NULLS LAST, Name];
        // Count lines per group with a server-side aggregate. This avoids loading
        // every QuoteLineItem into heap and the 50k-query-row limit, which matters
        // for the large-sales-transaction quotes this feature targets.
        Map<Id, Integer> lineCountByGroup = new Map<Id, Integer>();
        for (AggregateResult ar : [
            SELECT QuoteLineGroupId groupId, COUNT(Id) lineCount
            FROM QuoteLineItem
            WHERE QuoteId = :qId
              AND QuoteLineGroupId != null
            GROUP BY QuoteLineGroupId
        ]) {
            lineCountByGroup.put((Id) ar.get('groupId'), (Integer) ar.get('lineCount'));
        }
        Map<Id, List<QuoteLineGroup>> childrenByParent = new Map<Id, List<QuoteLineGroup>>();
        List<QuoteLineGroup> roots = new List<QuoteLineGroup>();
        for (QuoteLineGroup g : groups) {
            if (g.ParentQuoteLineGroupId == null) roots.add(g);
            else {
                if (!childrenByParent.containsKey(g.ParentQuoteLineGroupId)) childrenByParent.put(g.ParentQuoteLineGroupId, new List<QuoteLineGroup>());
                childrenByParent.get(g.ParentQuoteLineGroupId).add(g);
            }
        }
        List<Object> parentNodes = new List<Object>();
        for (QuoteLineGroup g : roots) parentNodes.add(buildGroupNode(g, childrenByParent, lineCountByGroup));
        return JSON.serialize(new Map<String, Object>{ 'parents' => parentNodes });
    }

    private static Map<String, Object> buildGroupNode(QuoteLineGroup g, Map<Id, List<QuoteLineGroup>> childrenByParent, Map<Id, Integer> lineCountByGroup) {
        Map<String, Object> node = new Map<String, Object>();
        node.put('id', g.Id);
        node.put('name', String.isNotBlank(g.Name) ? g.Name : ('Group ' + g.Id));
        node.put('lineItemCount', lineCountByGroup.containsKey(g.Id) ? lineCountByGroup.get(g.Id) : 0);
        List<Object> childList = new List<Object>();
        if (childrenByParent.containsKey(g.Id)) {
            for (QuoteLineGroup c : childrenByParent.get(g.Id)) childList.add(buildGroupNode(c, childrenByParent, lineCountByGroup));
        }
        node.put('children', childList);
        return node;
    }

    /**
     * Deletes the given quote line groups (and all their descendants and line items),
     * restricted to groups that belong to the specified quote.
     * The quoteId ownership check prevents accidental cross-quote deletes caused by
     * stale UI state or crafted payloads.
     */
    private static void deleteQuoteLineGroups(String quoteId, String groupsToDeleteJson) {
        if (String.isBlank(quoteId) || String.isBlank(groupsToDeleteJson)) return;
        List<Object> arr;
        try {
            arr = (List<Object>) JSON.deserializeUntyped(groupsToDeleteJson);
        } catch (Exception e) {
            return; // malformed JSON — nothing to delete
        }
        Set<Id> candidateIds = new Set<Id>();
        for (Object o : arr) {
            if (o == null || String.isBlank(String.valueOf(o))) continue;
            try {
                candidateIds.add(Id.valueOf(String.valueOf(o)));
            } catch (Exception e) {
                continue; // skip individual invalid Id — don't abort the whole operation
            }
        }
        if (candidateIds.isEmpty()) return;
        // Ownership guard: only expand groups that actually belong to this quote
        Id qId = Id.valueOf(quoteId);
        Set<Id> rootIds = new Set<Id>();
        for (QuoteLineGroup g : [SELECT Id FROM QuoteLineGroup WHERE Id IN :candidateIds AND QuoteId = :qId]) {
            rootIds.add(g.Id);
        }
        if (rootIds.isEmpty()) return;
        Set<Id> allGroupIds = new Set<Id>(rootIds);
        // Frontier-based BFS: only query newly discovered children each iteration
        Set<Id> frontier = new Set<Id>(rootIds);
        while (!frontier.isEmpty()) {
            Set<Id> nextFrontier = new Set<Id>();
            for (QuoteLineGroup g : [SELECT Id, ParentQuoteLineGroupId FROM QuoteLineGroup WHERE ParentQuoteLineGroupId IN :frontier AND QuoteId = :qId]) {
                if (!allGroupIds.contains(g.Id)) {
                    allGroupIds.add(g.Id);
                    nextFrontier.add(g.Id);
                }
            }
            frontier = nextFrontier;
        }
        List<QuoteLineItem> toDeleteItems = [SELECT Id FROM QuoteLineItem WHERE QuoteLineGroupId IN :allGroupIds AND QuoteId = :qId];
        if (!toDeleteItems.isEmpty()) delete toDeleteItems;
        List<QuoteLineGroup> toDeleteGroups = [SELECT Id, ParentQuoteLineGroupId FROM QuoteLineGroup WHERE Id IN :allGroupIds];
        Set<Id> remaining = new Set<Id>(allGroupIds);
        while (!remaining.isEmpty()) {
            Set<Id> parentIdsInRemaining = new Set<Id>();
            for (QuoteLineGroup g : toDeleteGroups) {
                if (remaining.contains(g.Id) && g.ParentQuoteLineGroupId != null && remaining.contains(g.ParentQuoteLineGroupId)) parentIdsInRemaining.add(g.ParentQuoteLineGroupId);
            }
            List<Id> leafIds = new List<Id>();
            for (Id gid : remaining) if (!parentIdsInRemaining.contains(gid)) leafIds.add(gid);
            if (leafIds.isEmpty()) break;
            delete [SELECT Id FROM QuoteLineGroup WHERE Id IN :leafIds];
            for (Id gid : leafIds) remaining.remove(gid);
        }
    }

    private static void applyGroupRenames(String quoteId, String groupRenamesJson) {
        if (String.isBlank(quoteId) || String.isBlank(groupRenamesJson)) return;
        Id qId = Id.valueOf(quoteId);
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(groupRenamesJson);
        // Build a map of requested Id -> new name, filtering out blank values
        Map<Id, String> requestedNamesByGroupId = new Map<Id, String>();
        for (String k : m.keySet()) {
            Object v = m.get(k);
            if (v == null || String.isBlank(String.valueOf(v))) continue;
            String newName = String.valueOf(v).trim();
            if (String.isBlank(newName)) continue;
            try { requestedNamesByGroupId.put(Id.valueOf(k), newName); } catch (Exception e) { continue; }
        }
        if (requestedNamesByGroupId.isEmpty()) return;
        // Ownership guard: only rename groups that actually belong to this quote
        List<QuoteLineGroup> toUpdate = new List<QuoteLineGroup>();
        for (QuoteLineGroup g : [
            SELECT Id
            FROM QuoteLineGroup
            WHERE Id IN :requestedNamesByGroupId.keySet()
              AND QuoteId = :qId
        ]) {
            toUpdate.add(new QuoteLineGroup(Id = g.Id, Name = requestedNamesByGroupId.get(g.Id)));
        }
        if (!toUpdate.isEmpty()) update toUpdate;
    }

    /** Returns map tempId -> new QuoteLineGroup Id. Processes in dependency order so parents (existing Id or tempId) are created before children. */
    private static Map<String, Id> createNewSubgroupsUnderExisting(String quoteId, String newSubgroupsJson) {
        if (String.isBlank(quoteId) || String.isBlank(newSubgroupsJson)) return new Map<String, Id>();
        List<Object> raw = (List<Object>) JSON.deserializeUntyped(newSubgroupsJson);
        if (raw.isEmpty()) return new Map<String, Id>();
        Id qId = Id.valueOf(quoteId);
        // Pre-compute the set of group Ids that belong to this quote — used to validate
        // real (non-tempId) parentGroupId values and prevent cross-quote subgroup creation.
        Set<Id> validGroupIdsForQuote = new Set<Id>();
        Map<Id, Integer> nextSortOrderByParent = new Map<Id, Integer>();
        for (QuoteLineGroup g : [SELECT Id, ParentQuoteLineGroupId, SortOrder FROM QuoteLineGroup WHERE QuoteId = :qId]) {
            validGroupIdsForQuote.add(g.Id);
            if (g.ParentQuoteLineGroupId != null) {
                Id p = g.ParentQuoteLineGroupId;
                Integer so = g.SortOrder != null ? Integer.valueOf(String.valueOf(g.SortOrder)) : 0;
                nextSortOrderByParent.put(p, nextSortOrderByParent.containsKey(p) ? Math.max(nextSortOrderByParent.get(p), so) : so);
            }
        }
        List<Map<String, Object>> items = new List<Map<String, Object>>();
        for (Object o : raw) {
            Map<String, Object> item = (Map<String, Object>) o;
            String parentIdStr = item.containsKey('parentGroupId') ? String.valueOf(item.get('parentGroupId')) : null;
            String nameStr = item.containsKey('name') ? String.valueOf(item.get('name')).trim() : null;
            String tempId = item.containsKey('tempId') ? String.valueOf(item.get('tempId')) : null;
            if (String.isBlank(parentIdStr) || String.isBlank(nameStr)) continue;
            items.add(item);
        }
        Map<String, Id> tempIdToNewId = new Map<String, Id>();
        Set<Integer> created = new Set<Integer>();
        while (created.size() < items.size()) {
            Integer createdThisPass = 0;
            for (Integer i = 0; i < items.size(); i++) {
                if (created.contains(i)) continue;
                Map<String, Object> item = items[i];
                String parentIdStr = String.valueOf(item.get('parentGroupId'));
                String nameStr = String.valueOf(item.get('name')).trim();
                String tempId = item.containsKey('tempId') ? String.valueOf(item.get('tempId')) : null;
                Id parentId = null;
                if (parentIdStr.length() == 15 || parentIdStr.length() == 18) {
                    try { parentId = Id.valueOf(parentIdStr); } catch (Exception e) { continue; }
                    // Ownership guard: reject real parentIds not belonging to this quote
                    if (!validGroupIdsForQuote.contains(parentId)) continue;
                } else if (tempIdToNewId.containsKey(parentIdStr)) {
                    parentId = tempIdToNewId.get(parentIdStr);
                } else continue;
                Integer nextSo = (nextSortOrderByParent.containsKey(parentId) ? nextSortOrderByParent.get(parentId) : 0) + 1;
                nextSortOrderByParent.put(parentId, nextSo);
                QuoteLineGroup g = new QuoteLineGroup(QuoteId = qId, ParentQuoteLineGroupId = parentId, Name = nameStr, SortOrder = nextSo);
                insert g;
                validGroupIdsForQuote.add(g.Id); // allow this new group as a parent in subsequent passes
                if (String.isNotBlank(tempId)) tempIdToNewId.put(tempId, g.Id);
                nextSortOrderByParent.put(g.Id, 0);
                created.add(i);
                createdThisPass++;
            }
            if (createdThisPass == 0) break;
        }
        return tempIdToNewId;
    }

    private static Map<Id, Integer> parseExistingGroupCounts(String existingGroupCountsJson, Map<String, Id> tempIdToNewGroupId) {
        Map<String, Object> m;
        try {
            m = (Map<String, Object>) JSON.deserializeUntyped(existingGroupCountsJson);
        } catch (Exception e) {
            // Mirror the productCountsJson guard: fail loudly with an actionable message
            // instead of an opaque deserialization error.
            throw new RLM_SetUpQuoteException('Invalid existing group counts JSON: ' + e.getMessage());
        }
        if (m == null) {
            throw new RLM_SetUpQuoteException('Invalid existing group counts JSON: payload was null.');
        }
        Map<Id, Integer> groupIdToCount = new Map<Id, Integer>();
        for (String k : m.keySet()) {
            Object v = m.get(k);
            Integer count = RLM_SetUpQuoteProductSets.parseNonNegativeInteger(v);
            Id gid = null;
            if (tempIdToNewGroupId != null && tempIdToNewGroupId.containsKey(k)) gid = tempIdToNewGroupId.get(k);
            else try { gid = Id.valueOf(k); } catch (Exception e) { continue; }
            groupIdToCount.put(gid, count);
        }
        return groupIdToCount;
    }

    /** Ownership guard: returns only the entries whose group Id belongs to the given quote. */
    private static Map<Id, Integer> filterGroupCountsToQuote(String quoteId, Map<Id, Integer> groupIdToCount) {
        if (groupIdToCount == null || groupIdToCount.isEmpty() || String.isBlank(quoteId)) return new Map<Id, Integer>();
        Id qId;
        try {
            qId = Id.valueOf(quoteId);
        } catch (Exception e) {
            return new Map<Id, Integer>();
        }
        Set<Id> requestedGroupIds = new Set<Id>(groupIdToCount.keySet());
        Map<Id, Integer> filtered = new Map<Id, Integer>();
        for (QuoteLineGroup qlg : [SELECT Id FROM QuoteLineGroup WHERE QuoteId = :qId AND Id IN :requestedGroupIds]) {
            if (groupIdToCount.containsKey(qlg.Id)) filtered.put(qlg.Id, groupIdToCount.get(qlg.Id));
        }
        return filtered;
    }

    private static void appendExistingGroupCounts(String quoteId, String existingGroupCountsJson, Map<String, Id> tempIdToNewGroupId) {
        if (String.isBlank(quoteId) || String.isBlank(existingGroupCountsJson)) return;
        Map<Id, Integer> groupIdToCount = parseExistingGroupCounts(existingGroupCountsJson, tempIdToNewGroupId);
        if (groupIdToCount.isEmpty()) return;
        Id pricebook2Id = getStandardPricebookId();
        try {
            Id qLookup = Id.valueOf(quoteId);
            for (Quote rq : [SELECT Pricebook2Id FROM Quote WHERE Id = :qLookup WITH USER_MODE LIMIT 1]) {
                if (rq.Pricebook2Id != null) {
                    pricebook2Id = rq.Pricebook2Id;
                }
            }
        } catch (Exception e) { /* keep standard */ }
        List<PricebookEntry> pbes = loadDemoRotationPricebookEntries(pricebook2Id);
        if (pbes.isEmpty()) return;
        Id qId = Id.valueOf(quoteId);
        // Ownership guard: discard any group Ids that don't belong to this quote
        Set<Id> requestedGroupIds = new Set<Id>(groupIdToCount.keySet());
        Set<Id> validGroupIds = new Set<Id>();
        for (QuoteLineGroup qlg : [SELECT Id FROM QuoteLineGroup WHERE QuoteId = :qId AND Id IN :requestedGroupIds WITH USER_MODE]) {
            validGroupIds.add(qlg.Id);
        }
        for (Id gid : new List<Id>(groupIdToCount.keySet())) {
            if (!validGroupIds.contains(gid)) groupIdToCount.remove(gid);
        }
        if (groupIdToCount.isEmpty()) return;
        List<Id> groupIds = new List<Id>(groupIdToCount.keySet());
        // Accumulate items across every group and insert once (no DML in a loop).
        List<QuoteLineItem> allNewItems = new List<QuoteLineItem>();
        for (Id gid : groupIds) {
            Integer count = groupIdToCount.get(gid);
            if (count <= 0) continue;
            for (Integer i = 0; i < count; i++) {
                PricebookEntry pbe = pbes.get(Math.mod(i, pbes.size()));
                QuoteLineItem li = new QuoteLineItem(QuoteId = qId, QuoteLineGroupId = gid, Product2Id = pbe.Product2Id, PricebookEntryId = pbe.Id, Quantity = 1, UnitPrice = pbe.UnitPrice != null ? pbe.UnitPrice : 0);
                if (pbe.ProductSellingModel != null) {
                    String st = String.valueOf(pbe.ProductSellingModel.SellingModelType);
                    String ptu = String.valueOf(pbe.ProductSellingModel.PricingTermUnit);
                    String bf = PRICING_TERM_TO_BILLING_FREQUENCY.get(ptu);
                    // Relative dates (today / +1yr), consistent with subscriptionStartDateIso().
                    if ('TermDefined' == st && String.isNotBlank(bf)) {
                        li.StartDate = Date.today();
                        li.EndDate = Date.today().addYears(1);
                        li.PeriodBoundary = 'Anniversary';
                        li.BillingFrequency = bf;
                    } else if ('Evergreen' == st && String.isNotBlank(bf)) {
                        li.StartDate = Date.today();
                        li.PeriodBoundary = 'Anniversary';
                        li.BillingFrequency = bf;
                    }
                }
                allNewItems.add(li);
            }
        }
        if (!allNewItems.isEmpty()) insert as user allNewItems;
    }

    private static Map<String, Object> buildFlowInputMap(Input in0) {
        Map<String, Object> inputMap = new Map<String, Object>();
        inputMap.put('var_IsCreate', in0.isCreate == true);
        inputMap.put('var_QuoteId', String.isBlank(in0.quoteId) ? null : in0.quoteId);
        inputMap.put('var_NewQuoteName', String.isBlank(in0.newQuoteName) ? null : in0.newQuoteName);
        inputMap.put('var_LargeDeal', in0.largeDeal == true);
        inputMap.put('var_HierarchyJson', String.isBlank(in0.hierarchyJson) ? null : in0.hierarchyJson);
        inputMap.put('var_ProductCountsJson', String.isBlank(in0.productCountsJson) ? null : in0.productCountsJson);
        inputMap.put('var_UngroupedProductCount', in0.ungroupedProductCount);
        inputMap.put('var_ProductSetMode', RLM_SetUpQuoteProductSets.normalizeProductSetMode(in0.productSetMode));
        inputMap.put('var_CsvImportLineItemsJson', String.isBlank(in0.csvImportLineItemsJson) ? null : in0.csvImportLineItemsJson);
        inputMap.put('var_GroupsToDeleteJson', String.isBlank(in0.groupsToDeleteJson) ? null : in0.groupsToDeleteJson);
        inputMap.put('var_GroupRenamesJson', String.isBlank(in0.groupRenamesJson) ? null : in0.groupRenamesJson);
        inputMap.put('var_NewSubgroupsJson', String.isBlank(in0.newSubgroupsJson) ? null : in0.newSubgroupsJson);
        inputMap.put('var_ExistingGroupCountsJson', String.isBlank(in0.existingGroupCountsJson) ? null : in0.existingGroupCountsJson);
        inputMap.put('var_RepeatBuyAssignmentsJson', String.isBlank(in0.repeatBuyAssignmentsJson) ? null : in0.repeatBuyAssignmentsJson);
        inputMap.put('var_RepeatBuyAccountId', String.isBlank(in0.repeatBuyAccountId) ? null : in0.repeatBuyAccountId);
        inputMap.put('var_QuoteAccountId', String.isBlank(in0.quoteAccountId) ? null : in0.quoteAccountId);
        inputMap.put('var_ParentNames', in0.parentGroupNames != null ? in0.parentGroupNames : new List<String>());
        inputMap.put('var_SubgroupCSVPerParent', in0.subgroupNamesPerParent != null ? in0.subgroupNamesPerParent : new List<String>());
        inputMap.put('var_ProductCountsCSVPerParent', in0.productCountsPerParent != null ? in0.productCountsPerParent : new List<String>());
        inputMap.put('var_SkipConfiguration', in0.skipConfiguration == true);
        return inputMap;
    }

    private static Input inputFromMap(Map<String, Object> m) {
        Input in0 = new Input();
        in0.isCreate = m.get('isCreate') == true;
        in0.quoteId = (String) m.get('quoteId');
        in0.newQuoteName = (String) m.get('newQuoteName');
        in0.largeDeal = m.get('largeDeal') == true;
        in0.hierarchyJson = (String) m.get('hierarchyJson');
        in0.productCountsJson = (String) m.get('productCountsJson');
        in0.ungroupedProductCount = RLM_SetUpQuoteProductSets.parseNonNegativeInteger(m.get('ungroupedProductCount'));
        in0.productSetMode = (String) m.get('productSetMode');
        in0.csvImportLineItemsJson = (String) m.get('csvImportLineItemsJson');
        in0.groupsToDeleteJson = (String) m.get('groupsToDeleteJson');
        in0.groupRenamesJson = (String) m.get('groupRenamesJson');
        in0.newSubgroupsJson = (String) m.get('newSubgroupsJson');
        in0.existingGroupCountsJson = (String) m.get('existingGroupCountsJson');
        in0.repeatBuyAssignmentsJson = (String) m.get('repeatBuyAssignmentsJson');
        in0.repeatBuyAccountId = (String) m.get('repeatBuyAccountId');
        in0.quoteAccountId = (String) m.get('quoteAccountId');
        in0.parentGroupNames = listOfStrings(m.get('parentGroupNames'));
        in0.subgroupNamesPerParent = listOfStrings(m.get('subgroupNamesPerParent'));
        in0.productCountsPerParent = listOfStrings(m.get('productCountsPerParent'));
        Object nt = m.get('numTopLevel');
        in0.numTopLevel = nt != null ? Integer.valueOf(nt) : null;
        Object nn = m.get('numNestedPerTop');
        in0.numNestedPerTop = nn != null ? Integer.valueOf(nn) : null;
        in0.productCountsCSV = (String) m.get('productCountsCSV');
        in0.skipConfiguration = m.get('skipConfiguration') == true;
        in0.transactionType = (String) m.get('transactionType');
        return in0;
    }

    private static List<String> listOfStrings(Object o) {
        if (o == null) return null;
        if (o instanceof List<Object>) {
            List<String> out = new List<String>();
            for (Object item : (List<Object>) o) {
                out.add(item != null ? String.valueOf(item) : '');
            }
            return out;
        }
        return null;
    }

    private static Output fail(String qId, String msg) {
        Output o = new Output();
        o.quoteId = qId;
        o.success = false;
        o.errorMessage = msg;
        return o;
    }

    private static Boolean useHierarchyJsonInput(Input in0) {
        return String.isNotBlank(in0.hierarchyJson);
    }

    private static Boolean useTreeInput(Input in0) {
        if (in0.parentGroupNames == null || in0.parentGroupNames.isEmpty()) return false;
        return true;
    }

    private static Id getStandardPricebookId() {
        try {
            return RLM_ProductCatalogPbeService.resolveStandardPricebook2Id();
        } catch (RLM_ProductCatalogPbeService.ProductCatalogPbeException e) {
            throw new RLM_SetUpQuoteException(e.getMessage());
        }
    }

    /** Demo product rotation (same order as DemoInvocableAction singles), resolved for the given price book. */
    private static List<PricebookEntry> loadDemoRotationPricebookEntries(Id pricebook2Id) {
        List<String> order = RLM_DemoProductCodes.orderedDemoProductIdentifiers();
        Map<String, PricebookEntry> m = RLM_ProductCatalogPbeService.resolveProductsToPBEMap(order, pricebook2Id);
        List<PricebookEntry> out = new List<PricebookEntry>();
        for (String k : order) {
            if (m.containsKey(k)) {
                out.add(m.get(k));
            }
        }
        return out;
    }

    private static Map<String, PricebookEntry> loadProductSetPricebookEntryMap(String productSetMode, Id pricebook2Id) {
        List<String> identifiers = RLM_SetUpQuoteProductSets.identifiersForResolution(productSetMode);
        Map<String, PricebookEntry> pbeMap = RLM_ProductCatalogPbeService.resolveProductsToPBEMap(identifiers, pricebook2Id);
        List<String> missing = new List<String>();
        for (String identifier : identifiers) {
            if (!pbeMap.containsKey(identifier)) {
                missing.add(identifier);
            }
        }
        if (!missing.isEmpty()) {
            throw new RLM_SetUpQuoteException('Missing active price book entries for product set ' + RLM_SetUpQuoteProductSets.normalizeProductSetMode(productSetMode) + ': ' + String.join(missing, ', '));
        }
        return pbeMap;
    }

    @TestVisible
    private static Map<String, Object> buildCreateQuoteHeaderFields(Input in0, Id pricebook2Id) {
        Map<String, Object> out = new Map<String, Object>{
            'Name' => in0.newQuoteName,
            'Pricebook2Id' => pricebook2Id
        };
        String accountId = String.isNotBlank(in0.quoteAccountId) ? in0.quoteAccountId : in0.repeatBuyAccountId;
        if (String.isNotBlank(accountId)) {
            out.put('QuoteAccountId', accountId);
            applyBillingHeaderDefaults(out, accountId);
        }
        // Service start, expiration, and term mirror the standard RLM_QuickQuote action.
        // Billing schedule generation and tax both key off these header values, so a
        // builder-created quote that omits them cannot bill/tax the way a Quick Quote can.
        out.put('StartDate', isoDate(Date.today()));
        out.put('ExpirationDate', isoDate(Date.today().addDays(30)));
        if (quoteHasField('RLM_TermMonths__c')) {
            out.put('RLM_TermMonths__c', 12);
        }
        // Stamp the validated TransactionProcessingType on the header so the sales transaction
        // line editor honors the same pricing/tax/rate permutation on later re-pricing.
        PstPrefs prefs = resolvePstPrefs(in0);
        if (String.isNotBlank(prefs.typeDeveloperName)) {
            out.put('TransactionType', prefs.typeDeveloperName);
        }
        return out;
    }

    /**
     * Copies the billing/shipping address and bill-to / primary contact from the source
     * Account onto a new quote header, mirroring the standard RLM_QuickQuote action.
     * Tax jurisdiction resolution and billing both rely on these values; a builder quote
     * that omits them is missing the billing information a Quick Quote would have set.
     * Only non-blank values are copied so we never overwrite with empty data.
     */
    private static void applyBillingHeaderDefaults(Map<String, Object> out, String accountId) {
        Id acctId;
        try {
            acctId = Id.valueOf(accountId);
        } catch (Exception e) {
            return; // invalid Id — leave header defaults to platform behavior
        }
        for (Account a : [
            SELECT BillingStreet, BillingCity, BillingState, BillingPostalCode, BillingCountry,
                   ShippingStreet, ShippingCity, ShippingState, ShippingPostalCode, ShippingCountry
            FROM Account WHERE Id = :acctId LIMIT 1
        ]) {
            putIfNotBlank(out, 'BillingStreet', a.BillingStreet);
            putIfNotBlank(out, 'BillingCity', a.BillingCity);
            putIfNotBlank(out, 'BillingState', a.BillingState);
            putIfNotBlank(out, 'BillingPostalCode', a.BillingPostalCode);
            putIfNotBlank(out, 'BillingCountry', a.BillingCountry);
            putIfNotBlank(out, 'ShippingStreet', a.ShippingStreet);
            putIfNotBlank(out, 'ShippingCity', a.ShippingCity);
            putIfNotBlank(out, 'ShippingState', a.ShippingState);
            putIfNotBlank(out, 'ShippingPostalCode', a.ShippingPostalCode);
            putIfNotBlank(out, 'ShippingCountry', a.ShippingCountry);
        }
        for (Contact c : [
            SELECT Email, Phone FROM Contact WHERE AccountId = :acctId ORDER BY CreatedDate ASC LIMIT 1
        ]) {
            out.put('BillToContactId', c.Id);
            out.put('ContactId', c.Id);
            putIfNotBlank(out, 'Email', c.Email);
            putIfNotBlank(out, 'Phone', c.Phone);
        }
    }

    private static void putIfNotBlank(Map<String, Object> out, String fieldName, String value) {
        if (String.isNotBlank(value)) {
            out.put(fieldName, value);
        }
    }

    // Cached lowercase field-name set so the optional RLM_TermMonths__c custom field is
    // only written when the org actually has it (keeps the builder safe across editions).
    private static Set<String> quoteFieldNames;
    private static Boolean quoteHasField(String apiName) {
        if (quoteFieldNames == null) {
            quoteFieldNames = Schema.SObjectType.Quote.fields.getMap().keySet();
        }
        return quoteFieldNames.contains(apiName.toLowerCase());
    }

    private static String isoDate(Date d) {
        return DateTime.newInstanceGmt(d, Time.newInstance(0, 0, 0, 0)).formatGmt('yyyy-MM-dd');
    }

    /**
     * Resolved Place Sales Transaction preferences for one builder run.
     *
     * A TransactionProcessingType record bundles a pricing/tax/rate permutation, but its
     * TransactionType field on the Quote is only honored by the REST PST resource when the
     * request sends no top-level prefs. The Apex PlaceSalesTransactionExecutor the builder
     * uses always requires non-null pricing/config prefs, so the record's preferences are
     * translated into call-level enums here. The validated DeveloperName is still stamped on
     * the Quote header so downstream re-pricing in the sales transaction line editor uses it.
     */
    @TestVisible
    private class PstPrefs {
        // Defaults preserve the builder's prior behavior: force pricing, run tax, no rate fetch.
        public RevSalesTrxn.PricingPreferenceEnum pricingPref = RevSalesTrxn.PricingPreferenceEnum.FORCE;
        public RevSalesTrxn.TaxPreferenceEnum taxPref = null;                  // null => tax runs by default
        public RevSalesTrxn.CatalogRatesPreferenceEnum catalogRatesPref = null; // null => rates not fetched
        public String typeDeveloperName;                                       // stamped on header when resolved
    }

    private static Map<String, TransactionProcessingType> tptCache;

    /**
     * Translates the Input.transactionType selection into call-level PST preferences.
     * Blank or unknown names fall back to safe defaults so the builder keeps working in any org.
     */
    @TestVisible
    private static PstPrefs resolvePstPrefs(Input in0) {
        PstPrefs prefs = new PstPrefs();
        if (in0 == null || String.isBlank(in0.transactionType)) {
            return prefs;
        }
        TransactionProcessingType tpt = lookupTransactionProcessingType(in0.transactionType.trim());
        if (tpt == null) {
            return prefs;
        }
        prefs.typeDeveloperName = tpt.DeveloperName;
        prefs.pricingPref = toPricingEnum(tpt.PricingPreference);
        prefs.taxPref = toTaxEnum(tpt.TaxPreference);
        prefs.catalogRatesPref = toCatalogRatesEnum(tpt.RatingPreference);
        return prefs;
    }

    private static TransactionProcessingType lookupTransactionProcessingType(String devName) {
        if (tptCache == null) {
            tptCache = new Map<String, TransactionProcessingType>();
            for (TransactionProcessingType t : [
                SELECT DeveloperName, PricingPreference, TaxPreference, RatingPreference
                FROM TransactionProcessingType
            ]) {
                tptCache.put(t.DeveloperName, t);
            }
        }
        return tptCache.get(devName);
    }

    @TestVisible
    private static RevSalesTrxn.PricingPreferenceEnum toPricingEnum(String v) {
        if (v == 'Skip') return RevSalesTrxn.PricingPreferenceEnum.SKIP;
        if (v == 'System') return RevSalesTrxn.PricingPreferenceEnum.SYSTEM;
        // 'Force' or unset -> FORCE preserves the builder's existing default.
        return RevSalesTrxn.PricingPreferenceEnum.FORCE;
    }

    @TestVisible
    private static RevSalesTrxn.TaxPreferenceEnum toTaxEnum(String v) {
        // Skip is the only tax preference value; anything else (incl. unset) runs tax by default.
        return (v == 'Skip') ? RevSalesTrxn.TaxPreferenceEnum.SKIP : null;
    }

    @TestVisible
    private static RevSalesTrxn.CatalogRatesPreferenceEnum toCatalogRatesEnum(String v) {
        // Only fetch catalog rate cards when the selected type asks for it (usage-based products).
        return (v == 'Fetch') ? RevSalesTrxn.CatalogRatesPreferenceEnum.FETCH : null;
    }

    private static String runFromHierarchyJson(Input in0, List<Integer> csvLinesAddedOut) {
        if (String.isBlank(in0.hierarchyJson)) throw new RLM_SetUpQuoteException('Hierarchy JSON is required.');
        if (csvLinesAddedOut == null) csvLinesAddedOut = new List<Integer>();
        Boolean isCreate = (in0.isCreate == true);
        Boolean largeDeal = (in0.largeDeal == true);
        String productSetMode = RLM_SetUpQuoteProductSets.normalizeProductSetMode(in0.productSetMode);
        if (!isCreate && String.isNotBlank(in0.groupsToDeleteJson)) deleteQuoteLineGroups(in0.quoteId, in0.groupsToDeleteJson);
        if (!isCreate) applyGroupRenames(in0.quoteId, in0.groupRenamesJson);
        Map<String, Id> tempIdToNewGroupId = new Map<String, Id>();
        if (!isCreate && String.isNotBlank(in0.newSubgroupsJson)) tempIdToNewGroupId = createNewSubgroupsUnderExisting(in0.quoteId, in0.newSubgroupsJson);
        Map<Id, Integer> siemensExistingGroupCounts = new Map<Id, Integer>();
        if (!isCreate && String.isNotBlank(in0.existingGroupCountsJson)) {
            if (RLM_SetUpQuoteProductSets.isSiemens(productSetMode)) {
                // Ownership guard: only retain existing-group counts for groups on this quote
                siemensExistingGroupCounts = filterGroupCountsToQuote(in0.quoteId, parseExistingGroupCounts(in0.existingGroupCountsJson, tempIdToNewGroupId));
            } else {
                appendExistingGroupCounts(in0.quoteId, in0.existingGroupCountsJson, tempIdToNewGroupId);
            }
        }
        Map<String, Object> treeMap = (Map<String, Object>) JSON.deserializeUntyped(in0.hierarchyJson);
        List<Object> parentsList = (List<Object>) treeMap.get('parents');
        if (parentsList == null) parentsList = new List<Object>();
        Integer ungroupedProductCount = in0.ungroupedProductCount != null ? in0.ungroupedProductCount : 0;
        // Empty-hierarchy shell handling:
        //   - Create: empty quote (2-step flow Step 1 = empty quote + large deal). A create
        //     WITH CSV is left to the normal ungrouped path below, so it must not enter here.
        //   - Modify: CSV-only ungrouped import (runHierarchyEmptyCsvModifyQuote) or a no-op
        //     Large Deal flip. The modify+CSV case must be reachable, so don't require CSV
        //     to be blank for modify (only for create).
        Boolean emptyHierarchyShell = parentsList.isEmpty() && !hasPositiveIdCount(siemensExistingGroupCounts) && ungroupedProductCount <= 0;
        if (emptyHierarchyShell && (String.isBlank(in0.csvImportLineItemsJson) || !isCreate)) {
            if (isCreate) {
                if (String.isBlank(in0.newQuoteName)) throw new RLM_SetUpQuoteException('New quote name required when creating.');
                Id pricebook2Id = getStandardPricebookId();
                RevSalesTrxn.RecordResource headerRecord = new RevSalesTrxn.RecordResource(Quote.getSObjectType(), 'POST');
                headerRecord.fieldValues = buildCreateQuoteHeaderFields(in0, pricebook2Id);
                List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords = new List<RevSalesTrxn.RecordWithReferenceRequest>{
                    new RevSalesTrxn.RecordWithReferenceRequest('refHeader', headerRecord)
                };
                RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('SetUpQuoteInvocable', listOfRecords);
                PstPrefs prefs = resolvePstPrefs(in0);
                RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
                    graph, prefs.pricingPref, RevSalesTrxn.ConfigurationExecutionEnum.SKIP,
                    new RevSalesTrxn.ConfigurationOptionsInput(), null, prefs.catalogRatesPref, prefs.taxPref, null);
                if (resp == null || !resp.isSuccess) throw new RLM_SetUpQuoteException(resp != null && resp.errorResponse != null ? String.valueOf(resp.errorResponse) : 'PST execution failed');
                Id quoteId = (Id) resp.salesTransactionId;
                if (largeDeal) update new Quote(Id = quoteId, IsLargeDeal = true);
                return quoteId;
            } else {
                if (String.isNotBlank(in0.csvImportLineItemsJson)) {
                    return runHierarchyEmptyCsvModifyQuote(in0, csvLinesAddedOut);
                }
                if (largeDeal && String.isNotBlank(in0.quoteId)) update new Quote(Id = in0.quoteId, IsLargeDeal = true);
                return in0.quoteId;
            }
        }
        Boolean useCsvImport = String.isNotBlank(in0.csvImportLineItemsJson);
        Map<String, Integer> countsMap = new Map<String, Integer>();
        if (!useCsvImport && String.isNotBlank(in0.productCountsJson)) {
            Map<String, Object> countsObj;
            try {
                countsObj = (Map<String, Object>) JSON.deserializeUntyped(in0.productCountsJson);
            } catch (Exception e) {
                // Malformed JSON must fail loudly: silently proceeding with an empty
                // counts map would create groups/lines with zero counts ("no lines added").
                throw new RLM_SetUpQuoteException('Invalid product counts JSON: ' + e.getMessage());
            }
            if (countsObj != null) {
                for (String k : countsObj.keySet()) {
                    Object v = countsObj.get(k);
                    Integer count = null;
                    try {
                        if (v instanceof Integer) count = (Integer) v;
                        else if (v instanceof Decimal) count = ((Decimal) v).intValue();
                        else if (v instanceof Long) count = ((Long) v).intValue();
                        else if (v instanceof Double) count = ((Double) v).intValue();
                        else if (v != null) count = Integer.valueOf(String.valueOf(v));
                    } catch (Exception e) {
                        // Skip a single unparseable entry rather than aborting the whole import.
                        continue;
                    }
                    if (count != null) countsMap.put(k, count);
                }
            }
        }
        Id pricebook2Id = getStandardPricebookId();
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords = new List<RevSalesTrxn.RecordWithReferenceRequest>();
        RevSalesTrxn.RecordResource headerRecord;
        if (isCreate) {
            if (String.isBlank(in0.newQuoteName)) throw new RLM_SetUpQuoteException('New quote name required when creating.');
            headerRecord = new RevSalesTrxn.RecordResource(Quote.getSObjectType(), 'POST');
            headerRecord.fieldValues = buildCreateQuoteHeaderFields(in0, pricebook2Id);
        } else {
            if (String.isBlank(in0.quoteId)) throw new RLM_SetUpQuoteException('Quote Id required when modifying.');
            headerRecord = new RevSalesTrxn.RecordResource(Quote.getSObjectType(), 'PATCH', in0.quoteId);
            headerRecord.fieldValues = new Map<String, Object>();
        }
        // Always add quote to graph so PST has a root and processes children. When modifying, use literal quoteId on groups/lines so they attach to existing quote (not a new one).
        listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refHeader', headerRecord));
        String quoteIdRef = isCreate ? '@{refHeader.id}' : String.valueOf(in0.quoteId);
        List<PricebookEntry> pbes = new List<PricebookEntry>();
        Map<String, PricebookEntry> productSetPbeMap = new Map<String, PricebookEntry>();
        Boolean hasProductSetGraphCounts = !useCsvImport && (hasPositivePathCount(countsMap) || hasPositiveIdCount(siemensExistingGroupCounts) || ungroupedProductCount > 0);
        if (hasProductSetGraphCounts) {
            productSetPbeMap = loadProductSetPricebookEntryMap(productSetMode, pricebook2Id);
        } else if (!useCsvImport && !countsMap.isEmpty()) {
            pbes = loadDemoRotationPricebookEntries(pricebook2Id);
            if (pbes.isEmpty()) throw new RLM_SetUpQuoteException('No valid price book entries found.');
        }
        Map<String, String> pathToGroupRef = new Map<String, String>();
        List<String> groupRefs = new List<String>();
        Integer sortOrder = 1;
        Integer refIdx = 0;
        List<Integer> lineIndexHolder = new List<Integer>{ 0 };
        Map<String, Integer> countsForGroups = useCsvImport ? new Map<String, Integer>() : countsMap;
        addLineItemsForExistingGroups(siemensExistingGroupCounts, listOfRecords, productSetPbeMap, productSetMode, lineIndexHolder, quoteIdRef);
        if (!isCreate && useCsvImport) {
            CsvMergeState mergeState = buildCsvMergeTargetsForModify(in0.quoteId, parentsList, listOfRecords, quoteIdRef, refIdx, sortOrder);
            pathToGroupRef.putAll(mergeState.pathToGroupTarget);
            refIdx = mergeState.refIdx;
            sortOrder = mergeState.sortOrder;
        } else {
            for (Integer pi = 0; pi < parentsList.size(); pi++) {
                Map<String, Object> parentNode = (Map<String, Object>) parentsList.get(pi);
                String path = parentNode.containsKey('path') ? String.valueOf(parentNode.get('path')) : String.valueOf(pi);
                String name = parentNode.containsKey('name') ? String.valueOf(parentNode.get('name')).trim() : ('Group ' + (pi + 1));
                if (String.isBlank(name)) name = 'Group ' + (pi + 1);
                String refName = 'refGrp_' + (refIdx++);
                pathToGroupRef.put(path, refName);
                RevSalesTrxn.RecordResource topRec = new RevSalesTrxn.RecordResource(QuoteLineGroup.getSObjectType(), 'POST');
                topRec.fieldValues = new Map<String, Object>{ 'Name' => name, 'QuoteId' => quoteIdRef, 'SortOrder' => sortOrder++ };
                listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest(refName, topRec));
                groupRefs.add(refName);
                addLineItemsForGroup(path, refName, countsForGroups, listOfRecords, pbes, productSetPbeMap, productSetMode, lineIndexHolder, quoteIdRef);
                List<Object> children = (List<Object>) parentNode.get('children');
                if (children != null && !children.isEmpty()) {
                    sortOrder = addChildGroups(children, refName, listOfRecords, groupRefs, refIdx, sortOrder, path, countsForGroups, pbes, productSetPbeMap, productSetMode, lineIndexHolder, pathToGroupRef, quoteIdRef);
                    refIdx = groupRefs.size();
                }
            }
        }
        Integer linesAdded = 0;
        if (useCsvImport) {
            linesAdded = !isCreate
                ? addLineItemsFromCsvImportToResolvedGroups(in0.csvImportLineItemsJson, pathToGroupRef, listOfRecords, pricebook2Id, lineIndexHolder, quoteIdRef)
                : addLineItemsFromCsvImport(in0.csvImportLineItemsJson, pathToGroupRef, listOfRecords, pricebook2Id, lineIndexHolder, quoteIdRef);
            csvLinesAddedOut.clear();
            csvLinesAddedOut.add(linesAdded != null ? linesAdded : 0);
        }
        if (String.isNotBlank(in0.repeatBuyAssignmentsJson)) {
            addLineItemsFromRepeatBuyAssignments(
                in0.repeatBuyAssignmentsJson,
                pathToGroupRef,
                listOfRecords,
                pricebook2Id,
                lineIndexHolder,
                quoteIdRef
            );
        }
        if (!useCsvImport && ungroupedProductCount > 0) {
            addProductRequestsForCount(ungroupedProductCount, null, listOfRecords, pbes, productSetPbeMap, productSetMode, lineIndexHolder, quoteIdRef);
        }
        Boolean hasLineItems = useCsvImport ? (linesAdded != null && linesAdded > 0) : (!countsMap.isEmpty() || hasPositiveIdCount(siemensExistingGroupCounts) || ungroupedProductCount > 0);
        // Default (skipConfiguration not set): FORCE when line items present — same as before 2-step/skipConfiguration. CSV import path unchanged.
        RevSalesTrxn.ConfigurationExecutionEnum configEnum = (in0.skipConfiguration == true)
            ? RevSalesTrxn.ConfigurationExecutionEnum.SKIP
            : (hasLineItems ? RevSalesTrxn.ConfigurationExecutionEnum.FORCE : RevSalesTrxn.ConfigurationExecutionEnum.SKIP);
        RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('SetUpQuoteInvocable', listOfRecords);
        // Pricing/tax/rate preferences come from the selected TransactionProcessingType
        // (Input.transactionType). Defaults run pricing (Force) and tax, matching the
        // standard quote save; a Skip-tax type stamps no tax treatment, and a Fetch-rates
        // type retrieves usage rate cards. configEnum (configuration method) is independent.
        PstPrefs prefs = resolvePstPrefs(in0);
        RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
            graph, prefs.pricingPref, configEnum,
            new RevSalesTrxn.ConfigurationOptionsInput(), null, prefs.catalogRatesPref, prefs.taxPref, null);
        if (resp == null || !resp.isSuccess) throw new RLM_SetUpQuoteException(resp != null && resp.errorResponse != null ? String.valueOf(resp.errorResponse) : 'PST execution failed');
        Id quoteId = isCreate ? (Id) resp.salesTransactionId : in0.quoteId;
        if (largeDeal) {
            update new Quote(Id = quoteId, IsLargeDeal = true);
        }
        return quoteId;
    }

    /**
     * Modify existing quote with CSV line items only: no QuoteLineGroup records (flat QuoteLineItems).
     * Use hierarchyJson = {"parents":[]} plus csvImportLineItemsJson (path keys ignored for grouping).
     */
    private static String runHierarchyEmptyCsvModifyQuote(Input in0, List<Integer> csvLinesAddedOut) {
        if (csvLinesAddedOut == null) csvLinesAddedOut = new List<Integer>();
        if (String.isBlank(in0.quoteId)) {
            throw new RLM_SetUpQuoteException('Quote Id required when modifying.');
        }
        Boolean largeDeal = (in0.largeDeal == true);
        Id pricebook2Id = getStandardPricebookId();
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords = new List<RevSalesTrxn.RecordWithReferenceRequest>();
        RevSalesTrxn.RecordResource headerRecord = new RevSalesTrxn.RecordResource(Quote.getSObjectType(), 'PATCH', in0.quoteId);
        headerRecord.fieldValues = new Map<String, Object>();
        listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refHeader', headerRecord));
        String quoteIdRef = String.valueOf(in0.quoteId);
        List<Integer> lineIndexHolder = new List<Integer>{ 0 };
        Integer linesAdded = addLineItemsFromCsvImportUngrouped(in0.csvImportLineItemsJson, listOfRecords, pricebook2Id, lineIndexHolder, quoteIdRef);
        csvLinesAddedOut.clear();
        csvLinesAddedOut.add(linesAdded != null ? linesAdded : 0);
        if (linesAdded == null || linesAdded == 0) {
            throw new RLM_SetUpQuoteException(
                'No quote line items were resolved from CSV for ungrouped import. Check Product Code / Name and active PricebookEntry on the Standard Price Book.'
            );
        }
        RevSalesTrxn.ConfigurationExecutionEnum configEnum = (in0.skipConfiguration == true)
            ? RevSalesTrxn.ConfigurationExecutionEnum.SKIP
            : RevSalesTrxn.ConfigurationExecutionEnum.FORCE;
        RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('SetUpQuoteInvocable', listOfRecords);
        PstPrefs prefs = resolvePstPrefs(in0);
        RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
            graph,
            prefs.pricingPref,
            configEnum,
            new RevSalesTrxn.ConfigurationOptionsInput(),
            null,
            prefs.catalogRatesPref,
            prefs.taxPref,
            null
        );
        if (resp == null || !resp.isSuccess) {
            throw new RLM_SetUpQuoteException(resp != null && resp.errorResponse != null ? String.valueOf(resp.errorResponse) : 'PST execution failed');
        }
        Id quoteId = in0.quoteId;
        if (largeDeal) {
            update new Quote(Id = quoteId, IsLargeDeal = true);
        }
        return quoteId;
    }

    private class CsvMergeState {
        Map<String, String> existingPathToGroupId = new Map<String, String>();
        Map<String, String> createdPathToTarget = new Map<String, String>();
        Map<String, String> pathToGroupTarget = new Map<String, String>();
        Set<String> ambiguousPathKeys = new Set<String>();
        Integer refIdx = 0;
        Integer sortOrder = 1;
    }

    private static CsvMergeState buildCsvMergeTargetsForModify(
        String quoteId,
        List<Object> parentsList,
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords,
        String quoteIdRef,
        Integer startRefIdx,
        Integer startSortOrder
    ) {
        if (String.isBlank(quoteId)) {
            throw new RLM_SetUpQuoteException('Quote Id required when modifying.');
        }
        CsvMergeState state = buildExistingCsvMergeState(Id.valueOf(quoteId));
        state.refIdx = startRefIdx != null ? startRefIdx : 0;
        state.sortOrder = startSortOrder != null ? startSortOrder : 1;
        for (Object parentObj : parentsList) {
            resolveCsvMergeNode((Map<String, Object>) parentObj, new List<String>(), null, state, listOfRecords, quoteIdRef);
        }
        return state;
    }

    private static CsvMergeState buildExistingCsvMergeState(Id quoteId) {
        CsvMergeState state = new CsvMergeState();
        List<QuoteLineGroup> groups = [
            SELECT Id, Name, ParentQuoteLineGroupId, SortOrder
            FROM QuoteLineGroup
            WHERE QuoteId = :quoteId
            ORDER BY ParentQuoteLineGroupId NULLS FIRST, SortOrder NULLS LAST, Name
        ];
        Map<Id, List<QuoteLineGroup>> childrenByParent = new Map<Id, List<QuoteLineGroup>>();
        List<QuoteLineGroup> roots = new List<QuoteLineGroup>();
        for (QuoteLineGroup groupRow : groups) {
            if (groupRow.ParentQuoteLineGroupId == null) {
                roots.add(groupRow);
            } else {
                if (!childrenByParent.containsKey(groupRow.ParentQuoteLineGroupId)) {
                    childrenByParent.put(groupRow.ParentQuoteLineGroupId, new List<QuoteLineGroup>());
                }
                childrenByParent.get(groupRow.ParentQuoteLineGroupId).add(groupRow);
            }
        }
        for (QuoteLineGroup root : roots) {
            collectExistingCsvPath(root, childrenByParent, new List<String>(), state);
        }
        if (!state.ambiguousPathKeys.isEmpty()) {
            throw new RLM_SetUpQuoteException(
                'Existing quote has duplicate group paths after CSV normalization: ' +
                String.join(new List<String>(state.ambiguousPathKeys), ', ') +
                '. Rename one group or adjust the CSV before importing.'
            );
        }
        return state;
    }

    private static void collectExistingCsvPath(
        QuoteLineGroup groupRow,
        Map<Id, List<QuoteLineGroup>> childrenByParent,
        List<String> parentNames,
        CsvMergeState state
    ) {
        List<String> names = new List<String>();
        names.addAll(parentNames);
        names.add(groupRow.Name);
        String key = csvMergePathKey(names);
        String groupId = String.valueOf(groupRow.Id);
        if (state.existingPathToGroupId.containsKey(key) && state.existingPathToGroupId.get(key) != groupId) {
            state.ambiguousPathKeys.add(key);
        } else {
            state.existingPathToGroupId.put(key, groupId);
        }
        if (childrenByParent.containsKey(groupRow.Id)) {
            for (QuoteLineGroup child : childrenByParent.get(groupRow.Id)) {
                collectExistingCsvPath(child, childrenByParent, names, state);
            }
        }
    }

    private static void resolveCsvMergeNode(
        Map<String, Object> node,
        List<String> parentNames,
        String parentTarget,
        CsvMergeState state,
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords,
        String quoteIdRef
    ) {
        if (node == null) return;
        String name = node.containsKey('name') ? String.valueOf(node.get('name')).trim() : null;
        if (String.isBlank(name)) {
            name = 'Group';
        }
        List<String> names = new List<String>();
        names.addAll(parentNames);
        names.add(name);
        String key = csvMergePathKey(names);
        String target = null;
        if (state.existingPathToGroupId.containsKey(key)) {
            target = state.existingPathToGroupId.get(key);
        } else if (state.createdPathToTarget.containsKey(key)) {
            target = state.createdPathToTarget.get(key);
        } else {
            String refName = 'refGrp_' + state.refIdx++;
            target = '@{' + refName + '.id}';
            state.createdPathToTarget.put(key, target);
            RevSalesTrxn.RecordResource groupRecord = new RevSalesTrxn.RecordResource(QuoteLineGroup.getSObjectType(), 'POST');
            groupRecord.fieldValues = new Map<String, Object>{
                'Name' => name,
                'QuoteId' => quoteIdRef,
                'SortOrder' => state.sortOrder++
            };
            if (String.isNotBlank(parentTarget)) {
                groupRecord.fieldValues.put('ParentQuoteLineGroupId', parentTarget);
            }
            listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest(refName, groupRecord));
        }
        if (node.containsKey('path') && node.get('path') != null) {
            state.pathToGroupTarget.put(String.valueOf(node.get('path')), target);
        }
        List<Object> children = (List<Object>) node.get('children');
        if (children != null) {
            for (Object childObj : children) {
                resolveCsvMergeNode((Map<String, Object>) childObj, names, target, state, listOfRecords, quoteIdRef);
            }
        }
    }

    private static String csvMergePathKey(List<String> names) {
        List<String> parts = new List<String>();
        for (String name : names) {
            String part = normalizeCsvMergeSegment(name);
            if (String.isNotBlank(part)) {
                parts.add(part);
            }
        }
        return String.join(parts, '|');
    }

    private static String normalizeCsvMergeSegment(String value) {
        return String.isBlank(value) ? '' : value.trim().toLowerCase().replaceAll('\\s+', '');
    }

    private static Boolean hasPositiveIdCount(Map<Id, Integer> countsMap) {
        if (countsMap == null || countsMap.isEmpty()) return false;
        for (Integer count : countsMap.values()) {
            if (count != null && count > 0) return true;
        }
        return false;
    }

    private static Boolean hasPositivePathCount(Map<String, Integer> countsMap) {
        if (countsMap == null || countsMap.isEmpty()) return false;
        for (Integer count : countsMap.values()) {
            if (count != null && count > 0) return true;
        }
        return false;
    }

    private static void addLineItemsForExistingGroups(
        Map<Id, Integer> groupIdToCount,
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords,
        Map<String, PricebookEntry> productSetPbeMap,
        String productSetMode,
        List<Integer> lineIndexHolder,
        String quoteIdRef
    ) {
        if (groupIdToCount == null || groupIdToCount.isEmpty()) return;
        for (Id groupId : groupIdToCount.keySet()) {
            addProductRequestsForCount(groupIdToCount.get(groupId), String.valueOf(groupId), listOfRecords, null, productSetPbeMap, productSetMode, lineIndexHolder, quoteIdRef);
        }
    }

    private static void addLineItemsForGroup(
        String path,
        String groupRef,
        Map<String, Integer> countsMap,
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords,
        List<PricebookEntry> pbes,
        Map<String, PricebookEntry> productSetPbeMap,
        String productSetMode,
        List<Integer> lineIndexHolder,
        String quoteIdRef
    ) {
        Integer count = countsMap.containsKey(path) ? countsMap.get(path) : 0;
        if (count == null || count <= 0) return;
        addProductRequestsForCount(count, '@{' + groupRef + '.id}', listOfRecords, pbes, productSetPbeMap, productSetMode, lineIndexHolder, quoteIdRef);
    }

    private static void addProductRequestsForCount(
        Integer count,
        String quoteLineGroupIdRef,
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords,
        List<PricebookEntry> pbes,
        Map<String, PricebookEntry> productSetPbeMap,
        String productSetMode,
        List<Integer> lineIndexHolder,
        String quoteIdRef
    ) {
        if (count == null || count <= 0) return;
        Integer lineIndex = lineIndexHolder[0];
        if (productSetPbeMap != null && !productSetPbeMap.isEmpty()) {
            String productSetLabel = RLM_SetUpQuoteProductSets.isSiemens(productSetMode) ? 'Siemens' : 'QuantumBit';
            for (RLM_SetUpQuoteProductSets.ProductRequest request : RLM_SetUpQuoteProductSets.allocateRequests(productSetMode, count)) {
                PricebookEntry pbe = productSetPbeMap.get(request.productIdentifier);
                if (pbe == null) {
                    throw new RLM_SetUpQuoteException('Missing price book entry for ' + productSetLabel + ' product ' + request.productIdentifier);
                }
                RevSalesTrxn.RecordResource lineRec = new RevSalesTrxn.RecordResource(QuoteLineItem.getSObjectType(), 'POST');
                lineRec.fieldValues = buildQuoteLineItemFields(pbe, quoteIdRef, quoteLineGroupIdRef);
                listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refLine' + lineIndex, lineRec));
                lineIndex++;
            }
        } else {
            for (Integer i = 0; i < count; i++) {
                PricebookEntry pbe = pbes.get(Math.mod(i, pbes.size()));
                RevSalesTrxn.RecordResource lineRec = new RevSalesTrxn.RecordResource(QuoteLineItem.getSObjectType(), 'POST');
                lineRec.fieldValues = buildQuoteLineItemFields(pbe, quoteIdRef, quoteLineGroupIdRef);
                listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refLine' + lineIndex, lineRec));
                lineIndex++;
            }
        }
        lineIndexHolder[0] = lineIndex;
    }

    private static Map<String, Object> buildQuoteLineItemFields(PricebookEntry pbe, String quoteIdRef, String quoteLineGroupIdRef) {
        return buildQuoteLineItemFields(pbe, quoteIdRef, quoteLineGroupIdRef, 1);
    }

    private static Map<String, Object> buildQuoteLineItemFields(PricebookEntry pbe, String quoteIdRef, String quoteLineGroupIdRef, Decimal quantity) {
        Decimal unitPrice = (pbe.UnitPrice != null) ? pbe.UnitPrice : 0;
        String sellingModelType = pbe.ProductSellingModel != null ? String.valueOf(pbe.ProductSellingModel.SellingModelType) : null;
        String pricingTermUnit = pbe.ProductSellingModel != null ? String.valueOf(pbe.ProductSellingModel.PricingTermUnit) : null;
        String billingFrequency = (String.isNotBlank(pricingTermUnit) && PRICING_TERM_TO_BILLING_FREQUENCY.containsKey(pricingTermUnit)) ? PRICING_TERM_TO_BILLING_FREQUENCY.get(pricingTermUnit) : null;
        Map<String, Object> fields = new Map<String, Object>{
            'QuoteId' => quoteIdRef,
            'Product2Id' => pbe.Product2Id,
            'PricebookEntryId' => pbe.Id,
            'Quantity' => (quantity != null && quantity > 0) ? quantity : 1, // rule: no/zero quantity → 1
            'UnitPrice' => unitPrice
        };
        if (String.isNotBlank(quoteLineGroupIdRef)) {
            fields.put('QuoteLineGroupId', quoteLineGroupIdRef);
        }
        if ('TermDefined' == sellingModelType && String.isNotBlank(billingFrequency)) {
            fields.put('StartDate', subscriptionStartDateIso());
            fields.put('EndDate', subscriptionEndDateIso());
            fields.put('PeriodBoundary', 'Anniversary');
            fields.put('BillingFrequency', billingFrequency);
        } else if ('Evergreen' == sellingModelType && String.isNotBlank(billingFrequency)) {
            fields.put('StartDate', subscriptionStartDateIso());
            fields.put('PeriodBoundary', 'Anniversary');
            fields.put('BillingFrequency', billingFrequency);
        }
        return fields;
    }

    // Subscription line dates are relative to today (term = 1 year) so Set Up Quote runs
    // never produce stale fixed dates. Cached per transaction since buildQuoteLineItemFields
    // is called once per line item (potentially thousands of times).
    private static String startDateIsoCache;
    private static String endDateIsoCache;

    private static String subscriptionStartDateIso() {
        if (startDateIsoCache == null) {
            startDateIsoCache = DateTime.newInstanceGmt(Date.today(), Time.newInstance(0, 0, 0, 0)).formatGmt('yyyy-MM-dd') + 'T00:00:00.000Z';
        }
        return startDateIsoCache;
    }

    private static String subscriptionEndDateIso() {
        if (endDateIsoCache == null) {
            endDateIsoCache = DateTime.newInstanceGmt(Date.today().addYears(1), Time.newInstance(0, 0, 0, 0)).formatGmt('yyyy-MM-dd') + 'T00:00:00.000Z';
        }
        return endDateIsoCache;
    }

    private static Integer addLineItemsFromCsvImport(String csvImportLineItemsJson, Map<String, String> pathToGroupRef, List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords, Id pricebook2Id, List<Integer> lineIndexHolder, String quoteIdRef) {
        List<Object> items;
        try {
            items = (List<Object>) JSON.deserializeUntyped(csvImportLineItemsJson);
        } catch (Exception e) {
            return 0;
        }
        if (items == null || items.isEmpty()) return 0;
        List<String> allIdentifiers = new List<String>();
        for (Object itemObj : items) {
            Map<String, Object> item = (Map<String, Object>) itemObj;
            String productIdentifier = item != null && item.containsKey('productIdentifier') ? String.valueOf(item.get('productIdentifier')) : null;
            if (String.isNotBlank(productIdentifier)) allIdentifiers.add(productIdentifier.trim());
        }
        Map<String, PricebookEntry> pbeMap = RLM_ProductCatalogPbeService.resolveProductsToPBEMap(allIdentifiers, pricebook2Id);
        Integer lineIndex = lineIndexHolder[0];
        Integer linesAdded = 0;
        for (Object itemObj : items) {
            Map<String, Object> item = (Map<String, Object>) itemObj;
            String path = item != null && item.containsKey('path') && item.get('path') != null ? String.valueOf(item.get('path')) : null;
            String productIdentifier = item != null && item.containsKey('productIdentifier') ? String.valueOf(item.get('productIdentifier')) : null;
            Object qtyObj = (item != null && item.containsKey('quantity')) ? item.get('quantity') : null;
            // Rule: if no quantity is provided (or it is non-numeric), treat quantity as 1
            Decimal qty = parseCsvQuantity(qtyObj);
            if (String.isBlank(productIdentifier)) continue;
            String quoteLineGroupIdRef = null;
            if (String.isNotBlank(path)) {
                String groupRef = pathToGroupRef.get(path);
                if (String.isBlank(groupRef)) continue;
                quoteLineGroupIdRef = '@{' + groupRef + '.id}';
            }
            String trimmed = productIdentifier.trim();
            PricebookEntry pbe = pbeMap.get(trimmed);
            if (pbe == null && trimmed.contains(',')) {
                String prefix = trimmed.substring(0, trimmed.lastIndexOf(',')).trim();
                if (String.isNotBlank(prefix)) pbe = pbeMap.get(prefix);
            }
            if (pbe == null) continue;
            RevSalesTrxn.RecordResource lineRec = new RevSalesTrxn.RecordResource(QuoteLineItem.getSObjectType(), 'POST');
            lineRec.fieldValues = buildQuoteLineItemFields(pbe, quoteIdRef, quoteLineGroupIdRef, qty);
            listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refLine' + lineIndex, lineRec));
            lineIndex++;
            linesAdded++;
        }
        lineIndexHolder[0] = lineIndex;
        return linesAdded;
    }

    /**
     * Parse a CSV row quantity defensively. Missing, blank, or non-numeric
     * values (e.g. "1,000" or "two") default to 1 instead of throwing and
     * aborting the entire Set Up Quote run.
     */
    private static Decimal parseCsvQuantity(Object qtyObj) {
        if (qtyObj instanceof Integer) return (Integer) qtyObj;
        if (qtyObj instanceof Decimal) return (Decimal) qtyObj;
        if (qtyObj == null) return 1;
        String s = String.valueOf(qtyObj);
        if (String.isBlank(s)) return 1;
        try {
            return Decimal.valueOf(s.trim());
        } catch (Exception e) {
            return 1;
        }
    }

    private static Integer addLineItemsFromCsvImportToResolvedGroups(
        String csvImportLineItemsJson,
        Map<String, String> pathToGroupTarget,
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords,
        Id pricebook2Id,
        List<Integer> lineIndexHolder,
        String quoteIdRef
    ) {
        List<Object> items;
        try {
            items = (List<Object>) JSON.deserializeUntyped(csvImportLineItemsJson);
        } catch (Exception e) {
            return 0;
        }
        if (items == null || items.isEmpty()) return 0;
        List<String> allIdentifiers = new List<String>();
        for (Object itemObj : items) {
            Map<String, Object> item = (Map<String, Object>) itemObj;
            String productIdentifier = item != null && item.containsKey('productIdentifier') ? String.valueOf(item.get('productIdentifier')) : null;
            if (String.isNotBlank(productIdentifier)) allIdentifiers.add(productIdentifier.trim());
        }
        Map<String, PricebookEntry> pbeMap = RLM_ProductCatalogPbeService.resolveProductsToPBEMap(allIdentifiers, pricebook2Id);
        Integer lineIndex = lineIndexHolder[0];
        Integer linesAdded = 0;
        for (Object itemObj : items) {
            Map<String, Object> item = (Map<String, Object>) itemObj;
            String path = item != null && item.containsKey('path') && item.get('path') != null ? String.valueOf(item.get('path')) : null;
            String productIdentifier = item != null && item.containsKey('productIdentifier') ? String.valueOf(item.get('productIdentifier')) : null;
            Object qtyObj = (item != null && item.containsKey('quantity')) ? item.get('quantity') : null;
            Decimal qty = parseCsvQuantity(qtyObj);
            if (String.isBlank(productIdentifier)) continue;
            String groupTarget = null;
            if (String.isNotBlank(path)) {
                groupTarget = pathToGroupTarget.get(path);
                if (String.isBlank(groupTarget)) continue;
            }
            String trimmed = productIdentifier.trim();
            PricebookEntry pbe = pbeMap.get(trimmed);
            if (pbe == null && trimmed.contains(',')) {
                String prefix = trimmed.substring(0, trimmed.lastIndexOf(',')).trim();
                if (String.isNotBlank(prefix)) pbe = pbeMap.get(prefix);
            }
            if (pbe == null) continue;
            RevSalesTrxn.RecordResource lineRec = new RevSalesTrxn.RecordResource(QuoteLineItem.getSObjectType(), 'POST');
            lineRec.fieldValues = buildQuoteLineItemFields(pbe, quoteIdRef, groupTarget, qty);
            listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refLine' + lineIndex, lineRec));
            lineIndex++;
            linesAdded++;
        }
        lineIndexHolder[0] = lineIndex;
        return linesAdded;
    }

    /** Same as addLineItemsFromCsvImport but QuoteLineItem has no QuoteLineGroupId (path not matched to groups). */
    private static Integer addLineItemsFromCsvImportUngrouped(
        String csvImportLineItemsJson,
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords,
        Id pricebook2Id,
        List<Integer> lineIndexHolder,
        String quoteIdRef
    ) {
        List<Object> items;
        try {
            items = (List<Object>) JSON.deserializeUntyped(csvImportLineItemsJson);
        } catch (Exception e) {
            return 0;
        }
        if (items == null || items.isEmpty()) return 0;
        List<String> allIdentifiers = new List<String>();
        for (Object itemObj : items) {
            Map<String, Object> item = (Map<String, Object>) itemObj;
            String productIdentifier = item != null && item.containsKey('productIdentifier') ? String.valueOf(item.get('productIdentifier')) : null;
            if (String.isNotBlank(productIdentifier)) allIdentifiers.add(productIdentifier.trim());
        }
        Map<String, PricebookEntry> pbeMap = RLM_ProductCatalogPbeService.resolveProductsToPBEMap(allIdentifiers, pricebook2Id);
        Integer lineIndex = lineIndexHolder[0];
        Integer linesAdded = 0;
        for (Object itemObj : items) {
            Map<String, Object> item = (Map<String, Object>) itemObj;
            String productIdentifier = item != null && item.containsKey('productIdentifier') ? String.valueOf(item.get('productIdentifier')) : null;
            Object qtyObj = (item != null && item.containsKey('quantity')) ? item.get('quantity') : null;
            Decimal qty = parseCsvQuantity(qtyObj);
            if (String.isBlank(productIdentifier)) continue;
            String trimmed = productIdentifier.trim();
            PricebookEntry pbe = pbeMap.get(trimmed);
            if (pbe == null && trimmed.contains(',')) {
                String prefix = trimmed.substring(0, trimmed.lastIndexOf(',')).trim();
                if (String.isNotBlank(prefix)) pbe = pbeMap.get(prefix);
            }
            if (pbe == null) continue;
            RevSalesTrxn.RecordResource lineRec = new RevSalesTrxn.RecordResource(QuoteLineItem.getSObjectType(), 'POST');
            lineRec.fieldValues = buildQuoteLineItemFields(pbe, quoteIdRef, null, qty);
            listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refLine' + lineIndex, lineRec));
            lineIndex++;
            linesAdded++;
        }
        lineIndexHolder[0] = lineIndex;
        return linesAdded;
    }

    private static void addLineItemsFromRepeatBuyAssignments(
        String repeatBuyAssignmentsJson,
        Map<String, String> pathToGroupRef,
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords,
        Id pricebook2Id,
        List<Integer> lineIndexHolder,
        String quoteIdRef
    ) {
        if (String.isBlank(repeatBuyAssignmentsJson) || pathToGroupRef == null || pathToGroupRef.isEmpty()) return;
        List<Object> rows;
        try {
            rows = (List<Object>) JSON.deserializeUntyped(repeatBuyAssignmentsJson);
        } catch (Exception e) {
            return;
        }
        if (rows == null || rows.isEmpty()) return;

        List<String> ids = new List<String>();
        for (Object rowObj : rows) {
            Map<String, Object> row = (Map<String, Object>) rowObj;
            String pid = row != null && row.containsKey('productIdentifier') ? String.valueOf(row.get('productIdentifier')) : null;
            if (String.isNotBlank(pid)) ids.add(pid.trim());
        }
        Map<String, PricebookEntry> pbeMap = RLM_ProductCatalogPbeService.resolveProductsToPBEMap(ids, pricebook2Id);
        Integer lineIndex = lineIndexHolder[0];

        for (Object rowObj : rows) {
            Map<String, Object> row = (Map<String, Object>) rowObj;
            if (row == null) continue;
            Boolean removed = row.containsKey('removed') && row.get('removed') == true;
            if (removed) continue;

            String productIdentifier = row.containsKey('productIdentifier') ? String.valueOf(row.get('productIdentifier')) : null;
            if (String.isBlank(productIdentifier)) continue;
            String sourcePath = row.containsKey('sourcePath') ? String.valueOf(row.get('sourcePath')) : null;
            String targetPath = row.containsKey('targetPath') ? String.valueOf(row.get('targetPath')) : null;
            if (String.isBlank(targetPath)) targetPath = sourcePath;
            if (String.isBlank(targetPath)) continue;

            Decimal qty = 1;
            if (row.containsKey('quantity') && row.get('quantity') != null) {
                try {
                    qty = Decimal.valueOf(String.valueOf(row.get('quantity')));
                } catch (Exception e) {
                    qty = 1;
                }
            }
            if (qty == null || qty <= 0) qty = 1;

            String trimmed = productIdentifier.trim();
            PricebookEntry pbe = pbeMap.get(trimmed);
            if (pbe == null && trimmed.contains(',')) {
                String prefix = trimmed.substring(0, trimmed.lastIndexOf(',')).trim();
                if (String.isNotBlank(prefix)) pbe = pbeMap.get(prefix);
            }
            if (pbe == null) continue;

            Boolean duplicateToTarget = row.containsKey('duplicateToTarget') && row.get('duplicateToTarget') == true;
            if (duplicateToTarget && String.isNotBlank(sourcePath) && sourcePath != targetPath) {
                String srcRef = pathToGroupRef.get(sourcePath);
                if (String.isNotBlank(srcRef)) {
                    RevSalesTrxn.RecordResource srcLineRec = new RevSalesTrxn.RecordResource(QuoteLineItem.getSObjectType(), 'POST');
                    srcLineRec.fieldValues = buildQuoteLineItemFields(pbe, quoteIdRef, '@{' + srcRef + '.id}', qty);
                    listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refLine' + lineIndex, srcLineRec));
                    lineIndex++;
                }
            }

            String tgtRef = pathToGroupRef.get(targetPath);
            if (String.isBlank(tgtRef)) continue;
            RevSalesTrxn.RecordResource lineRec = new RevSalesTrxn.RecordResource(QuoteLineItem.getSObjectType(), 'POST');
            lineRec.fieldValues = buildQuoteLineItemFields(pbe, quoteIdRef, '@{' + tgtRef + '.id}', qty);
            listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refLine' + lineIndex, lineRec));
            lineIndex++;
        }
        lineIndexHolder[0] = lineIndex;
    }

    @AuraEnabled(cacheable=false)
    public static List<Map<String, String>> getAccountsForRepeatBuy() {
        List<Map<String, String>> out = new List<Map<String, String>>();
        for (Account a : [
            SELECT Id, Name
            FROM Account
            ORDER BY Name
            LIMIT 200
        ]) {
            out.add(new Map<String, String>{
                'value' => a.Id,
                'label' => String.isNotBlank(a.Name) ? a.Name : ('Account ' + a.Id)
            });
        }
        return out;
    }

    @AuraEnabled(cacheable=false)
    public static List<Map<String, String>> getRecentQuotesForRepeatBuy(String accountId) {
        List<Map<String, String>> out = new List<Map<String, String>>();
        if (String.isBlank(accountId)) return out;
        List<Quote> rows = [
            SELECT Id, Name, QuoteNumber, Status, LastModifiedDate
            FROM Quote
            WHERE AccountId = :accountId OR QuoteAccountId = :accountId
            ORDER BY LastModifiedDate DESC
            LIMIT 10
        ];
        for (Quote q : rows) {
            out.add(new Map<String, String>{
                'value' => q.Id,
                'label' => (String.isNotBlank(q.Name) ? q.Name : q.QuoteNumber) + ' (' + q.QuoteNumber + ')',
                'status' => String.valueOf(q.Status),
                'lastModified' => String.valueOf(q.LastModifiedDate)
            });
        }
        return out;
    }

    @AuraEnabled(cacheable=false)
    public static String getRepeatBuyLines(String quoteIdsJson) {
        if (String.isBlank(quoteIdsJson)) return '[]';
        List<Object> arr = (List<Object>) JSON.deserializeUntyped(quoteIdsJson);
        Set<Id> quoteIds = new Set<Id>();
        for (Object o : arr) {
            if (o != null && String.isNotBlank(String.valueOf(o))) {
                try {
                    quoteIds.add(Id.valueOf(String.valueOf(o)));
                } catch (Exception e) {
                    /* ignore bad id */
                }
            }
        }
        if (quoteIds.isEmpty()) return '[]';

        Map<Id, Quote> quoteById = new Map<Id, Quote>([
            SELECT Id, Name, QuoteNumber, Status, LastModifiedDate
            FROM Quote
            WHERE Id IN :quoteIds
        ]);

        // Dynamic net-total field fallback by org capability.
        String netField = 'TotalPrice';
        Map<String, Schema.SObjectField> fld = Schema.SObjectType.QuoteLineItem.fields.getMap();
        if (fld.containsKey('NetAmount')) netField = 'NetAmount';
        else if (fld.containsKey('SBQQ__NetTotal__c')) netField = 'SBQQ__NetTotal__c';

        String soql =
            'SELECT Id, QuoteId, Quantity, UnitPrice, Product2Id, Product2.Name, Product2.ProductCode, QuoteLineGroupId, QuoteLineGroup.Name, ' +
            netField +
            ' FROM QuoteLineItem WHERE QuoteId IN :quoteIds WITH USER_MODE ORDER BY QuoteId, QuoteLineGroup.Name, CreatedDate';
        List<QuoteLineItem> lines = Database.query(soql);

        Map<Id, List<Map<String, Object>>> grouped = new Map<Id, List<Map<String, Object>>>();
        for (QuoteLineItem li : lines) {
            if (!grouped.containsKey(li.QuoteId)) grouped.put(li.QuoteId, new List<Map<String, Object>>());
            grouped.get(li.QuoteId).add(new Map<String, Object>{
                'lineId' => li.Id,
                'groupName' => (li.QuoteLineGroup != null && String.isNotBlank(li.QuoteLineGroup.Name)) ? li.QuoteLineGroup.Name : 'Ungrouped',
                'productName' => (li.Product2 != null ? li.Product2.Name : null),
                'productCode' => (li.Product2 != null ? li.Product2.ProductCode : null),
                'historicalQuantity' => li.Quantity,
                'editableQuantity' => li.Quantity,
                'historicalUnitPrice' => li.UnitPrice,
                'historicalNetTotal' => li.get(netField)
            });
        }

        List<Map<String, Object>> payload = new List<Map<String, Object>>();
        for (Id qId : quoteIds) {
            Quote q = quoteById.get(qId);
            if (q == null) continue;
            payload.add(new Map<String, Object>{
                'quoteId' => q.Id,
                'quoteLabel' => (String.isNotBlank(q.Name) ? q.Name : q.QuoteNumber) + ' (' + q.QuoteNumber + ')',
                'status' => q.Status,
                'lines' => (grouped.containsKey(qId) ? grouped.get(qId) : new List<Map<String, Object>>())
            });
        }
        return JSON.serialize(payload);
    }

    private static Integer addChildGroups(
        List<Object> children,
        String parentRef,
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords,
        List<String> groupRefs,
        Integer refIdx,
        Integer sortOrder,
        String parentPath,
        Map<String, Integer> countsMap,
        List<PricebookEntry> pbes,
        Map<String, PricebookEntry> productSetPbeMap,
        String productSetMode,
        List<Integer> lineIndexHolder,
        Map<String, String> pathToGroupRef,
        String quoteIdRef
    ) {
        for (Integer ci = 0; ci < children.size(); ci++) {
            Map<String, Object> node = (Map<String, Object>) children.get(ci);
            String path = node.containsKey('path') ? String.valueOf(node.get('path')) : (parentPath != '' ? parentPath + '-' + ci : String.valueOf(ci));
            String name = node.containsKey('name') ? String.valueOf(node.get('name')).trim() : ('Group ' + path);
            if (String.isBlank(name)) name = 'Group ' + path;
            String refName = 'refGrp_' + refIdx++;
            if (pathToGroupRef != null) pathToGroupRef.put(path, refName);
            RevSalesTrxn.RecordResource rec = new RevSalesTrxn.RecordResource(QuoteLineGroup.getSObjectType(), 'POST');
            rec.fieldValues = new Map<String, Object>{
                'Name' => name, 'QuoteId' => quoteIdRef, 'ParentQuoteLineGroupId' => '@{' + parentRef + '.id}', 'SortOrder' => sortOrder++
            };
            listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest(refName, rec));
            groupRefs.add(refName);
            addLineItemsForGroup(path, refName, countsMap, listOfRecords, pbes, productSetPbeMap, productSetMode, lineIndexHolder, quoteIdRef);
            List<Object> sub = (List<Object>) node.get('children');
            if (sub != null && !sub.isEmpty()) sortOrder = addChildGroups(sub, refName, listOfRecords, groupRefs, refIdx, sortOrder, path, countsMap, pbes, productSetPbeMap, productSetMode, lineIndexHolder, pathToGroupRef, quoteIdRef);
            refIdx = groupRefs.size();
        }
        return sortOrder;
    }

    private static String getPathByIndex(Map<String, Object> treeMap, Integer index) {
        List<String> paths = new List<String>();
        List<Object> parents = (List<Object>) treeMap.get('parents');
        if (parents == null) return '';
        collectPaths(parents, '', paths);
        return index < paths.size() ? paths.get(index) : '';
    }

    private static void collectPaths(List<Object> nodes, String basePath, List<String> out) {
        for (Integer i = 0; i < nodes.size(); i++) {
            Map<String, Object> n = (Map<String, Object>) nodes.get(i);
            String path = basePath != '' ? basePath + '-' + i : String.valueOf(i);
            out.add(path);
            List<Object> children = (List<Object>) n.get('children');
            if (children != null && !children.isEmpty()) collectPaths(children, path, out);
        }
    }

    private static String runTree(Input in0) {
        List<String> parentNames = in0.parentGroupNames != null ? in0.parentGroupNames : new List<String>();
        if (parentNames.isEmpty()) {
            throw new RLM_SetUpQuoteException('Add at least one parent group. Enter a parent group name and click Next, then choose 2 for "Add another parent?".');
        }
        Boolean isCreate = (in0.isCreate == true);
        Boolean largeDeal = (in0.largeDeal == true);
        List<String> subgroupCSVList = in0.subgroupNamesPerParent != null ? in0.subgroupNamesPerParent : new List<String>();
        List<String> countCSVList = in0.productCountsPerParent != null ? in0.productCountsPerParent : new List<String>();
        // Pad to match parent count (flow may send shorter lists)
        while (subgroupCSVList.size() < parentNames.size()) subgroupCSVList.add('');
        while (countCSVList.size() < parentNames.size()) countCSVList.add('');

        Id pricebook2Id = getStandardPricebookId();
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords = new List<RevSalesTrxn.RecordWithReferenceRequest>();

        RevSalesTrxn.RecordResource headerRecord;
        if (isCreate) {
            if (String.isBlank(in0.newQuoteName)) throw new RLM_SetUpQuoteException('New quote name required when creating.');
            headerRecord = new RevSalesTrxn.RecordResource(Quote.getSObjectType(), 'POST');
            Map<String, Object> headerFields = buildCreateQuoteHeaderFields(in0, pricebook2Id);
            if (largeDeal) headerFields.put('IsLargeDeal', true);
            headerRecord.fieldValues = headerFields;
        } else {
            if (String.isBlank(in0.quoteId)) throw new RLM_SetUpQuoteException('Quote Id required when modifying.');
            headerRecord = new RevSalesTrxn.RecordResource(Quote.getSObjectType(), 'PATCH', in0.quoteId);
            if (largeDeal) headerRecord.fieldValues = new Map<String, Object>{ 'IsLargeDeal' => true };
        }
        listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refHeader', headerRecord));

        List<String> groupRefs = new List<String>();
        List<Integer> groupsPerParent = new List<Integer>();
        Integer sortOrder = 1;
        for (Integer p = 0; p < parentNames.size(); p++) {
            String raw = parentNames[p];
            String parentName = String.isNotBlank(raw) ? raw.trim() : ('Group ' + (p + 1));
            String refTop = 'refTop' + (p + 1);
            RevSalesTrxn.RecordResource topRec = new RevSalesTrxn.RecordResource(QuoteLineGroup.getSObjectType(), 'POST');
            topRec.fieldValues = new Map<String, Object>{
                'Name' => parentName,
                'QuoteId' => '@{refHeader.id}',
                'SortOrder' => sortOrder++
            };
            listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest(refTop, topRec));
            groupRefs.add(refTop);
            List<String> subgroups = new List<String>();
            if (p < subgroupCSVList.size() && String.isNotBlank(subgroupCSVList[p])) {
                for (String s : subgroupCSVList[p].split(',')) {
                    String t = s.trim();
                    if (String.isNotBlank(t)) subgroups.add(t);
                }
            }
            groupsPerParent.add(1 + subgroups.size());
            for (Integer s = 0; s < subgroups.size(); s++) {
                String refNest = 'refNest' + (p + 1) + '_' + (s + 1);
                RevSalesTrxn.RecordResource nestRec = new RevSalesTrxn.RecordResource(QuoteLineGroup.getSObjectType(), 'POST');
                nestRec.fieldValues = new Map<String, Object>{
                    'Name' => subgroups[s],
                    'QuoteId' => '@{refHeader.id}',
                    'ParentQuoteLineGroupId' => '@{' + refTop + '.id}',
                    'SortOrder' => sortOrder++
                };
                listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest(refNest, nestRec));
                groupRefs.add(refNest);
            }
        }

        List<Integer> productCounts = new List<Integer>();
        for (Integer p = 0; p < parentNames.size(); p++) {
            Integer numGroupsForParent = p < groupsPerParent.size() ? groupsPerParent.get(p) : 1;
            String csv = p < countCSVList.size() ? countCSVList[p] : '';
            List<Integer> counts = parseProductCounts(csv, numGroupsForParent);
            productCounts.addAll(counts);
        }

        List<PricebookEntry> pbes = loadDemoRotationPricebookEntries(pricebook2Id);
        if (pbes.isEmpty()) throw new RLM_SetUpQuoteException('No valid price book entries found.');

        Integer lineIndex = 0;
        for (Integer g = 0; g < groupRefs.size(); g++) {
            Integer count = g < productCounts.size() ? productCounts.get(g) : 0;
            if (count == null || count <= 0) continue;
            String groupRef = groupRefs.get(g);
            for (Integer i = 0; i < count; i++) {
                PricebookEntry pbe = pbes.get(Math.mod(i, pbes.size()));
                RevSalesTrxn.RecordResource lineRec = new RevSalesTrxn.RecordResource(QuoteLineItem.getSObjectType(), 'POST');
                lineRec.fieldValues = buildQuoteLineItemFields(pbe, '@{refHeader.id}', '@{' + groupRef + '.id}');
                listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refLine' + lineIndex, lineRec));
                lineIndex++;
            }
        }

        RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('SetUpQuoteInvocable', listOfRecords);
        PstPrefs prefs = resolvePstPrefs(in0);
        RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
            graph,
            prefs.pricingPref,
            RevSalesTrxn.ConfigurationExecutionEnum.FORCE,
            new RevSalesTrxn.ConfigurationOptionsInput(),
            null,
            prefs.catalogRatesPref,
            prefs.taxPref,
            null
        );
        if (resp == null || !resp.isSuccess) {
            throw new RLM_SetUpQuoteException(resp != null && resp.errorResponse != null ? String.valueOf(resp.errorResponse) : 'PST execution failed');
        }
        return isCreate ? resp.salesTransactionId : in0.quoteId;
    }

    private static String run(Input in0) {
        Boolean isCreate = (in0.isCreate == true);
        if (in0.numTopLevel == null) throw new RLM_SetUpQuoteException('Add at least one parent group or provide number of top-level groups.');
        Integer numTop = Math.max(1, Math.min(in0.numTopLevel, MAX_TOP_LEVEL));
        Integer numNested = in0.numNestedPerTop == null ? 0 : Math.max(0, Math.min(in0.numNestedPerTop, MAX_NESTED_PER_TOP));
        Boolean largeDeal = (in0.largeDeal == true);

        List<Integer> productCounts = parseProductCounts(in0.productCountsCSV, numTop * (1 + numNested));

        Id pricebook2Id = getStandardPricebookId();
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords = new List<RevSalesTrxn.RecordWithReferenceRequest>();

        RevSalesTrxn.RecordResource headerRecord;
        if (isCreate) {
            if (String.isBlank(in0.newQuoteName)) throw new RLM_SetUpQuoteException('New quote name required when creating.');
            headerRecord = new RevSalesTrxn.RecordResource(Quote.getSObjectType(), 'POST');
            Map<String, Object> headerFields = buildCreateQuoteHeaderFields(in0, pricebook2Id);
            if (largeDeal) headerFields.put('IsLargeDeal', true);
            headerRecord.fieldValues = headerFields;
        } else {
            if (String.isBlank(in0.quoteId)) throw new RLM_SetUpQuoteException('Quote Id required when modifying.');
            headerRecord = new RevSalesTrxn.RecordResource(Quote.getSObjectType(), 'PATCH', in0.quoteId);
            if (largeDeal) headerRecord.fieldValues = new Map<String, Object>{ 'IsLargeDeal' => true };
        }
        listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refHeader', headerRecord));

        List<String> groupRefs = new List<String>();
        Integer sortOrder = 1;
        for (Integer t = 1; t <= numTop; t++) {
            RevSalesTrxn.RecordResource topRec = new RevSalesTrxn.RecordResource(QuoteLineGroup.getSObjectType(), 'POST');
            topRec.fieldValues = new Map<String, Object>{
                'Name' => 'Group ' + t,
                'QuoteId' => '@{refHeader.id}',
                'SortOrder' => sortOrder++
            };
            String refTop = 'refTop' + t;
            listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest(refTop, topRec));
            groupRefs.add(refTop);
            for (Integer n = 1; n <= numNested; n++) {
                RevSalesTrxn.RecordResource nestRec = new RevSalesTrxn.RecordResource(QuoteLineGroup.getSObjectType(), 'POST');
                nestRec.fieldValues = new Map<String, Object>{
                    'Name' => 'Nested ' + t + '-' + n,
                    'QuoteId' => '@{refHeader.id}',
                    'ParentQuoteLineGroupId' => '@{' + refTop + '.id}',
                    'SortOrder' => sortOrder++
                };
                String refNest = 'refNest' + t + '_' + n;
                listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest(refNest, nestRec));
                groupRefs.add(refNest);
            }
        }

        List<PricebookEntry> pbes = loadDemoRotationPricebookEntries(pricebook2Id);
        if (pbes.isEmpty()) throw new RLM_SetUpQuoteException('No valid price book entries found.');

        Integer lineIndex = 0;
        for (Integer g = 0; g < groupRefs.size(); g++) {
            Integer count = g < productCounts.size() ? productCounts.get(g) : 0;
            if (count == null || count <= 0) continue;
            String groupRef = groupRefs.get(g);
            for (Integer i = 0; i < count; i++) {
                PricebookEntry pbe = pbes.get(Math.mod(i, pbes.size()));
                RevSalesTrxn.RecordResource lineRec = new RevSalesTrxn.RecordResource(QuoteLineItem.getSObjectType(), 'POST');
                lineRec.fieldValues = buildQuoteLineItemFields(pbe, '@{refHeader.id}', '@{' + groupRef + '.id}');
                listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refLine' + lineIndex, lineRec));
                lineIndex++;
            }
        }

        RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('SetUpQuoteInvocable', listOfRecords);
        PstPrefs prefs = resolvePstPrefs(in0);
        RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
            graph,
            prefs.pricingPref,
            RevSalesTrxn.ConfigurationExecutionEnum.FORCE,
            new RevSalesTrxn.ConfigurationOptionsInput(),
            null,
            prefs.catalogRatesPref,
            prefs.taxPref,
            null
        );
        if (resp == null || !resp.isSuccess) {
            throw new RLM_SetUpQuoteException(resp != null && resp.errorResponse != null ? String.valueOf(resp.errorResponse) : 'PST execution failed');
        }
        return isCreate ? resp.salesTransactionId : in0.quoteId;
    }

    private static List<Integer> parseProductCounts(String csv, Integer expectedSize) {
        List<Integer> counts = new List<Integer>();
        if (expectedSize == null || expectedSize <= 0) return counts;
        if (String.isNotBlank(csv)) {
            for (String s : csv.split(',')) {
                s = s.trim();
                if (String.isBlank(s)) counts.add(0);
                else {
                    try { counts.add(Integer.valueOf(s)); } catch (Exception e) { counts.add(0); }
                }
            }
        }
        while (counts.size() < expectedSize) counts.add(0);
        return counts;
    }

    /** All group paths in hierarchy JSON (same path rules as PST group creation). Used for CSV import preview. */
    public static void collectHierarchyPathsIntoSet(String hierarchyJson, Set<String> pathsOut) {
        if (String.isBlank(hierarchyJson) || pathsOut == null) {
            return;
        }
        try {
            Map<String, Object> treeMap = (Map<String, Object>) JSON.deserializeUntyped(hierarchyJson);
            List<Object> parentsList = (List<Object>) treeMap.get('parents');
            if (parentsList == null) {
                return;
            }
            for (Integer pi = 0; pi < parentsList.size(); pi++) {
                Map<String, Object> parentNode = (Map<String, Object>) parentsList.get(pi);
                String path = parentNode.containsKey('path') ? String.valueOf(parentNode.get('path')) : String.valueOf(pi);
                pathsOut.add(path);
                List<Object> children = (List<Object>) parentNode.get('children');
                if (children != null && !children.isEmpty()) {
                    collectHierarchyChildPaths(children, path, pathsOut);
                }
            }
        } catch (Exception e) {
            /* ignore */
        }
    }

    private static void collectHierarchyChildPaths(List<Object> children, String parentPath, Set<String> pathsOut) {
        for (Integer ci = 0; ci < children.size(); ci++) {
            Map<String, Object> node = (Map<String, Object>) children.get(ci);
            String path = node.containsKey('path')
                ? String.valueOf(node.get('path'))
                : (parentPath != '' ? parentPath + '-' + ci : String.valueOf(ci));
            pathsOut.add(path);
            List<Object> sub = (List<Object>) node.get('children');
            if (sub != null && !sub.isEmpty()) {
                collectHierarchyChildPaths(sub, path, pathsOut);
            }
        }
    }

    /**
     * Counts the QuoteLineItems a CSV import will produce, mirroring the exact rules of
     * addLineItemsFromCsvImport so the preview total matches the actual import:
     *   - A row with no productIdentifier, or one that does not resolve to a PricebookEntry, is not counted.
     *   - A row whose path is non-blank but does NOT match any hierarchy path is skipped
     *     (in the import its group ref resolves blank and the row is dropped).
     *   - A row with a blank/missing path IS counted: the import adds it as an ungrouped
     *     line on the quote, so excluding it here would undercount the projection.
     * Each surviving row counts as one QuoteLineItem (quantity lives on the line, not as extra rows).
     */
    public static Integer countCsvImportLinesForPreview(String hierarchyJson, String csvImportLineItemsJson) {
        Set<String> validPaths = new Set<String>();
        collectHierarchyPathsIntoSet(hierarchyJson, validPaths);
        Boolean ungroupedCsvOnly = validPaths.isEmpty();
        if (String.isBlank(csvImportLineItemsJson)) {
            return 0;
        }
        List<Object> items;
        try {
            items = (List<Object>) JSON.deserializeUntyped(csvImportLineItemsJson);
        } catch (Exception e) {
            return 0;
        }
        if (items == null || items.isEmpty()) {
            return 0;
        }
        List<String> allIdentifiers = new List<String>();
        for (Object itemObj : items) {
            Map<String, Object> item = (Map<String, Object>) itemObj;
            String productIdentifier = item != null && item.containsKey('productIdentifier')
                ? String.valueOf(item.get('productIdentifier'))
                : null;
            if (String.isNotBlank(productIdentifier)) {
                allIdentifiers.add(productIdentifier.trim());
            }
        }
        Id pricebook2Id = getStandardPricebookId();
        Map<String, PricebookEntry> pbeMap = RLM_ProductCatalogPbeService.resolveProductsToPBEMap(allIdentifiers, pricebook2Id);
        Integer linesAdded = 0;
        for (Object itemObj : items) {
            Map<String, Object> item = (Map<String, Object>) itemObj;
            String path = item != null && item.containsKey('path') && item.get('path') != null ? String.valueOf(item.get('path')) : null;
            String productIdentifier = item != null && item.containsKey('productIdentifier')
                ? String.valueOf(item.get('productIdentifier'))
                : null;
            if (String.isBlank(productIdentifier)) {
                continue;
            }
            // Mirror addLineItemsFromCsvImport: a non-blank path that does not match any
            // hierarchy group is dropped; a blank/missing path falls through and is counted
            // as an ungrouped line (the import adds it ungrouped on the quote).
            if (!ungroupedCsvOnly && String.isNotBlank(path)) {
                if (!validPaths.contains(path)) {
                    continue;
                }
            }
            String trimmed = productIdentifier.trim();
            PricebookEntry pbe = pbeMap.get(trimmed);
            if (pbe == null && trimmed.contains(',')) {
                String prefix = trimmed.substring(0, trimmed.lastIndexOf(',')).trim();
                if (String.isNotBlank(prefix)) {
                    pbe = pbeMap.get(prefix);
                }
            }
            if (pbe == null) {
                continue;
            }
            linesAdded++;
        }
        return linesAdded;
    }

    /** Sum of integer values in productCountsJson map (demo line count per path). */
    public static Integer sumProductCountsJsonValues(String productCountsJson) {
        if (String.isBlank(productCountsJson)) {
            return 0;
        }
        Integer sum = 0;
        try {
            Map<String, Object> countsObj = (Map<String, Object>) JSON.deserializeUntyped(productCountsJson);
            for (String k : countsObj.keySet()) {
                Object v = countsObj.get(k);
                Integer count = null;
                if (v instanceof Integer) {
                    count = (Integer) v;
                } else if (v instanceof Decimal) {
                    count = ((Decimal) v).intValue();
                } else if (v instanceof Long) {
                    count = ((Long) v).intValue();
                } else if (v instanceof Double) {
                    count = ((Double) v).intValue();
                } else if (v != null) {
                    count = Integer.valueOf(String.valueOf(v));
                }
                if (count != null && count > 0) {
                    sum += count;
                }
            }
        } catch (Exception e) {
            /* ignore */
        }
        return sum;
    }

    public class RLM_SetUpQuoteException extends Exception {}
}
