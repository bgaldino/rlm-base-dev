/**
 * Estimates QuoteLineItem row count before Run (wizard preview on product-count and confirm steps).
 * Mirrors RLM_SetUpQuoteInvocable modify order: deletes → additive existingGroupCounts → new hierarchy lines.
 */
public with sharing class RLM_SetUpQuoteLinePreview {
    // Hard cap on QuoteLineGroup delete-expansion BFS depth (realistic nesting <=5; 50 is
    // well under the synchronous SOQL governor). Hitting it means the expansion is partial.
    private static final Integer EXPANSION_MAX_LEVELS = 50;

    // Thrown when the depth guard trips, so the preview surfaces an error instead of
    // silently undercounting the deleted-group / projected-line totals.
    public class PreviewExpansionException extends Exception {}

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
        String productSetMode = RLM_SetUpQuoteProductSets.normalizeProductSetMode(
            m.get('productSetMode') != null ? String.valueOf(m.get('productSetMode')) : null
        );
        String csvImportLineItemsJson =
            m.get('csvImportLineItemsJson') != null ? String.valueOf(m.get('csvImportLineItemsJson')) : null;

        Integer currentTotal = 0;
        Id parsedQId = null;
        if (!isCreate && String.isNotBlank(quoteIdStr)) {
            try {
                parsedQId = Id.valueOf(quoteIdStr);
                currentTotal = [SELECT COUNT() FROM QuoteLineItem WHERE QuoteId = :parsedQId WITH USER_MODE];
            } catch (Exception e) {
                return buildResponse(0, 0, 0, 0, 0, 'Invalid quote Id');
            }
        }

        Set<Id> deletedGroupIds;
        try {
            deletedGroupIds = expandDeletedGroupIds(groupsToDeleteJson, parsedQId);
        } catch (PreviewExpansionException e) {
            // Partial delete-set (depth guard tripped): surface an error instead of
            // silently undercounting linesRemovedFromDeletes / the projected total.
            return buildResponse(currentTotal, 0, 0, 0, currentTotal, e.getMessage());
        }
        Integer linesRemovedFromDeletes = 0;
        if (!isCreate && parsedQId != null && !deletedGroupIds.isEmpty()) {
            linesRemovedFromDeletes = [
                SELECT COUNT()
                FROM QuoteLineItem
                WHERE QuoteId = :parsedQId
                  AND QuoteLineGroupId IN :deletedGroupIds
                WITH USER_MODE
            ];
        }

        Integer existingAdds = 0;
        if (!isCreate && parsedQId != null && String.isNotBlank(existingGroupCountsJson)) {
            try {
                existingAdds = computeExistingGroupAdds(existingGroupCountsJson, deletedGroupIds, productSetMode, parsedQId);
            } catch (Exception e) {
                // Surface the failure instead of silently undercounting the preview.
                Integer projectedOnError = currentTotal - linesRemovedFromDeletes;
                if (projectedOnError < 0) {
                    projectedOnError = 0;
                }
                return buildResponse(
                    currentTotal,
                    linesRemovedFromDeletes,
                    0,
                    0,
                    projectedOnError,
                    'Could not read the existing group product counts, so the preview may be inaccurate. Refresh the page and re-enter the counts, then try again.'
                );
            }
        }

        Integer newFromHierarchy = 0;
        List<Object> parentsList = parseParentsList(hierarchyJson);
        Boolean useCsv = String.isNotBlank(csvImportLineItemsJson);
        if (useCsv) {
            // CSV lines resolve even with an empty hierarchy (CSV-only / ungrouped
            // modify where hierarchyJson is {"parents":[]}), so count them
            // regardless of whether parents are present.
            newFromHierarchy = RLM_SetUpQuoteInvocable.countCsvImportLinesForPreview(hierarchyJson, csvImportLineItemsJson);
        } else {
            if (parentsList != null && !parentsList.isEmpty()) {
                newFromHierarchy = RLM_SetUpQuoteProductSets.sumExpectedQliCounts(productSetMode, productCountsJson);
            }
            // Ungrouped (no-group) lines: the non-CSV invocable path adds these via
            // addProductRequestsForCount(ungroupedProductCount, ...) independent of the
            // hierarchy, so include them here or the preview undercounts. Expected QLI
            // count mirrors the invocable's product-set/demo allocation.
            Integer ungroupedProductCount = RLM_SetUpQuoteProductSets.parseNonNegativeInteger(m.get('ungroupedProductCount'));
            if (ungroupedProductCount > 0) {
                newFromHierarchy += RLM_SetUpQuoteProductSets.expectedQliCountForRequestedCount(productSetMode, ungroupedProductCount);
            }
        }

        Integer projected = currentTotal - linesRemovedFromDeletes + existingAdds + newFromHierarchy;
        if (projected < 0) {
            projected = 0;
        }

        return buildResponse(currentTotal, linesRemovedFromDeletes, existingAdds, newFromHierarchy, projected, null);
    }

    private static String buildResponse(
        Integer currentTotal,
        Integer linesRemoved,
        Integer existingAdds,
        Integer newHierarchy,
        Integer projected,
        String error
    ) {
        Map<String, Object> out = new Map<String, Object>{
            'currentTotal' => currentTotal,
            'linesRemovedFromDeletes' => linesRemoved,
            'netExistingGroupDelta' => existingAdds,
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

    private static Set<Id> expandDeletedGroupIds(String groupsToDeleteJson, Id quoteId) {
        Set<Id> result = new Set<Id>();
        if (String.isBlank(groupsToDeleteJson)) {
            return result;
        }
        Boolean truncated = false;
        try {
            List<Object> arr = (List<Object>) JSON.deserializeUntyped(groupsToDeleteJson);
            Set<Id> rootIds = new Set<Id>();
            for (Object o : arr) {
                if (o == null) {
                    continue;
                }
                String idStr = String.valueOf(o);
                if (String.isBlank(idStr)) {
                    continue;
                }
                try {
                    rootIds.add(Id.valueOf(idStr));
                } catch (Exception e) {
                    // Skip invalid Id entries rather than discarding the entire delete set.
                    continue;
                }
            }
            if (rootIds.isEmpty()) {
                return result;
            }
            // Ownership guard: only traverse roots that belong to the target quote
            if (quoteId != null) {
                Set<Id> ownedRoots = new Set<Id>();
                for (QuoteLineGroup g : [SELECT Id FROM QuoteLineGroup WHERE Id IN :rootIds AND QuoteId = :quoteId WITH USER_MODE]) {
                    ownedRoots.add(g.Id);
                }
                rootIds = ownedRoots;
                if (rootIds.isEmpty()) {
                    return result;
                }
            }
            result.addAll(rootIds);
            // Frontier BFS: each iteration only queries children of the groups
            // discovered in the previous level, instead of re-querying children of
            // the entire (growing) result set. Keeps this O(n) over the subtree
            // rather than O(n^2) on deep/wide hierarchies.
            Set<Id> frontier = new Set<Id>(rootIds);
            // Depth guard: bound the per-level SOQL so a pathologically deep hierarchy can't
            // exhaust the query governor limit. Group nesting is realistically <=5 levels;
            // EXPANSION_MAX_LEVELS is a safe hard cap well under the synchronous SOQL ceiling.
            Integer levelGuard = 0;
            while (!frontier.isEmpty() && levelGuard < EXPANSION_MAX_LEVELS) {
                levelGuard++;
                Set<Id> nextFrontier = new Set<Id>();
                List<QuoteLineGroup> children = quoteId != null
                    ? [SELECT Id FROM QuoteLineGroup WHERE ParentQuoteLineGroupId IN :frontier AND QuoteId = :quoteId WITH USER_MODE]
                    : [SELECT Id FROM QuoteLineGroup WHERE ParentQuoteLineGroupId IN :frontier WITH USER_MODE];
                for (QuoteLineGroup g : children) {
                    if (!result.contains(g.Id)) {
                        result.add(g.Id);
                        nextFrontier.add(g.Id);
                    }
                }
                frontier = nextFrontier;
            }
            // Guard tripped with levels still pending => the delete set is PARTIAL. Flag it
            // here (frontier is in scope) and throw AFTER the catch so the caller surfaces it
            // rather than silently undercounting.
            truncated = !frontier.isEmpty();
        } catch (Exception e) {
            return new Set<Id>();
        }
        if (truncated) {
            throw new PreviewExpansionException(
                'The group hierarchy is too deep to preview accurately (exceeded ' +
                EXPANSION_MAX_LEVELS + ' levels). Refresh the page and retry, or reduce nesting.');
        }
        return result;
    }

    private static Integer computeExistingGroupAdds(String existingGroupCountsJson, Set<Id> deletedGroupIds, String productSetMode, Id quoteId) {
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(existingGroupCountsJson);
        if (m == null || m.isEmpty()) {
            return 0;
        }
        Integer adds = 0;
        // Real group Ids are validated against the quote in one query; tempId (new subgroup) keys
        // are counted directly since they will be created on this quote.
        Map<Id, Integer> idToAddCount = new Map<Id, Integer>();
        for (String k : m.keySet()) {
            Object v = m.get(k);
            Integer addCount = RLM_SetUpQuoteProductSets.expectedQliCountForRequestedCount(productSetMode, parsePositiveInt(v));
            Id gid = null;
            try {
                gid = Id.valueOf(k);
            } catch (Exception e) {
                adds += addCount;
                continue;
            }
            if (deletedGroupIds != null && deletedGroupIds.contains(gid)) {
                continue;
            }
            idToAddCount.put(gid, addCount);
        }
        if (idToAddCount.isEmpty()) {
            return adds;
        }
        if (quoteId == null) {
            for (Integer c : idToAddCount.values()) {
                adds += c;
            }
            return adds;
        }
        // Ownership guard: only count adds for groups that belong to this quote
        Set<Id> validGroupIds = new Set<Id>();
        for (QuoteLineGroup g : [SELECT Id FROM QuoteLineGroup WHERE QuoteId = :quoteId AND Id IN :idToAddCount.keySet() WITH USER_MODE]) {
            validGroupIds.add(g.Id);
        }
        for (Id gid : idToAddCount.keySet()) {
            if (validGroupIds.contains(gid)) {
                adds += idToAddCount.get(gid);
            }
        }
        return adds;
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
