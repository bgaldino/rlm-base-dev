public class RLM_Utils_AccountAssetDeleter {

    public static void deleteAll(String accountId) {
        Id acctId = accountId;
        List<Asset> assets = [SELECT Id FROM Asset WHERE AccountId = :acctId];
        if (assets.isEmpty()) return;

        Set<Id> assetIds = new Map<Id, Asset>(assets).keySet();

        // Delete all restrict-delete children of Asset
        cleanupAssetReferences(assetIds);

        // Delete asset relationships (both directions)
        deleteAssetRelationships(assetIds);

        // Delete the assets themselves
        Database.DeleteResult[] results = Database.delete(assets, false);
        for (Database.DeleteResult r : results) {
            if (!r.isSuccess()) {
                for (Database.Error err : r.getErrors()) {
                    System.debug(LoggingLevel.ERROR,
                        'Error deleting Asset ' + r.getId() + ': ' + err.getMessage());
                }
            }
        }
    }

    private static void cleanupAssetReferences(Set<Id> assetIds) {
        // UsageCmtAssetRelatedObj (restrict on Asset via AssetId and RelatedObjectId)
        List<UsageCmtAssetRelatedObj> cmtByAsset = [
            SELECT Id FROM UsageCmtAssetRelatedObj WHERE AssetId IN :assetIds
        ];
        List<UsageCmtAssetRelatedObj> cmtByRelated = [
            SELECT Id FROM UsageCmtAssetRelatedObj WHERE RelatedObjectId IN :assetIds
        ];
        Map<Id, UsageCmtAssetRelatedObj> cmtMap = new Map<Id, UsageCmtAssetRelatedObj>(cmtByAsset);
        for (UsageCmtAssetRelatedObj r : cmtByRelated) cmtMap.put(r.Id, r);
        if (!cmtMap.isEmpty()) Database.delete(cmtMap.values(), false);

        // RecordAlert (restrict on Asset via ParentId and WhatId)
        List<RecordAlert> alerts = [
            SELECT Id FROM RecordAlert WHERE ParentId IN :assetIds OR WhatId IN :assetIds
        ];
        if (!alerts.isEmpty()) Database.delete(alerts, false);

        // Case (restrict on Asset)
        List<Case> cases = [SELECT Id FROM Case WHERE AssetId IN :assetIds];
        if (!cases.isEmpty()) Database.delete(cases, false);

        // ServiceContract (may not exist in all orgs)
        deleteByDynamicQuery('ServiceContract', 'AssetId', assetIds);

        // WorkOrder (may not exist in all orgs)
        deleteByDynamicQuery('WorkOrder', 'AssetId', assetIds);
    }

    private static void deleteByDynamicQuery(String objectName, String fieldName, Set<Id> ids) {
        try {
            String soql = 'SELECT Id FROM ' + objectName + ' WHERE ' + fieldName + ' IN :ids';
            List<SObject> records = Database.query(soql);
            if (!records.isEmpty()) Database.delete(records, false);
        } catch (Exception e) {
            System.debug(LoggingLevel.FINE, objectName + ' query skipped: ' + e.getMessage());
        }
    }

    private static void deleteAssetRelationships(Set<Id> assetIds) {
        List<AssetRelationship> byAsset = [
            SELECT Id FROM AssetRelationship WHERE AssetId IN :assetIds
        ];
        List<AssetRelationship> byRelated = [
            SELECT Id FROM AssetRelationship WHERE RelatedAssetId IN :assetIds
        ];
        Map<Id, AssetRelationship> unique = new Map<Id, AssetRelationship>(byAsset);
        for (AssetRelationship r : byRelated) unique.put(r.Id, r);
        if (!unique.isEmpty()) {
            Database.delete(unique.values(), false);
        }
    }
}
