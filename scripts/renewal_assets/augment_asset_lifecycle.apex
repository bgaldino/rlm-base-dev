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
 *   2. Reuses that asset's REAL PricebookEntry / ProductSellingModel / pricing /
 *      PeriodBoundary (read from the Initial-Sale AssetActionSource) -- so the added
 *      events sit on the asset's actual selling model (e.g. Term Monthly) and billing
 *      alignment, never a hardcoded one. Amounts use the BOOKED (post-discount)
 *      per-unit figure from the Initial-Sale state period, never the list UnitPrice,
 *      so a discounted asset is not silently repriced to list.
 *   3. Trims the existing full-window AssetStatePeriod to the first segment,
 *      then chains N contiguous, non-overlapping state periods.
 *   4. Inserts one Change AssetAction + AssetActionSource per event, placed at
 *      fractional positions inside the asset's OWN [LifecycleStartDate,
 *      LifecycleEndDate] -- so events stay valid whatever expiry bucket the
 *      asset is in.
 *   5. Updates the Asset header (CurrentQuantity / CurrentAmount / CurrentMrr)
 *      to the final running state.
 *
 * Quantity deltas (DELTAS below) are ABSOLUTE unit changes applied to the running
 * quantity -- a Renewal renews the same qty (0), an Upsell adds (+n), a Downsell
 * removes (-n). They are NOT a fraction of the asset's base quantity, so tune them
 * to your base qty (e.g. +2 is a large move on a base of 1, trivial on 10000).
 *
 * PRISTINE ONLY: to avoid trimming/overlaying REAL platform history, an asset is
 * augmented only when it is pristine -- exactly one Initial-Sale action and exactly
 * one state period, with no other actions. Assets that already carry lifecycle
 * changes are skipped (logged), never modified.
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

// Durable provenance marker stamped on EVERY record this script creates, so
// reset_augment.apex can delete exactly (and only) its own rows -- never real
// platform history. AssetActionSource.ExternalReference and AssetStatePeriod
// .SegmentName are both writable strings the platform does not populate for a
// plain term asset. MUST match AUGMENT_MARKER in reset_augment.apex.
final String AUGMENT_MARKER = 'RLM_AUGMENT_LIFECYCLE';

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
// AssetActionSource carries PBE / PSM / pricing (list UnitPrice + post-discount
// NetUnitPrice + ListPrice) and the original PeriodBoundary -- all reused so the
// added events keep the asset's actual price, discount, and billing alignment.
Map<Id, AssetActionSource> srcByAction = new Map<Id, AssetActionSource>();
for (AssetActionSource s : [SELECT Id, AssetActionId, PricebookEntryId, ProductSellingModelId,
                            UnitPrice, NetUnitPrice, ListPrice, PeriodBoundary
                            FROM AssetActionSource WHERE AssetActionId IN :initialActionByAsset.values()]) {
    srcByAction.put(s.AssetActionId, s);
}
// Existing full-window state period (to trim to first segment)
Map<Id, AssetStatePeriod> stateByAsset = new Map<Id, AssetStatePeriod>();
Map<Id, Integer> statePeriodCount = new Map<Id, Integer>();
for (AssetStatePeriod sp : [SELECT Id, AssetId, Quantity, Amount, Mrr, StartDate, EndDate
                            FROM AssetStatePeriod WHERE AssetId IN :targetIds ORDER BY StartDate]) {
    if (!stateByAsset.containsKey(sp.AssetId)) stateByAsset.put(sp.AssetId, sp); // keep earliest
    statePeriodCount.put(sp.AssetId, (statePeriodCount.containsKey(sp.AssetId) ? statePeriodCount.get(sp.AssetId) : 0) + 1);
}
// Total AssetAction count per asset -- a pristine asset has exactly one (Initial Sale).
Map<Id, Integer> actionCount = new Map<Id, Integer>();
for (AggregateResult ar : [SELECT AssetId aid, COUNT(Id) c FROM AssetAction
                           WHERE AssetId IN :targetIds GROUP BY AssetId]) {
    actionCount.put((Id) ar.get('aid'), (Integer) ar.get('c'));
}

List<AssetAction>       actionsIns = new List<AssetAction>();
List<AssetStatePeriod>  stateIns   = new List<AssetStatePeriod>();
List<AssetStatePeriod>  stateUpd   = new List<AssetStatePeriod>();
List<Asset>             assetUpd   = new List<Asset>();

// Track, per new action, the event index + asset so we can build sources after insert.
List<Id>      actionAssetIds = new List<Id>();
List<Integer> actionEvtIdx   = new List<Integer>();
// Per-unit BOOKED (post-discount) amount per asset, reused by the source-build loop
// so both loops price identically and never fall back to list UnitPrice.
Map<Id, Decimal> perUnitAmtByAsset = new Map<Id, Decimal>();
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
    // PRISTINE guard: refuse assets that already carry lifecycle history. Only the
    // single Initial-Sale action and its one state period may exist -- otherwise
    // trimming sp0 and layering a chain would corrupt/erase REAL history.
    Integer nAct = actionCount.containsKey(aid) ? actionCount.get(aid) : 0;
    Integer nSp  = statePeriodCount.containsKey(aid) ? statePeriodCount.get(aid) : 0;
    if (nAct != 1 || nSp != 1) {
        System.debug('skip (not pristine: actions=' + nAct + ' statePeriods=' + nSp
            + ' -- expected 1 and 1) ' + aid); skipped++; continue;
    }

    // List (pre-discount) vs net (post-discount) per-unit price, from the source.
    Decimal listUnitPrice = (src.ListPrice != null && src.ListPrice != 0) ? src.ListPrice
                          : ((src.UnitPrice != null && src.UnitPrice != 0) ? src.UnitPrice : 0);
    Decimal netUnitPrice  = (src.NetUnitPrice != null && src.NetUnitPrice != 0) ? src.NetUnitPrice
                          : listUnitPrice;
    // Per-unit BOOKED amount from the Initial-Sale STATE PERIOD (Amount / Quantity) --
    // the actual, post-discount figure. AssetActionSource.UnitPrice is the pre-discount
    // list price, so a discounted asset must NOT be repriced to it. Fall back to the net
    // unit price only if the period carries no amount.
    Decimal perUnitAmount = (sp0.Amount != null && sp0.Quantity != null && sp0.Quantity != 0)
                          ? (sp0.Amount / sp0.Quantity) : netUnitPrice;
    perUnitAmtByAsset.put(aid, perUnitAmount);
    // Per-unit MONTHLY recurring revenue, taken from the Initial-Sale state period
    // (Mrr / Quantity). UnitPrice is per-term, not monthly (e.g. Term Annual unit
    // price 12000 is Mrr 1000), so MRR fields must NOT be qty * unitPrice.
    Decimal perUnitMrr = (sp0.Mrr != null && sp0.Quantity != null && sp0.Quantity != 0)
                         ? (sp0.Mrr / sp0.Quantity) : 0;

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
            MrrChange = delta * perUnitMrr, Amount = delta * perUnitAmount
        ));
        actionAssetIds.add(aid); actionEvtIdx.add(i);

        running += delta;
        stateIns.add(new AssetStatePeriod(
            AssetId = aid, Quantity = running,
            Amount = running * perUnitAmount, Mrr = running * perUnitMrr,
            StartDate = st, EndDate = en,
            SegmentName = AUGMENT_MARKER               // provenance marker for reset
        ));
    }

    // 3) Update asset header to the final running state -- but only when a state
    // period is actually current. Asset.CurrentQuantity/CurrentMrr mirror the CURRENT
    // period and are 0 when none is current (per the Asset object reference), which is
    // exactly the case for an already-expired or not-yet-started lifecycle window. Seed
    // the header from the running state only if now falls inside [S, E]; otherwise leave
    // Current* at 0 so an inactive asset is not shown as active.
    Boolean assetCurrent = (S == null || S <= System.now())
                        && (E == null || E >= System.now());
    assetUpd.add(new Asset(Id = aid,
        CurrentQuantity = assetCurrent ? running : 0,
        CurrentAmount   = assetCurrent ? running * perUnitAmount : 0,
        CurrentMrr      = assetCurrent ? running * perUnitMrr : 0));
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
    // Preserve the source's real pricing: list UnitPrice, post-discount NetUnitPrice,
    // and the booked per-unit amount (from the state period) for ProductAmount.
    Decimal listUnitPrice = (baseSrc.ListPrice != null && baseSrc.ListPrice != 0) ? baseSrc.ListPrice
                          : ((baseSrc.UnitPrice != null && baseSrc.UnitPrice != 0) ? baseSrc.UnitPrice : 0);
    Decimal netUnitPrice  = (baseSrc.NetUnitPrice != null && baseSrc.NetUnitPrice != 0) ? baseSrc.NetUnitPrice
                          : listUnitPrice;
    Decimal perUnitAmount = perUnitAmtByAsset.containsKey(aid) ? perUnitAmtByAsset.get(aid) : netUnitPrice;
    Long spanSec = (a.LifecycleEndDate.getTime() - a.LifecycleStartDate.getTime()) / 1000;
    Datetime st = a.LifecycleStartDate.addSeconds((Integer)(spanSec * FRACS[i]));
    Datetime en = (i < FRACS.size() - 1)
                  ? a.LifecycleStartDate.addSeconds((Integer)(spanSec * FRACS[i+1])).addSeconds(-1)
                  : a.LifecycleEndDate;
    Integer delta = DELTAS[i];
    srcIns.add(new AssetActionSource(
        AssetActionId = actionsIns[k].Id,
        TransactionDate = st, StartDate = st, EndDate = en,
        Quantity = delta, ProductAmount = delta * perUnitAmount,
        UnitPrice = listUnitPrice, NetUnitPrice = netUnitPrice, ListPrice = listUnitPrice,
        // Reuse the asset's original billing alignment, not a hardcoded 'Anniversary'
        // (assets built with AlignToCalendar/DayOfPeriod/LastDayOfPeriod keep theirs).
        PeriodBoundary = (baseSrc.PeriodBoundary != null ? baseSrc.PeriodBoundary : 'Anniversary'),
        PricebookEntryId = baseSrc.PricebookEntryId,
        ProductSellingModelId = baseSrc.ProductSellingModelId,
        ExternalReference = AUGMENT_MARKER             // provenance marker for reset
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
