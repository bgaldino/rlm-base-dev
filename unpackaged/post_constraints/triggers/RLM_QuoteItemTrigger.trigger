trigger RLM_QuoteItemTrigger on QuoteLineItem (before insert) {
    //collect QuoteActionIds 
    Set<Id> quoteActionIds = new Set<Id>();

    for (QuoteLineItem qi : Trigger.new) {
        if (qi.QuoteActionId != null && qi.RLM_ConstraintEngineNodeStatus__c == null) {
            quoteActionIds.add(qi.QuoteActionId);
        }
    }

    if (!quoteActionIds.isEmpty()) {
        // Step 1: Get QuoteAction → SourceAsset
        Map<Id, Id> quoteActionToAssetId = new Map<Id, Id>();
        for (QuoteAction qAction : [
            SELECT Id, SourceAssetId 
            FROM QuoteAction 
            WHERE SourceAssetId != null 
              AND Id IN :quoteActionIds
        ]) {
            quoteActionToAssetId.put(qAction.Id, qAction.SourceAssetId);
        }

        // Step 2: Get AssetActions
        List<AssetAction> assetActions = [
            SELECT Id, AssetId, ActionDate 
            FROM AssetAction 
            WHERE AssetId IN :quoteActionToAssetId.values()
        ];

        // Step 3: Get latest AssetAction per Asset
        Map<Id, AssetAction> assetIdToLatestAction = new Map<Id, AssetAction>();
        for (AssetAction aAction : assetActions) {
            AssetAction existing = assetIdToLatestAction.get(aAction.AssetId);
            if (existing == null || aAction.ActionDate > existing.ActionDate) {
                assetIdToLatestAction.put(aAction.AssetId, aAction);
            }
        }

        // Step 4: Get related AssetActionSource records
        Map<Id, Id> assetIdToActionId = new Map<Id, Id>();
        for (Id assetId : assetIdToLatestAction.keySet()) {
            assetIdToActionId.put(assetId, assetIdToLatestAction.get(assetId).Id);
        }

        List<AssetActionSource> assetActionSources = [
            SELECT RLM_ConstraintEngineNodeStatus__c, AssetAction.AssetId 
            FROM AssetActionSource 
            WHERE AssetActionId IN :assetIdToActionId.values() ORDER BY CreatedDate DESC
        ];
        // Step 5: Map AssetId → Status
        Map<Id, String> assetIdToStatus = new Map<Id, String>();
        for (AssetActionSource actionSource : assetActionSources) {
            if (!assetIdToStatus.containsKey(actionSource.AssetAction.AssetId) && 
                actionSource.RLM_ConstraintEngineNodeStatus__c != null) {
                assetIdToStatus.put(
                    actionSource.AssetAction.AssetId, 
                    actionSource.RLM_ConstraintEngineNodeStatus__c
                );
            }
        }
        List<QuoteLineItem> toUpdate = new List<QuoteLineItem>();
        // Step 6: Set RLM_ConstraintEngineNodeStatus__c directly on Trigger.new records
        for (QuoteLineItem qi : Trigger.new) {            
            if (qi.QuoteActionId != null && qi.RLM_ConstraintEngineNodeStatus__c == null) {
                Id assetId = quoteActionToAssetId != null ? quoteActionToAssetId.get(qi.QuoteActionId) : null;
                if (assetId != null && assetIdToStatus != null) {
                    String status = assetIdToStatus.get(assetId);
                    if (status != null) {
                       qi.RLM_ConstraintEngineNodeStatus__c = status;
                    }
                }
            }
        }
    }
}
