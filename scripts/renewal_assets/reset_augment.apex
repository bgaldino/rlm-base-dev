/*
 * reset_augment.apex -- undo an augment_asset_lifecycle.apex run on specific assets.
 * Deletes the augment-created Change AssetActions (Type = 'Change') + their
 * AssetActionSources and the extra AssetStatePeriods, then restores each asset's
 * single Initial-Sale state period to span the full lifecycle and resets the Asset
 * header. Keeps the platform's Initial-Sale action untouched. Use to re-run augment
 * cleanly after a fix. Scope with ASSET_IDS.
 *
 * PROVENANCE GUARD: augment only creates Type = 'Change' actions. Any asset that
 * carries a non-Initial-Sale action whose Type is NOT 'Change' (a real Amendment,
 * Cancellation, etc.) has history reset cannot prove it created -- such an asset is
 * REFUSED (logged, untouched) rather than risk deleting real platform history.
 * Deletion itself is also restricted to Type = 'Change' for the same reason.
 *
 * Run with:  sf apex run --file scripts/renewal_assets/reset_augment.apex --target-org <alias>
 */
List<Id> ASSET_IDS = new List<Id>{ };   // put the Id(s) to un-augment here

if (ASSET_IDS.isEmpty()) { System.debug('reset_augment: no ASSET_IDS, no-op.'); return; }

// Refuse assets whose provenance can't be proven: any non-Initial-Sale action that
// is not Type='Change' is real platform history augment never creates.
Set<Id> unsafe = new Set<Id>();
for (AssetAction aa : [SELECT Id, AssetId FROM AssetAction
        WHERE AssetId IN :ASSET_IDS AND CategoryEnum != 'Initial Sale' AND Type != 'Change']) {
    unsafe.add(aa.AssetId);
}
List<Id> resetIds = new List<Id>();
for (Id aid : ASSET_IDS) { if (!unsafe.contains(aid)) resetIds.add(aid); }
if (!unsafe.isEmpty()) {
    System.debug('reset_augment: REFUSING ' + unsafe.size()
        + ' asset(s) with non-augment (non-Change) history: ' + unsafe);
}
if (resetIds.isEmpty()) { System.debug('reset_augment: nothing safe to reset, no-op.'); return; }

// Delete augment-created Change actions (Initial Sale + any real history stay) + their sources.
List<AssetAction> changeActs = [SELECT Id FROM AssetAction
    WHERE AssetId IN :resetIds AND CategoryEnum != 'Initial Sale' AND Type = 'Change'];
Set<Id> changeActIds = new Map<Id,AssetAction>(changeActs).keySet();
List<AssetActionSource> srcDel = [SELECT Id FROM AssetActionSource WHERE AssetActionId IN :changeActIds];
if (!srcDel.isEmpty())   delete srcDel;
if (!changeActs.isEmpty()) delete changeActs;

// For each asset: keep earliest state period (restore to full lifecycle), delete the rest.
Map<Id, Asset> assets = new Map<Id, Asset>([SELECT Id, LifecycleEndDate, Quantity FROM Asset WHERE Id IN :resetIds]);
List<AssetStatePeriod> allSp = [SELECT Id, AssetId, Quantity, Amount, Mrr, StartDate, EndDate
                                FROM AssetStatePeriod WHERE AssetId IN :resetIds ORDER BY StartDate];
Map<Id, AssetStatePeriod> keep = new Map<Id, AssetStatePeriod>();
List<AssetStatePeriod> spDel = new List<AssetStatePeriod>();
for (AssetStatePeriod sp : allSp) {
    if (!keep.containsKey(sp.AssetId)) keep.put(sp.AssetId, sp); else spDel.add(sp);
}
if (!spDel.isEmpty()) delete spDel;

List<AssetStatePeriod> spUpd = new List<AssetStatePeriod>();
List<Asset> aUpd = new List<Asset>();
for (Id aid : resetIds) {
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
System.debug('=== RESET COMPLETE === reset:' + resetIds.size()
    + ' refused:' + unsafe.size()
    + ' delActions:' + changeActs.size() + ' delSources:' + srcDel.size()
    + ' delStates:' + spDel.size() + ' restored:' + spUpd.size());
