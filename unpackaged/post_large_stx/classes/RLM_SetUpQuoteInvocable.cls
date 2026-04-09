/**
 * Invocable for "Set Up Quote" flow: create or modify quote, set Large Deal,
 * create top-level + nested groups (max 5 levels), add products per group (DemoInvocableAction product set).
 */
public with sharing class RLM_SetUpQuoteInvocable {

    /**
     * Resolves demo PricebookEntries dynamically from the Standard Pricebook
     * by ProductSellingModel type (OneTime, Evergreen, TermDefined), ordered
     * so callers can cycle through all selling-model varieties via Math.mod.
     * Returns up to 20 active PBEs — portable across scratch orgs and sandboxes.
     */
    @TestVisible
    private static List<PricebookEntry> loadDemoPricebookEntries() {
        return [
            SELECT Id, Product2Id, UnitPrice,
                   ProductSellingModel.SellingModelType,
                   ProductSellingModel.PricingTermUnit
            FROM PricebookEntry
            WHERE Pricebook2.IsStandard = true
              AND IsActive = true
              AND ProductSellingModelId != null
            ORDER BY ProductSellingModel.SellingModelType NULLS LAST
            LIMIT 20
        ];
    }
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
        @InvocableVariable(label='Hierarchy JSON (from LWC: { parents: [ { name, path, children: [...] } ] })')
        public String hierarchyJson;
        @InvocableVariable(label='Product counts JSON (from LWC: { "0": 2, "0-0": 1, ... })')
        public String productCountsJson;
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

    /**
     * Returns a list of quotes for the Modify flow: Id, Name, QuoteNumber, IsLargeDeal.
     * Used by Set Up Quote wizard to show a dropdown and to hide the Large Deal step when the selected quote already has Large Deal set.
     */
    @AuraEnabled(cacheable=true)
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

    private static void applyExistingGroupCounts(String quoteId, String existingGroupCountsJson, Map<String, Id> tempIdToNewGroupId) {
        if (String.isBlank(quoteId) || String.isBlank(existingGroupCountsJson)) return;
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(existingGroupCountsJson);
        Map<Id, Integer> groupIdToCount = new Map<Id, Integer>();
        for (String k : m.keySet()) {
            Object v = m.get(k);
            Integer count = null;
            if (v instanceof Integer) count = (Integer) v;
            else if (v instanceof Decimal) count = ((Decimal) v).intValue();
            else if (v instanceof Long) count = ((Long) v).intValue();
            else if (v instanceof Double) count = ((Double) v).intValue();
            else if (v != null) count = Integer.valueOf(String.valueOf(v));
            if (count == null || count < 0) count = 0;
            Id gid = null;
            if (tempIdToNewGroupId != null && tempIdToNewGroupId.containsKey(k)) gid = tempIdToNewGroupId.get(k);
            else try { gid = Id.valueOf(k); } catch (Exception e) { continue; }
            groupIdToCount.put(gid, count);
        }
        if (groupIdToCount.isEmpty()) return;
        List<PricebookEntry> pbes = loadDemoPricebookEntries();
        if (pbes.isEmpty()) return;
        Id qId = Id.valueOf(quoteId);
        // Ownership guard: discard any group Ids that don't belong to this quote
        Set<Id> requestedGroupIds = new Set<Id>(groupIdToCount.keySet());
        Set<Id> validGroupIds = new Set<Id>();
        for (QuoteLineGroup qlg : [SELECT Id FROM QuoteLineGroup WHERE QuoteId = :qId AND Id IN :requestedGroupIds]) {
            validGroupIds.add(qlg.Id);
        }
        for (Id gid : new List<Id>(groupIdToCount.keySet())) {
            if (!validGroupIds.contains(gid)) groupIdToCount.remove(gid);
        }
        if (groupIdToCount.isEmpty()) return;
        List<Id> groupIds = new List<Id>(groupIdToCount.keySet());
        // Bulkify: one SOQL for all line items in these groups, scoped to this quote
        List<QuoteLineItem> existingItems = [SELECT Id, QuoteLineGroupId FROM QuoteLineItem WHERE QuoteId = :qId AND QuoteLineGroupId IN :groupIds];
        Map<Id, List<QuoteLineItem>> groupIdToItems = new Map<Id, List<QuoteLineItem>>();
        for (Id gid : groupIds) groupIdToItems.put(gid, new List<QuoteLineItem>());
        for (QuoteLineItem it : existingItems) {
            if (groupIdToItems.containsKey(it.QuoteLineGroupId)) groupIdToItems.get(it.QuoteLineGroupId).add(it);
        }
        for (Id gid : groupIds) {
            Integer count = groupIdToCount.get(gid);
            List<QuoteLineItem> existing = groupIdToItems.get(gid);
            if (existing != null && !existing.isEmpty()) delete existing;
            if (count <= 0) continue;
            List<QuoteLineItem> newItems = new List<QuoteLineItem>();
            for (Integer i = 0; i < count; i++) {
                PricebookEntry pbe = pbes.get(Math.mod(i, pbes.size()));
                QuoteLineItem li = new QuoteLineItem(QuoteId = qId, QuoteLineGroupId = gid, Product2Id = pbe.Product2Id, PricebookEntryId = pbe.Id, Quantity = 1, UnitPrice = pbe.UnitPrice != null ? pbe.UnitPrice : 0);
                if (pbe.ProductSellingModel != null) {
                    String st = String.valueOf(pbe.ProductSellingModel.SellingModelType);
                    String ptu = String.valueOf(pbe.ProductSellingModel.PricingTermUnit);
                    String bf = PRICING_TERM_TO_BILLING_FREQUENCY.get(ptu);
                    if ('TermDefined' == st && String.isNotBlank(bf)) {
                        li.StartDate = Date.newInstance(2025, 9, 4);
                        li.EndDate = Date.newInstance(2026, 9, 9);
                        li.PeriodBoundary = 'Anniversary';
                        li.BillingFrequency = bf;
                    } else if ('Evergreen' == st && String.isNotBlank(bf)) {
                        li.StartDate = Date.newInstance(2025, 9, 4);
                        li.PeriodBoundary = 'Anniversary';
                        li.BillingFrequency = bf;
                    }
                }
                newItems.add(li);
            }
            if (!newItems.isEmpty()) insert newItems;
        }
    }

    private static Map<String, Object> buildFlowInputMap(Input in0) {
        Map<String, Object> inputMap = new Map<String, Object>();
        inputMap.put('var_IsCreate', in0.isCreate == true);
        inputMap.put('var_QuoteId', String.isBlank(in0.quoteId) ? null : in0.quoteId);
        inputMap.put('var_NewQuoteName', String.isBlank(in0.newQuoteName) ? null : in0.newQuoteName);
        inputMap.put('var_LargeDeal', in0.largeDeal == true);
        inputMap.put('var_HierarchyJson', String.isBlank(in0.hierarchyJson) ? null : in0.hierarchyJson);
        inputMap.put('var_ProductCountsJson', String.isBlank(in0.productCountsJson) ? null : in0.productCountsJson);
        inputMap.put('var_CsvImportLineItemsJson', String.isBlank(in0.csvImportLineItemsJson) ? null : in0.csvImportLineItemsJson);
        inputMap.put('var_GroupsToDeleteJson', String.isBlank(in0.groupsToDeleteJson) ? null : in0.groupsToDeleteJson);
        inputMap.put('var_GroupRenamesJson', String.isBlank(in0.groupRenamesJson) ? null : in0.groupRenamesJson);
        inputMap.put('var_NewSubgroupsJson', String.isBlank(in0.newSubgroupsJson) ? null : in0.newSubgroupsJson);
        inputMap.put('var_ExistingGroupCountsJson', String.isBlank(in0.existingGroupCountsJson) ? null : in0.existingGroupCountsJson);
        inputMap.put('var_RepeatBuyAssignmentsJson', String.isBlank(in0.repeatBuyAssignmentsJson) ? null : in0.repeatBuyAssignmentsJson);
        inputMap.put('var_RepeatBuyAccountId', String.isBlank(in0.repeatBuyAccountId) ? null : in0.repeatBuyAccountId);
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
        in0.csvImportLineItemsJson = (String) m.get('csvImportLineItemsJson');
        in0.groupsToDeleteJson = (String) m.get('groupsToDeleteJson');
        in0.groupRenamesJson = (String) m.get('groupRenamesJson');
        in0.newSubgroupsJson = (String) m.get('newSubgroupsJson');
        in0.existingGroupCountsJson = (String) m.get('existingGroupCountsJson');
        in0.repeatBuyAssignmentsJson = (String) m.get('repeatBuyAssignmentsJson');
        in0.repeatBuyAccountId = (String) m.get('repeatBuyAccountId');
        in0.parentGroupNames = listOfStrings(m.get('parentGroupNames'));
        in0.subgroupNamesPerParent = listOfStrings(m.get('subgroupNamesPerParent'));
        in0.productCountsPerParent = listOfStrings(m.get('productCountsPerParent'));
        Object nt = m.get('numTopLevel');
        in0.numTopLevel = nt != null ? Integer.valueOf(nt) : null;
        Object nn = m.get('numNestedPerTop');
        in0.numNestedPerTop = nn != null ? Integer.valueOf(nn) : null;
        in0.productCountsCSV = (String) m.get('productCountsCSV');
        in0.skipConfiguration = m.get('skipConfiguration') == true;
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
        if (Test.isRunningTest()) return Test.getStandardPricebookId();
        List<Pricebook2> pbs = [SELECT Id FROM Pricebook2 WHERE IsStandard = true LIMIT 1];
        if (pbs.isEmpty()) throw new RLM_SetUpQuoteException('Standard Price Book not found.');
        return pbs[0].Id;
    }

    private static Map<String, Object> buildCreateQuoteHeaderFields(Input in0, Id pricebook2Id) {
        Map<String, Object> out = new Map<String, Object>{
            'Name' => in0.newQuoteName,
            'Pricebook2Id' => pricebook2Id
        };
        if (String.isNotBlank(in0.repeatBuyAccountId)) {
            out.put('QuoteAccountId', in0.repeatBuyAccountId);
        }
        return out;
    }

    private static String runFromHierarchyJson(Input in0, List<Integer> csvLinesAddedOut) {
        if (String.isBlank(in0.hierarchyJson)) throw new RLM_SetUpQuoteException('Hierarchy JSON is required.');
        if (csvLinesAddedOut == null) csvLinesAddedOut = new List<Integer>();
        Boolean isCreate = (in0.isCreate == true);
        Boolean largeDeal = (in0.largeDeal == true);
        if (!isCreate && String.isNotBlank(in0.groupsToDeleteJson)) deleteQuoteLineGroups(in0.quoteId, in0.groupsToDeleteJson);
        if (!isCreate) applyGroupRenames(in0.quoteId, in0.groupRenamesJson);
        Map<String, Id> tempIdToNewGroupId = new Map<String, Id>();
        if (!isCreate && String.isNotBlank(in0.newSubgroupsJson)) tempIdToNewGroupId = createNewSubgroupsUnderExisting(in0.quoteId, in0.newSubgroupsJson);
        if (!isCreate && String.isNotBlank(in0.existingGroupCountsJson)) applyExistingGroupCounts(in0.quoteId, in0.existingGroupCountsJson, tempIdToNewGroupId);
        Map<String, Object> treeMap = (Map<String, Object>) JSON.deserializeUntyped(in0.hierarchyJson);
        List<Object> parentsList = (List<Object>) treeMap.get('parents');
        if (parentsList == null) parentsList = new List<Object>();
        // Allow create with empty hierarchy (no groups) for 2-step flow: Step 1 = empty quote + large deal.
        if (parentsList.isEmpty()) {
            if (isCreate) {
                if (String.isBlank(in0.newQuoteName)) throw new RLM_SetUpQuoteException('New quote name required when creating.');
                Id pricebook2Id = getStandardPricebookId();
                RevSalesTrxn.RecordResource headerRecord = new RevSalesTrxn.RecordResource(Quote.getSObjectType(), 'POST');
                headerRecord.fieldValues = buildCreateQuoteHeaderFields(in0, pricebook2Id);
                List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords = new List<RevSalesTrxn.RecordWithReferenceRequest>{
                    new RevSalesTrxn.RecordWithReferenceRequest('refHeader', headerRecord)
                };
                RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('SetUpQuoteInvocable', listOfRecords);
                RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
                    graph, RevSalesTrxn.PricingPreferenceEnum.SKIP, RevSalesTrxn.ConfigurationExecutionEnum.SKIP,
                    new RevSalesTrxn.ConfigurationOptionsInput(), null, null, RevSalesTrxn.TaxPreferenceEnum.SKIP, null);
                if (resp == null || !resp.isSuccess) throw new RLM_SetUpQuoteException(resp != null && resp.errorResponse != null ? String.valueOf(resp.errorResponse) : 'PST execution failed');
                Id quoteId = (Id) resp.salesTransactionId;
                if (largeDeal) update new Quote(Id = quoteId, IsLargeDeal = true);
                return quoteId;
            } else {
                if (largeDeal && String.isNotBlank(in0.quoteId)) {
                    try {
                        update new Quote(Id = Id.valueOf(in0.quoteId), IsLargeDeal = true);
                    } catch (Exception e) { /* invalid Id — skip large deal flag */ }
                }
                return in0.quoteId;
            }
        }
        Boolean useCsvImport = String.isNotBlank(in0.csvImportLineItemsJson);
        Map<String, Integer> countsMap = new Map<String, Integer>();
        if (!useCsvImport && String.isNotBlank(in0.productCountsJson)) {
            try {
                Map<String, Object> countsObj = (Map<String, Object>) JSON.deserializeUntyped(in0.productCountsJson);
                for (String k : countsObj.keySet()) {
                    Object v = countsObj.get(k);
                    Integer count = null;
                    if (v instanceof Integer) count = (Integer) v;
                    else if (v instanceof Decimal) count = ((Decimal) v).intValue();
                    else if (v instanceof Long) count = ((Long) v).intValue();
                    else if (v instanceof Double) count = ((Double) v).intValue();
                    else if (v != null) count = Integer.valueOf(String.valueOf(v));
                    if (count != null) countsMap.put(k, count);
                }
            } catch (Exception e) { /* ignore */ }
        }
        Id pricebook2Id = getStandardPricebookId();
        Boolean createViaPost = isCreate;
        String targetQuoteId = in0.quoteId;
        if (isCreate && largeDeal) {
            // Create the quote shell first, mark IsLargeDeal via DML, then run PST for groups/lines as PATCH.
            // This preserves "large deal on create" behavior while avoiding PST header-path endpoint issues.
            RevSalesTrxn.RecordResource preHeader = new RevSalesTrxn.RecordResource(Quote.getSObjectType(), 'POST');
            preHeader.fieldValues = buildCreateQuoteHeaderFields(in0, pricebook2Id);
            List<RevSalesTrxn.RecordWithReferenceRequest> preRecords = new List<RevSalesTrxn.RecordWithReferenceRequest>{
                new RevSalesTrxn.RecordWithReferenceRequest('refHeader', preHeader)
            };
            RevSalesTrxn.GraphRequest preGraph = new RevSalesTrxn.GraphRequest('SetUpQuoteInvocable_PreCreate', preRecords);
            RevSalesTrxn.PlaceSalesTransactionResponse preResp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
                preGraph,
                RevSalesTrxn.PricingPreferenceEnum.SKIP,
                RevSalesTrxn.ConfigurationExecutionEnum.SKIP,
                new RevSalesTrxn.ConfigurationOptionsInput(),
                null,
                null,
                RevSalesTrxn.TaxPreferenceEnum.SKIP,
                null
            );
            if (preResp == null || !preResp.isSuccess) {
                throw new RLM_SetUpQuoteException(
                    preResp != null && preResp.errorResponse != null
                        ? String.valueOf(preResp.errorResponse)
                        : 'PST pre-create execution failed'
                );
            }
            targetQuoteId = String.valueOf(preResp.salesTransactionId);
            update new Quote(Id = Id.valueOf(targetQuoteId), IsLargeDeal = true);
            createViaPost = false;
        }
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords = new List<RevSalesTrxn.RecordWithReferenceRequest>();
        RevSalesTrxn.RecordResource headerRecord;
        if (createViaPost) {
            if (String.isBlank(in0.newQuoteName)) throw new RLM_SetUpQuoteException('New quote name required when creating.');
            headerRecord = new RevSalesTrxn.RecordResource(Quote.getSObjectType(), 'POST');
            headerRecord.fieldValues = buildCreateQuoteHeaderFields(in0, pricebook2Id);
        } else {
            if (String.isBlank(targetQuoteId)) throw new RLM_SetUpQuoteException('Quote Id required when modifying.');
            headerRecord = new RevSalesTrxn.RecordResource(Quote.getSObjectType(), 'PATCH', targetQuoteId);
            headerRecord.fieldValues = new Map<String, Object>();
        }
        // Always add quote to graph so PST has a root and processes children. When modifying, use literal quoteId on groups/lines so they attach to existing quote (not a new one).
        listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refHeader', headerRecord));
        String quoteIdRef = createViaPost ? '@{refHeader.id}' : String.valueOf(targetQuoteId);
        List<PricebookEntry> pbes = new List<PricebookEntry>();
        if (!useCsvImport && !countsMap.isEmpty()) {
            pbes = loadDemoPricebookEntries();
            if (pbes.isEmpty()) throw new RLM_SetUpQuoteException('No valid price book entries found.');
        }
        Map<String, String> pathToGroupRef = new Map<String, String>();
        List<String> groupRefs = new List<String>();
        Integer sortOrder = 1;
        Integer refIdx = 0;
        List<Integer> lineIndexHolder = new List<Integer>{ 0 };
        Map<String, Integer> countsForGroups = useCsvImport ? new Map<String, Integer>() : countsMap;
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
            addLineItemsForGroup(path, refName, countsForGroups, listOfRecords, pbes, lineIndexHolder, quoteIdRef);
            List<Object> children = (List<Object>) parentNode.get('children');
            if (children != null && !children.isEmpty()) {
                sortOrder = addChildGroups(children, refName, listOfRecords, groupRefs, refIdx, sortOrder, path, countsForGroups, pbes, lineIndexHolder, pathToGroupRef, quoteIdRef);
                refIdx = groupRefs.size();
            }
        }
        Integer linesAdded = 0;
        if (useCsvImport) {
            linesAdded = addLineItemsFromCsvImport(in0.csvImportLineItemsJson, pathToGroupRef, listOfRecords, pricebook2Id, lineIndexHolder, quoteIdRef);
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
        Boolean hasLineItems = useCsvImport ? (linesAdded != null && linesAdded > 0) : !countsMap.isEmpty();
        // Default (skipConfiguration not set): FORCE when line items present — same as before 2-step/skipConfiguration. CSV import path unchanged.
        RevSalesTrxn.ConfigurationExecutionEnum configEnum = (in0.skipConfiguration == true)
            ? RevSalesTrxn.ConfigurationExecutionEnum.SKIP
            : (hasLineItems ? RevSalesTrxn.ConfigurationExecutionEnum.FORCE : RevSalesTrxn.ConfigurationExecutionEnum.SKIP);
        RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('SetUpQuoteInvocable', listOfRecords);
        RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
            graph, RevSalesTrxn.PricingPreferenceEnum.SKIP, configEnum,
            new RevSalesTrxn.ConfigurationOptionsInput(), null, null, RevSalesTrxn.TaxPreferenceEnum.SKIP, null);
        if (resp == null || !resp.isSuccess) throw new RLM_SetUpQuoteException(resp != null && resp.errorResponse != null ? String.valueOf(resp.errorResponse) : 'PST execution failed');
        Id quoteId = createViaPost ? (Id) resp.salesTransactionId : Id.valueOf(targetQuoteId);
        if (largeDeal) {
            update new Quote(Id = quoteId, IsLargeDeal = true);
        }
        return quoteId;
    }

    private static void addLineItemsForGroup(String path, String groupRef, Map<String, Integer> countsMap, List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords, List<PricebookEntry> pbes, List<Integer> lineIndexHolder, String quoteIdRef) {
        Integer count = countsMap.containsKey(path) ? countsMap.get(path) : 0;
        if (count == null || count <= 0) return;
        Integer lineIndex = lineIndexHolder[0];
        for (Integer i = 0; i < count; i++) {
            PricebookEntry pbe = pbes.get(Math.mod(i, pbes.size()));
            RevSalesTrxn.RecordResource lineRec = new RevSalesTrxn.RecordResource(QuoteLineItem.getSObjectType(), 'POST');
            lineRec.fieldValues = buildQuoteLineItemFields(pbe, quoteIdRef, '@{' + groupRef + '.id}');
            listOfRecords.add(new RevSalesTrxn.RecordWithReferenceRequest('refLine' + lineIndex, lineRec));
            lineIndex++;
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
            'QuoteLineGroupId' => quoteLineGroupIdRef,
            'Product2Id' => pbe.Product2Id,
            'PricebookEntryId' => pbe.Id,
            'Quantity' => (quantity != null && quantity > 0) ? quantity : 1, // rule: no/zero quantity → 1
            'UnitPrice' => unitPrice
        };
        if ('TermDefined' == sellingModelType && String.isNotBlank(billingFrequency)) {
            fields.put('StartDate', '2025-09-04T00:00:00.000Z');
            fields.put('EndDate', '2026-09-09T00:00:00.000Z');
            fields.put('PeriodBoundary', 'Anniversary');
            fields.put('BillingFrequency', billingFrequency);
        } else if ('Evergreen' == sellingModelType && String.isNotBlank(billingFrequency)) {
            fields.put('StartDate', '2025-09-04T00:00:00.000Z');
            fields.put('PeriodBoundary', 'Anniversary');
            fields.put('BillingFrequency', billingFrequency);
        }
        return fields;
    }

    /** Resolve product identifier (code or name) to a PricebookEntry for the given price book. Tries ProductCode first, then Name. PBE order: OneTime → Evergreen → TermDefined. If not found and identifier contains a comma, retries with the part before the last comma. Returns null if not found. Used for single-item resolution (e.g. productCounts path). */
    private static PricebookEntry resolveProductToPBE(String productIdentifier, Id pricebook2Id) {
        if (String.isBlank(productIdentifier) || pricebook2Id == null) return null;
        List<String> ids = new List<String>{ productIdentifier.trim() };
        Map<String, PricebookEntry> m = resolveProductsToPBEMap(ids, pricebook2Id);
        String trimmed = productIdentifier.trim();
        PricebookEntry pbe = m.get(trimmed);
        if (pbe != null) return pbe;
        if (trimmed.contains(',')) {
            String prefix = trimmed.substring(0, trimmed.lastIndexOf(',')).trim();
            if (String.isNotBlank(prefix)) pbe = m.get(prefix);
        }
        return pbe;
    }

    /** Bulk resolve: run SOQL once per batch. Returns map identifier -> PBE (ProductCode wins over Name; PBE order OneTime → Evergreen → TermDefined). */
    private static Map<String, PricebookEntry> resolveProductsToPBEMap(List<String> identifiers, Id pricebook2Id) {
        Map<String, PricebookEntry> result = new Map<String, PricebookEntry>();
        if (identifiers == null || identifiers.isEmpty() || pricebook2Id == null) return result;
        Set<String> idSet = new Set<String>();
        for (String s : identifiers) {
            if (String.isNotBlank(s)) {
                idSet.add(s.trim());
                if (s.contains(',')) {
                    String prefix = s.substring(0, s.lastIndexOf(',')).trim();
                    if (String.isNotBlank(prefix)) idSet.add(prefix);
                }
            }
        }
        if (idSet.isEmpty()) return result;
        List<String> idList = new List<String>(idSet);
        Map<Id, Product2> byCode = new Map<Id, Product2>();
        Map<Id, Product2> byName = new Map<Id, Product2>();
        List<Product2> byCodeList = [SELECT Id, ProductCode, Name FROM Product2 WHERE ProductCode IN :idList AND IsActive = true];
        for (Product2 p : byCodeList) byCode.put(p.Id, p);
        List<Product2> byNameList = [SELECT Id, ProductCode, Name FROM Product2 WHERE Name IN :idList AND IsActive = true];
        for (Product2 p : byNameList) byName.put(p.Id, p);
        Set<Id> product2Ids = new Set<Id>();
        product2Ids.addAll(byCode.keySet());
        product2Ids.addAll(byName.keySet());
        if (product2Ids.isEmpty()) return result;
        List<PricebookEntry> pbes = [SELECT Id, Product2Id, UnitPrice, ProductSellingModel.SellingModelType, ProductSellingModel.PricingTermUnit FROM PricebookEntry WHERE Product2Id IN :product2Ids AND Pricebook2Id = :pricebook2Id AND IsActive = true];
        Map<Id, List<PricebookEntry>> pbeByProduct = new Map<Id, List<PricebookEntry>>();
        Map<String, Integer> orderMap = new Map<String, Integer>{ 'OneTime' => 1, 'Evergreen' => 2, 'TermDefined' => 3 };
        for (PricebookEntry pe : pbes) {
            if (!pbeByProduct.containsKey(pe.Product2Id)) pbeByProduct.put(pe.Product2Id, new List<PricebookEntry>());
            pbeByProduct.get(pe.Product2Id).add(pe);
        }
        for (String iden : idList) {
            Id product2Id = null;
            for (Product2 p : byCodeList) { if (p.ProductCode == iden) { product2Id = p.Id; break; } }
            if (product2Id == null) { for (Product2 p : byNameList) { if (p.Name == iden) { product2Id = p.Id; break; } } }
            if (product2Id == null) continue;
            List<PricebookEntry> listPbe = pbeByProduct.get(product2Id);
            if (listPbe == null || listPbe.isEmpty()) continue;
            PricebookEntry chosen = listPbe[0];
            Integer chosenOrder = orderMap.containsKey(String.valueOf(chosen.ProductSellingModel != null ? chosen.ProductSellingModel.SellingModelType : null)) ? orderMap.get(String.valueOf(chosen.ProductSellingModel.SellingModelType)) : 99;
            for (Integer i = 1; i < listPbe.size(); i++) {
                String st = listPbe[i].ProductSellingModel != null ? String.valueOf(listPbe[i].ProductSellingModel.SellingModelType) : null;
                Integer o = orderMap.containsKey(st) ? orderMap.get(st) : 99;
                if (o < chosenOrder) { chosen = listPbe[i]; chosenOrder = o; }
            }
            result.put(iden, chosen);
        }
        return result;
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
        Map<String, PricebookEntry> pbeMap = resolveProductsToPBEMap(allIdentifiers, pricebook2Id);
        Integer lineIndex = lineIndexHolder[0];
        Integer linesAdded = 0;
        for (Object itemObj : items) {
            Map<String, Object> item = (Map<String, Object>) itemObj;
            String path = item != null && item.containsKey('path') ? String.valueOf(item.get('path')) : null;
            String productIdentifier = item != null && item.containsKey('productIdentifier') ? String.valueOf(item.get('productIdentifier')) : null;
            Object qtyObj = (item != null && item.containsKey('quantity')) ? item.get('quantity') : null;
            // Rule: if no quantity is provided, treat quantity as 1
            Decimal qty = (qtyObj instanceof Integer) ? (Integer) qtyObj : (qtyObj instanceof Decimal) ? (Decimal) qtyObj : (qtyObj != null && String.isNotBlank(String.valueOf(qtyObj))) ? Decimal.valueOf(String.valueOf(qtyObj)) : 1;
            if (String.isBlank(path) || String.isBlank(productIdentifier)) continue;
            String groupRef = pathToGroupRef.get(path);
            if (String.isBlank(groupRef)) continue;
            String trimmed = productIdentifier.trim();
            PricebookEntry pbe = pbeMap.get(trimmed);
            if (pbe == null && trimmed.contains(',')) {
                String prefix = trimmed.substring(0, trimmed.lastIndexOf(',')).trim();
                if (String.isNotBlank(prefix)) pbe = pbeMap.get(prefix);
            }
            if (pbe == null) continue;
            RevSalesTrxn.RecordResource lineRec = new RevSalesTrxn.RecordResource(QuoteLineItem.getSObjectType(), 'POST');
            lineRec.fieldValues = buildQuoteLineItemFields(pbe, quoteIdRef, '@{' + groupRef + '.id}', qty);
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
        Map<String, PricebookEntry> pbeMap = resolveProductsToPBEMap(ids, pricebook2Id);
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
            ' FROM QuoteLineItem WHERE QuoteId IN :quoteIds ORDER BY QuoteId, QuoteLineGroup.Name, CreatedDate';
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

    private static Integer addChildGroups(List<Object> children, String parentRef, List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords, List<String> groupRefs, Integer refIdx, Integer sortOrder, String parentPath, Map<String, Integer> countsMap, List<PricebookEntry> pbes, List<Integer> lineIndexHolder, Map<String, String> pathToGroupRef, String quoteIdRef) {
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
            addLineItemsForGroup(path, refName, countsMap, listOfRecords, pbes, lineIndexHolder, quoteIdRef);
            List<Object> sub = (List<Object>) node.get('children');
            if (sub != null && !sub.isEmpty()) sortOrder = addChildGroups(sub, refName, listOfRecords, groupRefs, refIdx, sortOrder, path, countsMap, pbes, lineIndexHolder, pathToGroupRef, quoteIdRef);
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

        List<PricebookEntry> pbes = loadDemoPricebookEntries();
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
        RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
            graph,
            RevSalesTrxn.PricingPreferenceEnum.SKIP,
            RevSalesTrxn.ConfigurationExecutionEnum.FORCE,
            new RevSalesTrxn.ConfigurationOptionsInput(),
            null,
            null,
            RevSalesTrxn.TaxPreferenceEnum.SKIP,
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

        List<PricebookEntry> pbes = loadDemoPricebookEntries();
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
        RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
            graph,
            RevSalesTrxn.PricingPreferenceEnum.SKIP,
            RevSalesTrxn.ConfigurationExecutionEnum.FORCE,
            new RevSalesTrxn.ConfigurationOptionsInput(),
            null,
            null,
            RevSalesTrxn.TaxPreferenceEnum.SKIP,
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
     * Rows in CSV that match a hierarchy path and resolve to a PricebookEntry (same rules as addLineItemsFromCsvImport).
     * Each row counts as one QuoteLineItem record (quantity is on the line, not extra rows).
     */
    public static Integer countCsvImportLinesForPreview(String hierarchyJson, String csvImportLineItemsJson) {
        Set<String> validPaths = new Set<String>();
        collectHierarchyPathsIntoSet(hierarchyJson, validPaths);
        if (validPaths.isEmpty() || String.isBlank(csvImportLineItemsJson)) {
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
        Map<String, PricebookEntry> pbeMap = resolveProductsToPBEMap(allIdentifiers, pricebook2Id);
        Integer linesAdded = 0;
        for (Object itemObj : items) {
            Map<String, Object> item = (Map<String, Object>) itemObj;
            String path = item != null && item.containsKey('path') ? String.valueOf(item.get('path')) : null;
            String productIdentifier = item != null && item.containsKey('productIdentifier')
                ? String.valueOf(item.get('productIdentifier'))
                : null;
            if (String.isBlank(path) || String.isBlank(productIdentifier)) {
                continue;
            }
            if (!validPaths.contains(path)) {
                continue;
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