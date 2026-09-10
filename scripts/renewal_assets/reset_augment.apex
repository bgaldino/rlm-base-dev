/*
 * reset_augment.apex -- undo an augment_asset_lifecycle.apex run on specific assets.
 * Deletes the Change AssetActions + their AssetActionSources and the extra
 * AssetStatePeriods added by augment_asset_lifecycle.apex, then restores each
 * asset's single Initial-Sale state period to span the full lifecycle and resets
 * the Asset header. Keeps the platform's Initial-Sale action untouched. Use to
 * re-run augment cleanly after a fix. Scope with ASSET_IDS.
 *
 * Run with:  sf apex run --file scripts/renewal_assets/reset_augment.apex --target-org <alias>
 */
List<Id> ASSET_IDS = new List<Id>{ };   // put the Id(s) to un-augment here

if (ASSET_IDS.isEmpty()) { System.debug('reset_augment: no ASSET_IDS, no-op.'); return; }

// Delete Change actions (Initial Sale stays) + their sources.
List<AssetAction> changeActs = [SELECT Id FROM AssetAction
    WHERE AssetId IN :ASSET_IDS AND CategoryEnum != 'Initial Sale'];
Set<Id> changeActIds = new Map<Id,AssetAction>(changeActs).keySet();
List<AssetActionSource> srcDel = [SELECT Id FROM AssetActionSource WHERE AssetActionId IN :changeActIds];
if (!srcDel.isEmpty())   delete srcDel;
if (!changeActs.isEmpty()) delete changeActs;

// For each asset: keep earliest state period (restore to full lifecycle), delete the rest.
Map<Id, Asset> assets = new Map<Id, Asset>([SELECT Id, LifecycleEndDate, Quantity FROM Asset WHERE Id IN :ASSET_IDS]);
List<AssetStatePeriod> allSp = [SELECT Id, AssetId, Quantity, Amount, Mrr, StartDate, EndDate
                                FROM AssetStatePeriod WHERE AssetId IN :ASSET_IDS ORDER BY StartDate];
Map<Id, AssetStatePeriod> keep = new Map<Id, AssetStatePeriod>();
List<AssetStatePeriod> spDel = new List<AssetStatePeriod>();
for (AssetStatePeriod sp : allSp) {
    if (!keep.containsKey(sp.AssetId)) keep.put(sp.AssetId, sp); else spDel.add(sp);
}
if (!spDel.isEmpty()) delete spDel;

List<AssetStatePeriod> spUpd = new List<AssetStatePeriod>();
List<Asset> aUpd = new List<Asset>();
for (Id aid : ASSET_IDS) {
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
System.debug('=== RESET COMPLETE === assets:' + ASSET_IDS.size()
    + ' delActions:' + changeActs.size() + ' delSources:' + srcDel.size()
    + ' delStates:' + spDel.size() + ' restored:' + spUpd.size());
