/**
 * Auto-applies the shipment-gated billing hold to software subscriptions created
 * under a one-time hardware bundle. Delegates to RLM_AssetBillingHoldHandler.
 * Fires on after update too because the platform derives RootAssetId after the
 * initial insert (assetization), so the bundle relationship may only be complete
 * on a follow-up update.
 */
trigger RLM_AssetBillingHold on Asset (after insert, after update) {
    RLM_AssetBillingHoldHandler.applyHold(Trigger.new);
}
