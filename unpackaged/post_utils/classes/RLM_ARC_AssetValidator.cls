/**
 * Validates whether assets (and their related assets) are eligible for asset lifecycle
 * actions (Swap, Upgrade, Downgrade, Transfer, Rollback).
 *
 * Checks for conditions that block specific actions per Salesforce 260 (Spring '26)
 * documented limitations:
 *   - Ramped assets: block Swap/Upgrade/Downgrade, Transfer, Rollback
 *   - Usage-based assets: block Swap/Upgrade/Downgrade, Transfer, Rollback
 *   - Expired assets: block Swap/Upgrade/Downgrade, Transfer
 *   - Derived-price products: block Swap/Upgrade/Downgrade
 *
 * NOTE: These constraints may be lifted in future releases — revisit when upgrading.
 *
 * Uses "without sharing" intentionally — the validator must see all related assets
 * regardless of the running user's record access to produce accurate results.
 * Returns boolean flags, ID lists, error messages, and queried Asset SObject
 * records for display in flow datatables.
 */
public without sharing class RLM_ARC_AssetValidator {

    @InvocableMethod(label='Validate Assets for Asset Actions' description='Checks whether any of the provided assets (including related assets via AssetRelationship) are ramped, usage-based, expired, or derived-price — conditions that block swap, transfer, and rollback operations.')
    public static List<Result> validate(List<Request> requests) {
        // 1. Build the expanded asset ID set per request (input IDs + related assets)
        List<Set<Id>> expandedIdsByRequest = expandWithRelatedAssets(requests);

        // 2. Collect all asset IDs across all requests for bulk queries
        Set<Id> allAssetIds = new Set<Id>();
        for (Set<Id> ids : expandedIdsByRequest) {
            allAssetIds.addAll(ids);
        }

        // 3. Query once for each validation dimension
        Set<Id> rampedAssetIds = getRampedAssetIds(allAssetIds);

        // Single Asset query for both expired check and product-to-asset mapping
        Set<Id> expiredAssetIds = new Set<Id>();
        Map<Id, Set<Id>> assetIdsByProductId = new Map<Id, Set<Id>>();
        queryAssetsForExpiredAndProducts(allAssetIds, expiredAssetIds, assetIdsByProductId);

        Set<Id> usageBasedAssetIds = getUsageBasedAssetIds(assetIdsByProductId);
        Set<Id> derivedPriceAssetIds = getDerivedPriceAssetIds(assetIdsByProductId);

        // 4. Query all blocked assets once for datatable display
        Set<Id> allBlockedIds = new Set<Id>();
        allBlockedIds.addAll(rampedAssetIds);
        allBlockedIds.addAll(usageBasedAssetIds);
        allBlockedIds.addAll(expiredAssetIds);
        allBlockedIds.addAll(derivedPriceAssetIds);

        Map<Id, Asset> blockedAssetMap = new Map<Id, Asset>();
        if (!allBlockedIds.isEmpty()) {
            blockedAssetMap = new Map<Id, Asset>((List<Asset>) Security.stripInaccessible(
                AccessType.READABLE,
                [SELECT Id, Name, Product2.Name, LifecycleStartDate, LifecycleEndDate
                 FROM Asset WHERE Id IN :allBlockedIds]
            ).getRecords());
        }

        // 5. Map results back to each request
        List<Result> results = new List<Result>();
        for (Set<Id> assetIds : expandedIdsByRequest) {
            Result res = new Result();
            res.rampedAssetIds = getIntersection(assetIds, rampedAssetIds);
            res.usageBasedAssetIds = getIntersection(assetIds, usageBasedAssetIds);
            res.expiredAssetIds = getIntersection(assetIds, expiredAssetIds);
            res.derivedPriceAssetIds = getIntersection(assetIds, derivedPriceAssetIds);
            res.hasRampedAssets = !res.rampedAssetIds.isEmpty();
            res.hasUsageBasedAssets = !res.usageBasedAssetIds.isEmpty();
            res.hasExpiredAssets = !res.expiredAssetIds.isEmpty();
            res.hasDerivedPriceAssets = !res.derivedPriceAssetIds.isEmpty();

            // Collect queried Asset records for all blocked assets in this request
            res.blockedAssets = new List<Asset>();
            for (Id assetId : assetIds) {
                if (blockedAssetMap.containsKey(assetId)) {
                    res.blockedAssets.add(blockedAssetMap.get(assetId));
                }
            }

            // Build action-specific error messages listing the exact blocking conditions
            res.swapBlockedMessage = buildBlockedMessage(res, 'swap, upgrade, or downgrade', true, true);
            res.transferBlockedMessage = buildBlockedMessage(res, 'transfer', true, false);
            res.rollbackBlockedMessage = buildBlockedMessage(res, 'rollback', false, false);
            results.add(res);
        }

        return results;
    }

    /**
     * Expands each request's input asset IDs to include related assets found via
     * AssetRelationship (queried in both directions). Uses a single SOQL query
     * across all requests.
     */
    private static List<Set<Id>> expandWithRelatedAssets(List<Request> requests) {
        // Collect all input IDs for a single relationship query
        Set<Id> allInputIds = new Set<Id>();
        List<Set<Id>> idsByRequest = new List<Set<Id>>();

        for (Request req : requests) {
            Set<Id> inputIds = (req.recordIds != null && !req.recordIds.isEmpty())
                ? new Set<Id>(req.recordIds)
                : new Set<Id>();
            idsByRequest.add(inputIds);
            allInputIds.addAll(inputIds);
        }

        if (allInputIds.isEmpty()) {
            return idsByRequest;
        }

        // Build a map: input asset ID → set of related asset IDs (both directions)
        Map<Id, Set<Id>> relatedByAssetId = new Map<Id, Set<Id>>();
        for (AssetRelationship ar : [
            SELECT AssetId, RelatedAssetId
            FROM AssetRelationship
            WHERE AssetId IN :allInputIds
            OR RelatedAssetId IN :allInputIds
        ]) {
            addRelation(relatedByAssetId, ar.AssetId, ar.RelatedAssetId);
            addRelation(relatedByAssetId, ar.RelatedAssetId, ar.AssetId);
        }

        // Expand each request's set with its related assets
        for (Set<Id> assetIds : idsByRequest) {
            Set<Id> related = new Set<Id>();
            for (Id assetId : assetIds) {
                if (relatedByAssetId.containsKey(assetId)) {
                    related.addAll(relatedByAssetId.get(assetId));
                }
            }
            assetIds.addAll(related);
        }

        return idsByRequest;
    }

    private static void addRelation(Map<Id, Set<Id>> relationMap, Id key, Id value) {
        if (!relationMap.containsKey(key)) {
            relationMap.put(key, new Set<Id>());
        }
        relationMap.get(key).add(value);
    }

    /**
     * Returns the IDs of assets that have at least one AssetStatePeriod with a
     * non-null RampIdentifier, indicating the asset has ramp pricing.
     */
    private static Set<Id> getRampedAssetIds(Set<Id> assetIds) {
        Set<Id> ramped = new Set<Id>();
        if (assetIds.isEmpty()) {
            return ramped;
        }
        for (AssetStatePeriod asp : [
            SELECT AssetId
            FROM AssetStatePeriod
            WHERE AssetId IN :assetIds
            AND RampIdentifier != NULL
        ]) {
            ramped.add(asp.AssetId);
        }
        return ramped;
    }

    /**
     * Single Asset query that populates both the expired asset set and the
     * product-to-asset map, saving one SOQL query vs. querying separately.
     */
    private static void queryAssetsForExpiredAndProducts(
        Set<Id> assetIds, Set<Id> expiredAssetIds, Map<Id, Set<Id>> assetIdsByProductId
    ) {
        if (assetIds.isEmpty()) {
            return;
        }
        for (Asset a : [
            SELECT Id, Product2Id, LifecycleEndDate
            FROM Asset
            WHERE Id IN :assetIds
        ]) {
            if (a.LifecycleEndDate != null && a.LifecycleEndDate < Date.today()) {
                expiredAssetIds.add(a.Id);
            }
            if (a.Product2Id != null) {
                if (!assetIdsByProductId.containsKey(a.Product2Id)) {
                    assetIdsByProductId.put(a.Product2Id, new Set<Id>());
                }
                assetIdsByProductId.get(a.Product2Id).add(a.Id);
            }
        }
    }

    /**
     * Returns the IDs of assets whose product has at least one active
     * ProductUsageResource, indicating usage-based pricing.
     */
    private static Set<Id> getUsageBasedAssetIds(Map<Id, Set<Id>> assetIdsByProductId) {
        Set<Id> usageBased = new Set<Id>();
        if (assetIdsByProductId.isEmpty()) {
            return usageBased;
        }
        Set<Id> productIds = assetIdsByProductId.keySet();
        for (ProductUsageResource pur : [
            SELECT ProductId
            FROM ProductUsageResource
            WHERE ProductId IN :productIds
            AND Status = 'Active'
        ]) {
            usageBased.addAll(assetIdsByProductId.get(pur.ProductId));
        }
        return usageBased;
    }

    /**
     * Returns the IDs of assets whose product has at least one PricebookEntry
     * with IsDerived = true, indicating derived pricing.
     */
    private static Set<Id> getDerivedPriceAssetIds(Map<Id, Set<Id>> assetIdsByProductId) {
        Set<Id> derived = new Set<Id>();
        if (assetIdsByProductId.isEmpty()) {
            return derived;
        }
        Set<Id> productIds = assetIdsByProductId.keySet();
        for (PricebookEntry pbe : [
            SELECT Product2Id
            FROM PricebookEntry
            WHERE Product2Id IN :productIds
            AND IsDerived = true
        ]) {
            derived.addAll(assetIdsByProductId.get(pbe.Product2Id));
        }
        return derived;
    }

    private static String buildBlockedMessage(Result res, String action, Boolean includeExpired, Boolean includeDerived) {
        List<String> reasons = new List<String>();
        if (res.hasRampedAssets) {
            reasons.add('ramped (' + res.rampedAssetIds.size() + ')');
        }
        if (res.hasUsageBasedAssets) {
            reasons.add('usage-based (' + res.usageBasedAssetIds.size() + ')');
        }
        if (includeExpired && res.hasExpiredAssets) {
            reasons.add('expired (' + res.expiredAssetIds.size() + ')');
        }
        if (includeDerived && res.hasDerivedPriceAssets) {
            reasons.add('derived-price (' + res.derivedPriceAssetIds.size() + ')');
        }
        if (reasons.isEmpty()) {
            return null;
        }
        return 'This action can\'t be completed. The selected assets include '
            + String.join(reasons, ', ')
            + ' assets that don\'t support ' + action + '. Remove the affected assets and try again.';
    }

    private static List<Id> getIntersection(Set<Id> a, Set<Id> b) {
        List<Id> overlap = new List<Id>();
        for (Id id : a) {
            if (b.contains(id)) {
                overlap.add(id);
            }
        }
        return overlap;
    }

    public class Request {
        @InvocableVariable(label='Asset Record IDs' required=true)
        public List<Id> recordIds;
    }

    public class Result {
        @InvocableVariable(label='Has Ramped Assets')
        public Boolean hasRampedAssets;

        @InvocableVariable(label='Has Usage-Based Assets')
        public Boolean hasUsageBasedAssets;

        @InvocableVariable(label='Has Expired Assets')
        public Boolean hasExpiredAssets;

        @InvocableVariable(label='Has Derived-Price Assets')
        public Boolean hasDerivedPriceAssets;

        @InvocableVariable(label='Ramped Asset IDs')
        public List<Id> rampedAssetIds;

        @InvocableVariable(label='Usage-Based Asset IDs')
        public List<Id> usageBasedAssetIds;

        @InvocableVariable(label='Expired Asset IDs')
        public List<Id> expiredAssetIds;

        @InvocableVariable(label='Derived-Price Asset IDs')
        public List<Id> derivedPriceAssetIds;

        @InvocableVariable(label='Swap Blocked Message')
        public String swapBlockedMessage;

        @InvocableVariable(label='Transfer Blocked Message')
        public String transferBlockedMessage;

        @InvocableVariable(label='Rollback Blocked Message')
        public String rollbackBlockedMessage;

        @InvocableVariable(label='Blocked Assets')
        public List<Asset> blockedAssets;
    }
}
