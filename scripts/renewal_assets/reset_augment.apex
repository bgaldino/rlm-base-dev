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
 * RESTORE IS PREFLIGHTED, NOT UNCONDITIONAL: deleting the marked rows is safe, but
 * the restore step stretches the surviving earliest period back to LifecycleEndDate
 * and resets the header from it. That is only correct if the sole survivor is the
 * original Initial Sale. If REAL renewal/amendment history was added AFTER augment
 * (unmarked, so it survives the delete), stretching the Initial-Sale period would
 * overlap it and the header reset would clobber the current values. So before any
 * DML this script checks, per asset, that the SURVIVING (unmarked) records are
 * exactly one action + one state period; any asset that fails is REFUSED entirely
 * (no delete, no restore) and left untouched -- the same pristine contract augment
 * itself enforces.
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
Map<Id, Integer> markedActByAsset = new Map<Id, Integer>();
Map<Id, Integer> markedSpByAsset  = new Map<Id, Integer>();

List<AssetActionSource> srcDel = [SELECT Id, AssetActionId FROM AssetActionSource
    WHERE AssetActionId IN :actIds AND ExternalReference = :AUGMENT_MARKER];
for (AssetActionSource s : srcDel) augActIds.add(s.AssetActionId);

List<AssetAction> augActs = augActIds.isEmpty()
    ? new List<AssetAction>()
    : [SELECT Id, AssetId FROM AssetAction WHERE Id IN :augActIds];
Map<Id, Id> augActAsset = new Map<Id, Id>();   // marked actionId -> assetId
for (AssetAction a : augActs) {
    augActAsset.put(a.Id, a.AssetId);
    markedActByAsset.put(a.AssetId,
        (markedActByAsset.containsKey(a.AssetId) ? markedActByAsset.get(a.AssetId) : 0) + 1);
}

// Marked state periods = augment's added segments (the trimmed Initial-Sale period
// is NOT marked, so it survives).
List<AssetStatePeriod> spDel = [SELECT Id, AssetId FROM AssetStatePeriod
    WHERE AssetId IN :ASSET_IDS AND SegmentName = :AUGMENT_MARKER];
for (AssetStatePeriod sp : spDel)
    markedSpByAsset.put(sp.AssetId,
        (markedSpByAsset.containsKey(sp.AssetId) ? markedSpByAsset.get(sp.AssetId) : 0) + 1);

// Candidate = any asset carrying a marked record.
Set<Id> candidates = new Set<Id>();
candidates.addAll(markedActByAsset.keySet());
candidates.addAll(markedSpByAsset.keySet());
if (candidates.isEmpty()) {
    System.debug('reset_augment: no augment-marked records on these assets, no-op.');
    return;
}

// Totals per candidate, so we can derive the SURVIVING (unmarked) counts.
Map<Id, Integer> totalActByAsset = new Map<Id, Integer>();
for (AggregateResult ar : [SELECT AssetId aid, COUNT(Id) c FROM AssetAction
                           WHERE AssetId IN :candidates GROUP BY AssetId])
    totalActByAsset.put((Id) ar.get('aid'), (Integer) ar.get('c'));
Map<Id, Integer> totalSpByAsset = new Map<Id, Integer>();
for (AggregateResult ar : [SELECT AssetId aid, COUNT(Id) c FROM AssetStatePeriod
                           WHERE AssetId IN :candidates GROUP BY AssetId])
    totalSpByAsset.put((Id) ar.get('aid'), (Integer) ar.get('c'));

// PREFLIGHT: an asset is eligible only if, once the marked rows go, the survivors are
// exactly the single Initial-Sale action + its one state period. Otherwise real
// post-augment history exists and the restore below would corrupt it -- refuse it.
Set<Id> eligible = new Set<Id>();
for (Id aid : candidates) {
    Integer unmarkedAct = (totalActByAsset.containsKey(aid) ? totalActByAsset.get(aid) : 0)
                        - (markedActByAsset.containsKey(aid) ? markedActByAsset.get(aid) : 0);
    Integer unmarkedSp  = (totalSpByAsset.containsKey(aid) ? totalSpByAsset.get(aid) : 0)
                        - (markedSpByAsset.containsKey(aid) ? markedSpByAsset.get(aid) : 0);
    if (unmarkedAct == 1 && unmarkedSp == 1) {
        eligible.add(aid);
    } else {
        System.debug('reset_augment: REFUSING ' + aid + ' -- post-augment history present '
            + '(surviving unmarked actions=' + unmarkedAct + ' statePeriods=' + unmarkedSp
            + ', expected 1 and 1). Left untouched.');
    }
}
if (eligible.isEmpty()) {
    System.debug('reset_augment: no eligible assets after preflight, no-op.');
    return;
}

// Scope every delete to eligible assets only -- a refused asset keeps all its rows.
List<AssetActionSource> srcDelE = new List<AssetActionSource>();
for (AssetActionSource s : srcDel)
    if (eligible.contains(augActAsset.get(s.AssetActionId))) srcDelE.add(s);
List<AssetAction> actDelE = new List<AssetAction>();
for (AssetAction a : augActs)
    if (eligible.contains(a.AssetId)) actDelE.add(a);
List<AssetStatePeriod> spDelE = new List<AssetStatePeriod>();
for (AssetStatePeriod sp : spDel)
    if (eligible.contains(sp.AssetId)) spDelE.add(sp);

if (!srcDelE.isEmpty()) delete srcDelE;
if (!actDelE.isEmpty()) delete actDelE;
if (!spDelE.isEmpty())  delete spDelE;

// Restore: for each eligible asset, stretch its (now sole) surviving Initial-Sale
// period back to the full lifecycle window and reset the header from it.
Map<Id, Asset> assets = new Map<Id, Asset>(
    [SELECT Id, LifecycleEndDate FROM Asset WHERE Id IN :eligible]);
Map<Id, AssetStatePeriod> keep = new Map<Id, AssetStatePeriod>();
for (AssetStatePeriod sp : [SELECT Id, AssetId, Quantity, Amount, Mrr, StartDate, EndDate
                            FROM AssetStatePeriod WHERE AssetId IN :eligible ORDER BY StartDate]) {
    if (!keep.containsKey(sp.AssetId)) keep.put(sp.AssetId, sp);   // earliest survivor
}
List<AssetStatePeriod> spUpd = new List<AssetStatePeriod>();
List<Asset> aUpd = new List<Asset>();
for (Id aid : eligible) {
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
System.debug('=== RESET COMPLETE === eligible:' + eligible.size()
    + ' delActions:' + actDelE.size() + ' delSources:' + srcDelE.size()
    + ' delStates:' + spDelE.size() + ' restored:' + spUpd.size());
