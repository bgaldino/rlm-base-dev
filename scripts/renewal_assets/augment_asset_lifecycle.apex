/*
 * augment_asset_lifecycle.apex
 * ---------------------------------------------------------------------------
 * Adds a richer, contiguous lifecycle EVENT HISTORY on top of assets that
 * ALREADY exist -- e.g. ones produced by build_quote_to_asset.py /
 * build_renewal_buckets.py (Quote -> Order -> Activation). This does NOT create
 * assets and does NOT touch pricing; it is purely ADDITIVE on records the
 * platform already generated, so a single Initial-Sale asset gains the timeline
 * of a real multi-year subscription (Renewals / Upsells / Downsells).
 *
 * For each target asset it:
 *   1. Keeps the platform's own Initial-Sale AssetAction + AssetActionSource.
 *   2. Reuses that asset's REAL PricebookEntry / ProductSellingModel / UnitPrice
 *      (read from the Initial-Sale AssetActionSource) -- so the added events sit
 *      on the asset's actual selling model (e.g. Term Monthly), never a
 *      hardcoded one.
 *   3. Trims the existing full-window AssetStatePeriod to the first segment,
 *      then chains N contiguous, non-overlapping state periods.
 *   4. Inserts one Change AssetAction + AssetActionSource per event, placed at
 *      fractional positions inside the asset's OWN [LifecycleStartDate,
 *      LifecycleEndDate] -- so events stay valid whatever expiry bucket the
 *      asset is in.
 *   5. Updates the Asset header (CurrentQuantity / CurrentAmount / CurrentMrr)
 *      to the final running state.
 *
 * Quantity deltas are scaled to the asset's REAL base quantity, not absolute
 * numbers -- a Renewal renews the same qty, an Upsell adds, a Downsell removes.
 *
 * ── HOW TO TARGET ASSETS ──────────────────────────────────────────────────
 * Pick ONE of the two blocks below (leave the other empty). Both are empty by
 * default, so the script no-ops until you set one -- there is no built-in
 * account pattern to accidentally hit the wrong org's assets.
 *   A) ACCOUNT_NAME_LIKE -- augment every asset whose Account.Name matches a
 *      SOQL LIKE pattern, e.g. 'RenewalTest%'. Normal path after a run.
 *   B) ASSET_IDS -- an explicit list of Asset Ids (smoke test / re-run subset).
 * If both are set, ASSET_IDS wins.
 *
 * ── SMOKE FIRST ───────────────────────────────────────────────────────────
 * Prove it on ONE asset before scaling: put a single Id in ASSET_IDS, run,
 * verify the (N+1)-period chain (see the skill's Validation Checks), then
 * switch to ACCOUNT_NAME_LIKE for the full set.
 *
 * ── UNDO ──────────────────────────────────────────────────────────────────
 * The run is additive and NOT de-duped -- running it twice on the same assets
 * layers a second series. To re-run cleanly, undo first with reset_augment.apex.
 *
 * Run with:  sf apex run --file scripts/renewal_assets/augment_asset_lifecycle.apex --target-org <alias>
 *
 * Governor headroom: ~21 DML rows per asset (trim 1 + N actions + N sources +
 * N states + 1 header). A single execution comfortably handles a few hundred
 * assets (48 assets ~= 987 rows, well under the 10k limit).
 */

// ── TARGET SELECTION (pick ONE) ────────────────────────────────────────────
String   ACCOUNT_NAME_LIKE = '';                        // e.g. '<accountPrefix>%'  ('' to disable)
List<Id> ASSET_IDS         = new List<Id>{ };           // explicit Ids (wins if non-empty)

// ── EVENT STRUCTURE ────────────────────────────────────────────────────────
// One entry per added event, ordered earliest->latest. Initial Sale already
// exists at fraction 0, so these are the CHANGE events layered after it.
//   FRACS  = position as a fraction of the asset's [start,end] window
//   CATS   = AssetAction CategoryEnum: 'Renewals' | 'Upsells' | 'Downsells'
//   DELTAS = quantity change vs the running quantity (0 renews same qty)
List<Decimal> FRACS  = new List<Decimal>{ 0.20, 0.27, 0.40, 0.47, 0.60, 0.80 };
List<String>  CATS   = new List<String> { 'Renewals','Upsells','Renewals','Downsells','Renewals','Renewals' };
List<Integer> DELTAS = new List<Integer>{ 0,         2,        0,         -1,          0,         0 };

// ── Resolve target Asset Ids ───────────────────────────────────────────────
List<Id> targetIds = new List<Id>();
if (!ASSET_IDS.isEmpty()) {
    targetIds = ASSET_IDS;
} else if (String.isNotBlank(ACCOUNT_NAME_LIKE)) {
    for (Asset a : [SELECT Id FROM Asset WHERE Account.Name LIKE :ACCOUNT_NAME_LIKE]) {
        targetIds.add(a.Id);
    }
}
if (targetIds.isEmpty()) {
    System.debug('augment_asset_lifecycle: no target assets (set ACCOUNT_NAME_LIKE or ASSET_IDS). No-op.');
    return;
}
System.debug('augment_asset_lifecycle: targeting ' + targetIds.size() + ' asset(s).');

// ── Gather per-asset data ──────────────────────────────────────────────────
Map<Id, Asset> assetById = new Map<Id, Asset>([
    SELECT Id, Product2Id, AccountId, CurrentQuantity, Quantity,
           LifecycleStartDate, LifecycleEndDate
    FROM Asset WHERE Id IN :targetIds
]);

// Existing Initial-Sale actions (to reach their AssetActionSource for PBE/PSM/UnitPrice)
Map<Id, Id> initialActionByAsset = new Map<Id, Id>();
for (AssetAction aa : [SELECT Id, AssetId FROM AssetAction
                       WHERE AssetId IN :targetIds AND CategoryEnum = 'Initial Sale']) {
    initialActionByAsset.put(aa.AssetId, aa.Id);
}
// AssetActionSource carries PBE / PSM / UnitPrice
Map<Id, AssetActionSource> srcByAction = new Map<Id, AssetActionSource>();
for (AssetActionSource s : [SELECT Id, AssetActionId, PricebookEntryId, ProductSellingModelId, UnitPrice
                            FROM AssetActionSource WHERE AssetActionId IN :initialActionByAsset.values()]) {
    srcByAction.put(s.AssetActionId, s);
}
// Existing full-window state period (to trim to first segment)
Map<Id, AssetStatePeriod> stateByAsset = new Map<Id, AssetStatePeriod>();
for (AssetStatePeriod sp : [SELECT Id, AssetId, Quantity, Amount, Mrr, StartDate, EndDate
                            FROM AssetStatePeriod WHERE AssetId IN :targetIds ORDER BY StartDate]) {
    if (!stateByAsset.containsKey(sp.AssetId)) stateByAsset.put(sp.AssetId, sp); // keep earliest
}

List<AssetAction>       actionsIns = new List<AssetAction>();
List<AssetStatePeriod>  stateIns   = new List<AssetStatePeriod>();
List<AssetStatePeriod>  stateUpd   = new List<AssetStatePeriod>();
List<Asset>             assetUpd   = new List<Asset>();

// Track, per new action, the event index + asset so we can build sources after insert.
List<Id>      actionAssetIds = new List<Id>();
List<Integer> actionEvtIdx   = new List<Integer>();
Integer skipped = 0;

for (Id aid : targetIds) {
    Asset a = assetById.get(aid);
    if (a == null) { System.debug('skip (no asset) ' + aid); skipped++; continue; }
    Id initAct = initialActionByAsset.get(aid);
    AssetActionSource src = (initAct != null) ? srcByAction.get(initAct) : null;
    AssetStatePeriod  sp0 = stateByAsset.get(aid);
    if (src == null || sp0 == null || a.LifecycleStartDate == null || a.LifecycleEndDate == null) {
        System.debug('skip (missing src/state/lifecycle dates) ' + aid); skipped++; continue;
    }

    Decimal unitPrice = (src.UnitPrice != null && src.UnitPrice != 0) ? src.UnitPrice : 0;

    Datetime S = a.LifecycleStartDate;
    Datetime E = a.LifecycleEndDate;
    Long spanSec = (E.getTime() - S.getTime()) / 1000;

    // Base quantity = what was actually sold, read from the Initial-Sale state
    // period first. Do NOT trust Asset.CurrentQuantity as the primary source:
    // once an asset has expired the platform zeroes CurrentQuantity/CurrentMrr,
    // which would seed the whole event walk from 0. Prefer the first positive
    // of: Initial-Sale period qty -> CurrentQuantity -> Asset.Quantity -> 1.
    Decimal baseQty =
        (sp0.Quantity != null && sp0.Quantity > 0)         ? sp0.Quantity
      : (a.CurrentQuantity != null && a.CurrentQuantity > 0) ? a.CurrentQuantity
      : (a.Quantity != null && a.Quantity > 0)              ? a.Quantity
      : 1;

    // event datetimes from fractions
    List<Datetime> evtDates = new List<Datetime>();
    for (Decimal f : FRACS) {
        evtDates.add(S.addSeconds((Integer)(spanSec * f)));
    }

    // 1) Trim existing (first) state period to end just before the first event
    sp0.EndDate = evtDates[0].addSeconds(-1);
    stateUpd.add(sp0);

    // 2) Build Change actions + contiguous state periods
    Decimal running = baseQty;
    for (Integer i = 0; i < FRACS.size(); i++) {
        Integer delta = DELTAS[i];
        String  cat   = CATS[i];
        Datetime st   = evtDates[i];
        Datetime en   = (i < FRACS.size() - 1) ? evtDates[i+1].addSeconds(-1) : E;

        actionsIns.add(new AssetAction(
            AssetId = aid, Type = 'Change', CategoryEnum = cat,
            ActionDate = st, QuantityChange = delta,
            MrrChange = delta * unitPrice, Amount = delta * unitPrice
        ));
        actionAssetIds.add(aid); actionEvtIdx.add(i);

        running += delta;
        stateIns.add(new AssetStatePeriod(
            AssetId = aid, Quantity = running,
            Amount = running * unitPrice, Mrr = running * unitPrice,
            StartDate = st, EndDate = en
        ));
    }

    // 3) Update asset header to the final running state
    assetUpd.add(new Asset(Id = aid, CurrentQuantity = running,
                           CurrentAmount = running * unitPrice, CurrentMrr = running * unitPrice));
}

// ── DML ────────────────────────────────────────────────────────────────────
if (!stateUpd.isEmpty()) update stateUpd;
if (!actionsIns.isEmpty()) insert actionsIns;

// build sources for the just-inserted actions
List<AssetActionSource> srcIns = new List<AssetActionSource>();
for (Integer k = 0; k < actionsIns.size(); k++) {
    Id aid = actionAssetIds[k];
    Integer i = actionEvtIdx[k];
    Asset a = assetById.get(aid);
    AssetActionSource baseSrc = srcByAction.get(initialActionByAsset.get(aid));
    Decimal unitPrice = (baseSrc.UnitPrice != null && baseSrc.UnitPrice != 0) ? baseSrc.UnitPrice : 0;
    Long spanSec = (a.LifecycleEndDate.getTime() - a.LifecycleStartDate.getTime()) / 1000;
    Datetime st = a.LifecycleStartDate.addSeconds((Integer)(spanSec * FRACS[i]));
    Datetime en = (i < FRACS.size() - 1)
                  ? a.LifecycleStartDate.addSeconds((Integer)(spanSec * FRACS[i+1])).addSeconds(-1)
                  : a.LifecycleEndDate;
    Integer delta = DELTAS[i];
    srcIns.add(new AssetActionSource(
        AssetActionId = actionsIns[k].Id,
        TransactionDate = st, StartDate = st, EndDate = en,
        Quantity = delta, ProductAmount = delta * unitPrice,
        UnitPrice = unitPrice, NetUnitPrice = unitPrice, ListPrice = unitPrice,
        PeriodBoundary = 'Anniversary',
        PricebookEntryId = baseSrc.PricebookEntryId,
        ProductSellingModelId = baseSrc.ProductSellingModelId
    ));
}
if (!srcIns.isEmpty()) insert srcIns;
if (!stateIns.isEmpty()) insert stateIns;
if (!assetUpd.isEmpty()) update assetUpd;

System.debug('=== AUGMENT COMPLETE ===');
System.debug('assets processed: ' + assetUpd.size()
    + ' | skipped: ' + skipped
    + ' | actions +' + actionsIns.size()
    + ' | sources +' + srcIns.size()
    + ' | statePeriods +' + stateIns.size() + ' (trimmed ' + stateUpd.size() + ')');
