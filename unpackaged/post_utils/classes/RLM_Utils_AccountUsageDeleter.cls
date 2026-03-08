public class RLM_Utils_AccountUsageDeleter {

    // --- Convenience method: delete all summaries with shared queries ---

    public static void deleteAllSummaries(String accountId) {
        Set<Id> assetIds = queryAssetIds(accountId);
        Set<Id> uebIds = getAllUsageEntitlementBucketIds(accountId);

        // Order matters: UAG blocks UBPI, so delete deepest children first
        deleteUsageSummaries(accountId, assetIds, uebIds);
        deleteUsageRatableSumCmtAssetRts(assetIds);
        deleteUsageRatableSummaries(accountId, assetIds, uebIds);
        deleteUsageBillingPeriodItems(accountId, assetIds, uebIds);
    }

    // --- Public standalone methods (each queries its own data) ---

    public static void deleteUsageBillingPeriodItems(String accountId) {
        deleteUsageBillingPeriodItems(accountId, queryAssetIds(accountId), getAllUsageEntitlementBucketIds(accountId));
    }

    public static void deleteUsageRatableSummaries(String accountId) {
        deleteUsageRatableSummaries(accountId, queryAssetIds(accountId), getAllUsageEntitlementBucketIds(accountId));
    }

    public static void deleteUsageSummaries(String accountId) {
        deleteUsageSummaries(accountId, queryAssetIds(accountId), getAllUsageEntitlementBucketIds(accountId));
    }

    public static void deleteUsageRatableSumCmtAssetRts(String accountId) {
        deleteUsageRatableSumCmtAssetRts(queryAssetIds(accountId));
    }

    public static void deleteTransactionJournals(String accountId) {
        List<TransactionJournal> toDelete = [
            SELECT Id FROM TransactionJournal WHERE AccountId = :accountId
        ];
        if (!toDelete.isEmpty()) {
            Database.delete(toDelete, false);
        }
    }

    // --- Entitlements (UEB bottom-up, then TUE, then UEA) ---

    public static void deleteEntitlements(String accountId) {
        Id acctId = accountId;

        List<TransactionUsageEntitlement> tues = [
            SELECT Id FROM TransactionUsageEntitlement WHERE AccountId = :acctId
        ];
        Set<Id> tueIds = new Set<Id>(new Map<Id, TransactionUsageEntitlement>(tues).keySet());

        List<UsageEntitlementAccount> ueas = [
            SELECT Id FROM UsageEntitlementAccount WHERE AccountId = :acctId
        ];
        Set<Id> ueaIds = new Set<Id>(new Map<Id, UsageEntitlementAccount>(ueas).keySet());

        // Also find UEAs by GrantBindingTargetId (restrict-delete on Asset)
        Set<Id> assetIds = queryAssetIds(acctId);
        if (!assetIds.isEmpty()) {
            for (UsageEntitlementAccount uea : [
                SELECT Id FROM UsageEntitlementAccount WHERE GrantBindingTargetId IN :assetIds
            ]) ueaIds.add(uea.Id);
        }

        // Collect all parent IDs for bucket queries
        Set<Id> allParentIds = new Set<Id>();
        allParentIds.addAll(tueIds);
        allParentIds.addAll(ueaIds);

        // Delete UEBs bottom-up
        if (!allParentIds.isEmpty()) {
            deleteEntitlementBucketsBottomUp(allParentIds);
        }

        // Delete TUEs
        if (!tueIds.isEmpty()) {
            List<TransactionUsageEntitlement> remaining = [
                SELECT Id FROM TransactionUsageEntitlement WHERE Id IN :tueIds
            ];
            if (!remaining.isEmpty()) {
                Database.delete(remaining, false);
            }
        }

        // Delete UEAs
        if (!ueaIds.isEmpty()) {
            List<UsageEntitlementAccount> remaining = [
                SELECT Id FROM UsageEntitlementAccount WHERE Id IN :ueaIds
            ];
            if (!remaining.isEmpty()) {
                Database.delete(remaining, false);
            }
        }
    }

    // --- Private implementation methods ---

    private static void deleteUsageBillingPeriodItems(String accountId, Set<Id> assetIds, Set<Id> uebIds) {
        List<UsageBillingPeriodItem> byAccount = [
            SELECT Id FROM UsageBillingPeriodItem WHERE AccountId = :accountId
        ];
        Map<Id, UsageBillingPeriodItem> toDelete = new Map<Id, UsageBillingPeriodItem>(byAccount);

        if (!assetIds.isEmpty()) {
            for (UsageBillingPeriodItem r : [
                SELECT Id FROM UsageBillingPeriodItem WHERE AssetId IN :assetIds
            ]) toDelete.put(r.Id, r);

            for (UsageBillingPeriodItem r : [
                SELECT Id FROM UsageBillingPeriodItem WHERE GrantBindingTargetId IN :assetIds
            ]) toDelete.put(r.Id, r);
        }

        if (!uebIds.isEmpty()) {
            for (UsageBillingPeriodItem r : [
                SELECT Id FROM UsageBillingPeriodItem WHERE UsageEntitlementBucketId IN :uebIds
            ]) toDelete.put(r.Id, r);
        }

        if (!toDelete.isEmpty()) {
            Database.delete(toDelete.values(), false);
        }
    }

    private static void deleteUsageRatableSummaries(String accountId, Set<Id> assetIds, Set<Id> uebIds) {
        List<UsageRatableSummary> byAccount = [
            SELECT Id FROM UsageRatableSummary WHERE AccountId = :accountId
        ];
        Map<Id, UsageRatableSummary> toDelete = new Map<Id, UsageRatableSummary>(byAccount);

        if (!assetIds.isEmpty()) {
            for (UsageRatableSummary r : [
                SELECT Id FROM UsageRatableSummary WHERE AssetId IN :assetIds
            ]) toDelete.put(r.Id, r);

            for (UsageRatableSummary r : [
                SELECT Id FROM UsageRatableSummary WHERE GrantBindingTargetId IN :assetIds
            ]) toDelete.put(r.Id, r);
        }

        if (!uebIds.isEmpty()) {
            for (UsageRatableSummary r : [
                SELECT Id FROM UsageRatableSummary WHERE UsageEntitlementBucketId IN :uebIds
            ]) toDelete.put(r.Id, r);
        }

        if (!toDelete.isEmpty()) {
            Database.delete(toDelete.values(), false);
        }
    }

    private static void deleteUsageSummaries(String accountId, Set<Id> assetIds, Set<Id> uebIds) {
        List<UsageSummary> byAccount = [
            SELECT Id FROM UsageSummary WHERE AccountId = :accountId
        ];
        Map<Id, UsageSummary> toDelete = new Map<Id, UsageSummary>(byAccount);

        if (!assetIds.isEmpty()) {
            for (UsageSummary r : [
                SELECT Id FROM UsageSummary WHERE AssetId IN :assetIds
            ]) toDelete.put(r.Id, r);

            for (UsageSummary r : [
                SELECT Id FROM UsageSummary WHERE GrantBindingTargetId IN :assetIds
            ]) toDelete.put(r.Id, r);
        }

        if (!uebIds.isEmpty()) {
            for (UsageSummary r : [
                SELECT Id FROM UsageSummary WHERE UsageEntitlementBucketId IN :uebIds
            ]) toDelete.put(r.Id, r);
        }

        if (!toDelete.isEmpty()) {
            Database.delete(toDelete.values(), false);
        }
    }

    private static void deleteUsageRatableSumCmtAssetRts(Set<Id> assetIds) {
        if (assetIds.isEmpty()) return;

        List<UsageRatableSumCmtAssetRt> toDelete = [
            SELECT Id FROM UsageRatableSumCmtAssetRt WHERE CommitmentAssetId IN :assetIds
        ];
        if (!toDelete.isEmpty()) {
            Database.delete(toDelete, false);
        }
    }

    // --- Bottom-up UEB deletion ---

    private static void deleteEntitlementBucketsBottomUp(Set<Id> parentIds) {
        List<UsageEntitlementBucket> initial = [
            SELECT Id, ParentId, TransactionUsageEntitlementId
            FROM UsageEntitlementBucket
            WHERE TransactionUsageEntitlementId IN :parentIds
            OR ParentId IN :parentIds
        ];

        if (initial.isEmpty()) return;

        Map<Id, UsageEntitlementBucket> bucketMap = new Map<Id, UsageEntitlementBucket>(initial);

        // Recursively discover all child buckets
        Set<Id> currentLevelIds = new Set<Id>(bucketMap.keySet());
        while (!currentLevelIds.isEmpty()) {
            List<UsageEntitlementBucket> children = [
                SELECT Id, ParentId, TransactionUsageEntitlementId
                FROM UsageEntitlementBucket
                WHERE ParentId IN :currentLevelIds
                AND Id NOT IN :bucketMap.keySet()
            ];
            if (children.isEmpty()) break;

            Set<Id> nextLevel = new Set<Id>();
            for (UsageEntitlementBucket child : children) {
                bucketMap.put(child.Id, child);
                nextLevel.add(child.Id);
            }
            currentLevelIds = nextLevel;
        }

        // Build parent-to-children index for O(n) leaf detection
        Map<Id, Set<Id>> parentToChildren = new Map<Id, Set<Id>>();
        for (UsageEntitlementBucket bucket : bucketMap.values()) {
            if (bucket.ParentId != null && bucketMap.containsKey(bucket.ParentId)) {
                if (!parentToChildren.containsKey(bucket.ParentId)) {
                    parentToChildren.put(bucket.ParentId, new Set<Id>());
                }
                parentToChildren.get(bucket.ParentId).add(bucket.Id);
            }
        }

        // Delete leaf-first in rounds
        Set<Id> remaining = new Set<Id>(bucketMap.keySet());
        Integer round = 0;

        while (!remaining.isEmpty() && round < 10) {
            round++;
            Set<Id> leaves = new Set<Id>();
            for (Id bucketId : remaining) {
                Set<Id> childIds = parentToChildren.get(bucketId);
                if (childIds == null || !hasAnyIn(childIds, remaining)) {
                    leaves.add(bucketId);
                }
            }

            if (leaves.isEmpty()) break;

            Database.DeleteResult[] results = Database.delete(
                [SELECT Id FROM UsageEntitlementBucket WHERE Id IN :leaves], false
            );

            Set<Id> deleted = new Set<Id>();
            for (Database.DeleteResult r : results) {
                if (r.isSuccess()) {
                    deleted.add(r.getId());
                } else {
                    for (Database.Error err : r.getErrors()) {
                        System.debug(LoggingLevel.ERROR,
                            'Error deleting UEB ' + r.getId() + ': ' + err.getMessage());
                    }
                }
            }

            remaining.removeAll(deleted);
            if (deleted.isEmpty()) break;
        }
    }

    // --- Helpers ---

    private static Boolean hasAnyIn(Set<Id> candidates, Set<Id> target) {
        for (Id candidate : candidates) {
            if (target.contains(candidate)) return true;
        }
        return false;
    }

    private static Set<Id> queryAssetIds(String accountId) {
        return new Map<Id, Asset>(
            [SELECT Id FROM Asset WHERE AccountId = :accountId]
        ).keySet();
    }

    private static Set<Id> getAllUsageEntitlementBucketIds(String accountId) {
        Id acctId = accountId;

        Set<Id> parentIds = new Set<Id>();

        for (TransactionUsageEntitlement t : [
            SELECT Id FROM TransactionUsageEntitlement WHERE AccountId = :acctId
        ]) parentIds.add(t.Id);

        for (UsageEntitlementAccount u : [
            SELECT Id FROM UsageEntitlementAccount WHERE AccountId = :acctId
        ]) parentIds.add(u.Id);

        if (parentIds.isEmpty()) return new Set<Id>();

        Map<Id, UsageEntitlementBucket> bucketMap = new Map<Id, UsageEntitlementBucket>([
            SELECT Id, ParentId
            FROM UsageEntitlementBucket
            WHERE TransactionUsageEntitlementId IN :parentIds
            OR ParentId IN :parentIds
        ]);

        Set<Id> currentLevel = new Set<Id>(bucketMap.keySet());
        while (!currentLevel.isEmpty()) {
            List<UsageEntitlementBucket> children = [
                SELECT Id, ParentId
                FROM UsageEntitlementBucket
                WHERE ParentId IN :currentLevel
                AND Id NOT IN :bucketMap.keySet()
            ];
            if (children.isEmpty()) break;
            Set<Id> nextLevel = new Set<Id>();
            for (UsageEntitlementBucket child : children) {
                bucketMap.put(child.Id, child);
                nextLevel.add(child.Id);
            }
            currentLevel = nextLevel;
        }

        return bucketMap.keySet();
    }
}
