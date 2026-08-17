/**
 * Automatic "born-held" billing gate for Asset-Based Ordering.
 *
 * Requirement: a software subscription bundled with physical (one-time) hardware
 * must not begin active billing until shipment is confirmed. Rather than expecting
 * an operator to place each new bundle on hold by hand, this handler stamps
 * qualifying software assets with RLM_Asset_Status__c = 'BillingHeld' the moment
 * they are created (and again if the bundle relationship is populated after the
 * initial insert, which is how the platform derives RootAssetId). Where a real
 * BillingScheduleGroup already exists for the held asset, its
 * NextBillingDateOverride is pushed to the far-future hold sentinel via
 * RLM_ShipmentFulfillmentService. The simulated shipment/serial event
 * (RLM_ShipmentFulfillmentService.confirmShipment) releases the gate.
 *
 * Classification mirrors RLM_ShipmentFulfillmentService: a child is "software
 * bundled with hardware" when its own product carries a TermDefined/Evergreen
 * selling model and its bundle root product carries a OneTime selling model.
 *
 * Trigger context runs in system mode, so queries/DML here do not depend on the
 * feature permission set's FLS.
 */
public with sharing class RLM_AssetBillingHoldHandler {

    private static final String STATUS_HELD = 'BillingHeld';
    private static final Set<String> SUBSCRIPTION_MODELS = new Set<String>{ 'TermDefined', 'Evergreen' };
    private static final Set<String> ONE_TIME_MODELS     = new Set<String>{ 'OneTime' };

    // Recursion guard: assets already held this transaction (our own status
    // update re-fires the Asset trigger in update context).
    @TestVisible
    private static Set<Id> processed = new Set<Id>();

    // ------------------------------------------------------------------
    // Asset trigger entry point (after insert / after update)
    // ------------------------------------------------------------------
    public static void applyHold(List<Asset> assets) {
        if (assets == null || assets.isEmpty()) return;

        // Candidate children: has a bundle root/parent, a product, and is not
        // already held. Skip anything processed earlier this transaction.
        List<Asset> candidates = new List<Asset>();
        Set<Id> rootIds = new Set<Id>();
        Set<Id> prodIds = new Set<Id>();
        for (Asset a : assets) {
            if (a.Id == null || processed.contains(a.Id)) continue;
            if (a.Product2Id == null) continue;
            if (a.RLM_Asset_Status__c == STATUS_HELD) continue;
            Id root = (a.RootAssetId != null) ? a.RootAssetId : a.ParentId;
            if (root == null || root == a.Id) continue;   // roots / standalone: nothing to hold
            candidates.add(a);
            rootIds.add(root);
            prodIds.add(a.Product2Id);
        }
        if (candidates.isEmpty()) return;

        // Root products (to test for a OneTime hardware root).
        Map<Id, Id> rootProductByAsset = new Map<Id, Id>();
        for (Asset r : [SELECT Id, Product2Id FROM Asset WHERE Id IN :rootIds]) {
            rootProductByAsset.put(r.Id, r.Product2Id);
            if (r.Product2Id != null) prodIds.add(r.Product2Id);
        }
        Map<Id, Set<String>> modelsByProduct = sellingModelTypesByProduct(prodIds);

        Set<Id> holdIds = new Set<Id>();
        for (Asset a : candidates) {
            Id root = (a.RootAssetId != null) ? a.RootAssetId : a.ParentId;
            Id rootProd = rootProductByAsset.get(root);
            if (rootProd == null) continue;
            Boolean childIsSubscription = hasAny(modelsByProduct.get(a.Product2Id), SUBSCRIPTION_MODELS);
            Boolean rootIsOneTime       = hasAny(modelsByProduct.get(rootProd), ONE_TIME_MODELS);
            if (childIsSubscription && rootIsOneTime) holdIds.add(a.Id);
        }
        if (holdIds.isEmpty()) return;

        processed.addAll(holdIds);
        List<Asset> updates = new List<Asset>();
        for (Id id : holdIds) {
            updates.add(new Asset(
                Id = id,
                RLM_Asset_Status__c = STATUS_HELD,
                RLM_Billing_Start_Date__c = null
            ));
        }
        update updates;   // trigger context = system mode

        // If real billing groups already exist for these assets, hold them too.
        RLM_ShipmentFulfillmentService.holdBillingGroups(holdIds);
    }

    // ------------------------------------------------------------------
    // BillingScheduleGroup trigger entry point (after insert)
    // ------------------------------------------------------------------
    // Billing groups are generated after the order activates - often after the
    // asset already exists and was flagged BillingHeld. When a new group is born
    // for an asset that is currently held, push its override to the hold sentinel.
    public static void applyHoldToNewGroups(List<BillingScheduleGroup> groups) {
        if (groups == null || groups.isEmpty()) return;
        Set<Id> assetIds = new Set<Id>();
        for (BillingScheduleGroup g : groups) {
            if (g.ReferenceEntityId != null) assetIds.add(g.ReferenceEntityId);
        }
        if (assetIds.isEmpty()) return;

        Set<Id> heldAssetIds = new Set<Id>();
        for (Asset a : [
            SELECT Id FROM Asset
            WHERE Id IN :assetIds AND RLM_Asset_Status__c = :STATUS_HELD
        ]) {
            heldAssetIds.add(a.Id);
        }
        if (heldAssetIds.isEmpty()) return;

        RLM_ShipmentFulfillmentService.holdBillingGroups(heldAssetIds);
    }

    // ------------------------------------------------------------------
    // Helpers (system mode - no WITH USER_MODE; trigger context)
    // ------------------------------------------------------------------
    private static Map<Id, Set<String>> sellingModelTypesByProduct(Set<Id> prodIds) {
        Map<Id, Set<String>> m = new Map<Id, Set<String>>();
        if (prodIds == null || prodIds.isEmpty()) return m;
        for (ProductSellingModelOption o : [
            SELECT Product2Id, ProductSellingModel.SellingModelType
            FROM ProductSellingModelOption
            WHERE Product2Id IN :prodIds AND ProductSellingModel.SellingModelType != null
        ]) {
            if (!m.containsKey(o.Product2Id)) m.put(o.Product2Id, new Set<String>());
            m.get(o.Product2Id).add(o.ProductSellingModel.SellingModelType);
        }
        return m;
    }

    private static Boolean hasAny(Set<String> have, Set<String> wanted) {
        if (have == null) return false;
        for (String w : wanted) if (have.contains(w)) return true;
        return false;
    }
}
