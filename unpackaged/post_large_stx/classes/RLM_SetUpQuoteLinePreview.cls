/**
 * Estimates QuoteLineItem row count before Run (wizard preview on product-count and confirm steps).
 * Mirrors SetUpQuoteInvocable modify order: deletes → net from existingGroupCounts → new hierarchy lines.
 */
public with sharing class RLM_SetUpQuoteLinePreview {
    @AuraEnabled(cacheable = false)
    public static String previewQuoteLineCounts(String previewJson) {
        if (String.isBlank(previewJson)) {
            return buildResponse(0, 0, 0, 0, 0, null);
        }
        Map<String, Object> m;
        try {
            m = (Map<String, Object>) JSON.deserializeUntyped(previewJson);
        } catch (Exception e) {
            return buildResponse(0, 0, 0, 0, 0, 'Invalid preview JSON');
        }
        Boolean isCreate = m.get('isCreate') == true;
        String quoteIdStr = m.get('quoteId') != null ? String.valueOf(m.get('quoteId')) : null;
        String groupsToDeleteJson = m.get('groupsToDeleteJson') != null ? String.valueOf(m.get('groupsToDeleteJson')) : null;
        String existingGroupCountsJson =
            m.get('existingGroupCountsJson') != null ? String.valueOf(m.get('existingGroupCountsJson')) : null;
        String hierarchyJson = m.get('hierarchyJson') != null ? String.valueOf(m.get('hierarchyJson')) : null;
        String productCountsJson = m.get('productCountsJson') != null ? String.valueOf(m.get('productCountsJson')) : null;
        String csvImportLineItemsJson =
            m.get('csvImportLineItemsJson') != null ? String.valueOf(m.get('csvImportLineItemsJson')) : null;

        Integer currentTotal = 0;
        if (!isCreate && String.isNotBlank(quoteIdStr)) {
            try {
                Id qId = Id.valueOf(quoteIdStr);
                currentTotal = [SELECT COUNT() FROM QuoteLineItem WHERE QuoteId = :qId];
            } catch (Exception e) {
                return buildResponse(0, 0, 0, 0, 0, 'Invalid quote Id');
            }
        }

        Set<Id> deletedGroupIds = expandDeletedGroupIds(groupsToDeleteJson);
        Integer linesRemovedFromDeletes = 0;
        if (!isCreate && String.isNotBlank(quoteIdStr) && !deletedGroupIds.isEmpty()) {
            try {
                Id qId = Id.valueOf(quoteIdStr);
                linesRemovedFromDeletes = [
                    SELECT COUNT()
                    FROM QuoteLineItem
                    WHERE QuoteId = :qId
                      AND QuoteLineGroupId IN :deletedGroupIds
                ];
            } catch (Exception e) {
                return buildResponse(0, 0, 0, 0, 0, 'Invalid quote Id');
            }
        }

        Integer netExisting = 0;
        if (!isCreate && String.isNotBlank(quoteIdStr) && String.isNotBlank(existingGroupCountsJson)) {
            try {
                Id qId = Id.valueOf(quoteIdStr);
                netExisting = computeNetExistingGroupLines(qId, existingGroupCountsJson, deletedGroupIds);
            } catch (Exception e) {
                return buildResponse(currentTotal, linesRemovedFromDeletes, 0, 0, 0, 'Invalid existing group counts data; refresh and try again');
            }
        }

        Integer newFromHierarchy = 0;
        if (String.isNotBlank(csvImportLineItemsJson)) {
            // CSV path: countCsvImportLinesForPreview parses hierarchyJson internally and
            // returns 0 for blank/empty hierarchies, so no need to call parseParentsList first.
            newFromHierarchy = RLM_SetUpQuoteInvocable.countCsvImportLinesForPreview(hierarchyJson, csvImportLineItemsJson);
        } else {
            List<Object> parentsList = parseParentsList(hierarchyJson);
            if (parentsList != null && !parentsList.isEmpty()) {
                newFromHierarchy = RLM_SetUpQuoteInvocable.sumProductCountsJsonValues(productCountsJson);
            }
        }

        Integer projected = currentTotal - linesRemovedFromDeletes + netExisting + newFromHierarchy;
        if (projected < 0) {
            projected = 0;
        }

        return buildResponse(currentTotal, linesRemovedFromDeletes, netExisting, newFromHierarchy, projected, null);
    }

    private static String buildResponse(
        Integer currentTotal,
        Integer linesRemoved,
        Integer netExisting,
        Integer newHierarchy,
        Integer projected,
        String error
    ) {
        Map<String, Object> out = new Map<String, Object>{
            'currentTotal' => currentTotal,
            'linesRemovedFromDeletes' => linesRemoved,
            'netExistingGroupDelta' => netExisting,
            'newLinesFromHierarchy' => newHierarchy,
            'projectedTotal' => projected,
            'error' => error
        };
        return JSON.serialize(out);
    }

    private static List<Object> parseParentsList(String hierarchyJson) {
        if (String.isBlank(hierarchyJson)) {
            return null;
        }
        try {
            Map<String, Object> treeMap = (Map<String, Object>) JSON.deserializeUntyped(hierarchyJson);
            return (List<Object>) treeMap.get('parents');
        } catch (Exception e) {
            return null;
        }
    }

    private static Set<Id> expandDeletedGroupIds(String groupsToDeleteJson) {
        Set<Id> result = new Set<Id>();
        if (String.isBlank(groupsToDeleteJson)) {
            return result;
        }
        try {
            List<Object> arr = (List<Object>) JSON.deserializeUntyped(groupsToDeleteJson);
            Set<Id> rootIds = new Set<Id>();
            for (Object o : arr) {
                if (o != null && String.isNotBlank(String.valueOf(o))) {
                    rootIds.add(Id.valueOf(String.valueOf(o)));
                }
            }
            if (rootIds.isEmpty()) {
                return result;
            }
            result.addAll(rootIds);
            Set<Id> frontier = new Set<Id>(rootIds);
            while (!frontier.isEmpty()) {
                Set<Id> nextFrontier = new Set<Id>();
                for (QuoteLineGroup g : [
                    SELECT Id
                    FROM QuoteLineGroup
                    WHERE ParentQuoteLineGroupId IN :frontier
                ]) {
                    if (!result.contains(g.Id)) {
                        result.add(g.Id);
                        nextFrontier.add(g.Id);
                    }
                }
                frontier = nextFrontier;
            }
        } catch (Exception e) {
            return new Set<Id>();
        }
        return result;
    }

    private static Integer computeNetExistingGroupLines(Id quoteId, String existingGroupCountsJson, Set<Id> deletedGroupIds) {
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(existingGroupCountsJson);
        if (m == null || m.isEmpty()) {
            return 0;
        }
        Set<Id> groupIdsForQuery = new Set<Id>();
        Map<Id, Integer> idToNewCount = new Map<Id, Integer>();
        Map<String, Integer> tempToNewCount = new Map<String, Integer>();

        for (String k : m.keySet()) {
            Object v = m.get(k);
            Integer newCount = parsePositiveInt(v);
            Id gid = null;
            try {
                gid = Id.valueOf(k);
            } catch (Exception e) {
                tempToNewCount.put(k, newCount);
                continue;
            }
            if (deletedGroupIds != null && deletedGroupIds.contains(gid)) {
                continue;
            }
            idToNewCount.put(gid, newCount);
            groupIdsForQuery.add(gid);
        }

        Integer net = 0;
        for (String tempId : tempToNewCount.keySet()) {
            net += tempToNewCount.get(tempId);
        }

        if (groupIdsForQuery.isEmpty()) {
            return net;
        }

        List<AggregateResult> ars = [
            SELECT QuoteLineGroupId grp, COUNT(Id) cnt
            FROM QuoteLineItem
            WHERE QuoteLineGroupId IN :groupIdsForQuery AND QuoteId = :quoteId
            GROUP BY QuoteLineGroupId
        ];
        Map<Id, Integer> currentByGroup = new Map<Id, Integer>();
        for (AggregateResult ar : ars) {
            Id g = (Id) ar.get('grp');
            Object cObj = ar.get('cnt');
            Integer c = cObj == null ? 0 : Integer.valueOf(String.valueOf(cObj));
            currentByGroup.put(g, c);
        }

        for (Id gid : idToNewCount.keySet()) {
            Integer newC = idToNewCount.get(gid);
            Integer cur = currentByGroup.containsKey(gid) ? currentByGroup.get(gid) : 0;
            net += (newC - cur);
        }
        return net;
    }

    private static Integer parsePositiveInt(Object v) {
        if (v == null) {
            return 0;
        }
        Integer count = null;
        if (v instanceof Integer) {
            count = (Integer) v;
        } else if (v instanceof Decimal) {
            count = ((Decimal) v).intValue();
        } else if (v instanceof Long) {
            count = ((Long) v).intValue();
        } else if (v instanceof Double) {
            count = ((Double) v).intValue();
        } else {
            try {
                count = Integer.valueOf(String.valueOf(v));
            } catch (Exception e) {
                return 0;
            }
        }
        return count != null && count >= 0 ? count : 0;
    }
}