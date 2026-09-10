/*
 * reset_augment.apex -- undo an augment_asset_lifecycle.apex run on specific assets.
 * Deletes ONLY the records augment created -- identified by the provenance marker
 * augment stamps on every row (AssetActionSource.ExternalReference and
 * AssetStatePeriod.SegmentName = AUGMENT_MARKER) -- then restores each affected
 * asset's remaining (Initial-Sale) state period to span the full lifecycle and
 * resets the Asset header. Scope with ASSET_IDS.
 *
 * PROVENANCE BY MARKER, NOT BY TYPE: `Type = 'Change'` is a GENERIC AssetAction
 * type the platform also uses for real Renewals/Upsells/Downsells, so it is NOT a
 * safe signal. This script deletes strictly by the marker augment writes, so real
 * platform history (marked by nothing) is never touched -- even a legitimate Change
 * action on the same asset. Assets with no marked records are left completely alone.
 * The marker string MUST match AUGMENT_MARKER in augment_asset_lifecycle.apex.
 *
 * Run with:  sf apex run --file scripts/renewal_assets/reset_augment.apex --target-org <alias>
 */
List<Id> ASSET_IDS = new List<Id>{ };   // put the Id(s) to un-augment here
final String AUGMENT_MARKER = 'RLM_AUGMENT_LIFECYCLE';   // MUST match augment_asset_lifecycle.apex

if (ASSET_IDS.isEmpty()) { System.debug('reset_augment: no ASSET_IDS, no-op.'); return; }

// Actions on the target assets, so we can scope AssetActionSource by parent action.
Set<Id> actIds = new Map<Id, AssetAction>(
    [SELECT Id FROM AssetAction WHERE AssetId IN :ASSET_IDS]).keySet();

// Marked sources = the ones augment created. Their parent actions are augment's too.
Set<Id> augActIds = new Set<Id>();
Set<Id> touchedAssets = new Set<Id>();
List<AssetActionSource> srcDel = [SELECT Id, AssetActionId FROM AssetActionSource
    WHERE AssetActionId IN :actIds AND ExternalReference = :AUGMENT_MARKER];
for (AssetActionSource s : srcDel) augActIds.add(s.AssetActionId);
List<AssetAction> actDel = augActIds.isEmpty()
    ? new List<AssetAction>()
    : [SELECT Id, AssetId FROM AssetAction WHERE Id IN :augActIds];
for (AssetAction a : actDel) touchedAssets.add(a.AssetId);

// Marked state periods = augment's added segments (the trimmed Initial-Sale period
// is NOT marked, so it survives).
List<AssetStatePeriod> spDel = [SELECT Id, AssetId FROM AssetStatePeriod
    WHERE AssetId IN :ASSET_IDS AND SegmentName = :AUGMENT_MARKER];
for (AssetStatePeriod sp : spDel) touchedAssets.add(sp.AssetId);

if (touchedAssets.isEmpty()) {
    System.debug('reset_augment: no augment-marked records on these assets, no-op.');
    return;
}

if (!srcDel.isEmpty()) delete srcDel;
if (!actDel.isEmpty()) delete actDel;
if (!spDel.isEmpty())  delete spDel;

// Restore: for each touched asset, stretch its earliest SURVIVING (unmarked) period
// back to the full lifecycle window and reset the header from it.
Map<Id, Asset> assets = new Map<Id, Asset>(
    [SELECT Id, LifecycleEndDate FROM Asset WHERE Id IN :touchedAssets]);
Map<Id, AssetStatePeriod> keep = new Map<Id, AssetStatePeriod>();
for (AssetStatePeriod sp : [SELECT Id, AssetId, Quantity, Amount, Mrr, StartDate, EndDate
                            FROM AssetStatePeriod WHERE AssetId IN :touchedAssets ORDER BY StartDate]) {
    if (!keep.containsKey(sp.AssetId)) keep.put(sp.AssetId, sp);   // earliest survivor
}
List<AssetStatePeriod> spUpd = new List<AssetStatePeriod>();
List<Asset> aUpd = new List<Asset>();
for (Id aid : touchedAssets) {
    AssetStatePeriod sp0 = keep.get(aid);
    Asset a = assets.get(aid);
    if (sp0 != null && a != null) {
        sp0.EndDate = a.LifecycleEndDate;               // restore full window
        spUpd.add(sp0);
        aUpd.add(new Asset(Id = aid,
            CurrentQuantity = sp0.Quantity,
            CurrentAmount = sp0.Amount, CurrentMrr = sp0.Mrr));
    }
}
if (!spUpd.isEmpty()) update spUpd;
if (!aUpd.isEmpty())  update aUpd;
System.debug('=== RESET COMPLETE === assetsTouched:' + touchedAssets.size()
    + ' delActions:' + actDel.size() + ' delSources:' + srcDel.size()
    + ' delStates:' + spDel.size() + ' restored:' + spUpd.size());
