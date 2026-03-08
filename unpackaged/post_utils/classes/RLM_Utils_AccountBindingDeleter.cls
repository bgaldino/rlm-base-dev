public class RLM_Utils_AccountBindingDeleter {

    private static final Integer BATCH_SIZE = 200;

    public static void deleteAll(String accountId) {
        deleteUsageResourcePolicies(accountId);
        deleteRateCardEntries(accountId);
        deleteAssetRateCardEntries(accountId);
    }

    public static void deleteUsageResourcePolicies(String accountId) {
        Map<Id, BindingObjUsageRsrcPlcy> unique = new Map<Id, BindingObjUsageRsrcPlcy>();

        for (BindingObjUsageRsrcPlcy p : [
            SELECT Id FROM BindingObjUsageRsrcPlcy WHERE BindingObjectId = :accountId
        ]) unique.put(p.Id, p);

        for (BindingObjUsageRsrcPlcy p : [
            SELECT Id FROM BindingObjUsageRsrcPlcy
            WHERE BindingObjectId IN (SELECT Id FROM Asset WHERE AccountId = :accountId)
        ]) unique.put(p.Id, p);

        for (BindingObjUsageRsrcPlcy p : [
            SELECT Id FROM BindingObjUsageRsrcPlcy
            WHERE BindingObjectId IN (SELECT Id FROM Contract WHERE AccountId = :accountId)
        ]) unique.put(p.Id, p);

        if (!unique.isEmpty()) {
            deleteBatched(unique.values());
        }
    }

    public static void deleteRateCardEntries(String accountId) {
        Map<Id, BindingObjectRateCardEntry> unique = new Map<Id, BindingObjectRateCardEntry>();

        for (BindingObjectRateCardEntry p : [
            SELECT Id FROM BindingObjectRateCardEntry WHERE BindingObjectId = :accountId
        ]) unique.put(p.Id, p);

        for (BindingObjectRateCardEntry p : [
            SELECT Id FROM BindingObjectRateCardEntry
            WHERE BindingObjectId IN (SELECT Id FROM Contract WHERE AccountId = :accountId)
        ]) unique.put(p.Id, p);

        if (!unique.isEmpty()) {
            deleteBatched(unique.values());
        }
    }

    public static void deleteAssetRateCardEntries(String accountId) {
        List<Asset> assets = [SELECT Id FROM Asset WHERE AccountId = :accountId];
        Set<Id> assetIds = new Map<Id, Asset>(assets).keySet();
        if (assetIds.isEmpty()) return;

        List<AssetRateCardEntry> toDelete = [
            SELECT Id FROM AssetRateCardEntry WHERE BindingObjectId IN :assetIds
        ];
        if (!toDelete.isEmpty()) {
            Database.delete(toDelete, false);
        }
    }

    private static void deleteBatched(List<SObject> records) {
        List<SObject> batch = new List<SObject>();
        for (SObject r : records) {
            batch.add(r);
            if (batch.size() == BATCH_SIZE) {
                Database.delete(batch, false);
                batch.clear();
            }
        }
        if (!batch.isEmpty()) {
            Database.delete(batch, false);
        }
    }
}
