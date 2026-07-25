// Assert the RATED results of a usage run. Part 2 of the consume->rate test:
// run scripts/apex/consumeUsageProfile.apex (or consumeUsageAllCurrencies.apex)
// first, wait for the orchestration to finish, then run this.
//
// The consume scripts record usage and start the asynchronous orchestration; on
// their own they prove only that journals were written. This script is the
// assertion half -- it checks that the journals actually became rated amounts,
// that the amounts are arithmetically right, and that a linked commitment drew
// down before the anchor grant.
//
// SCOPING. Every query is scoped to the QuantumBit assets and to the period the
// journals under test actually cover. An unrelated product's pending journal, or
// a rated summary left over from an earlier demo, must not be able to fail -- or
// silently satisfy -- this run.
//
// Collects every failure and throws once with a full report, matching
// validateMulticurrencyRates.apex, so one run tells you everything.
//
// NB: Apex cannot construct the abstract built-in Exception -- a custom
// subclass is required.
public class RatedUsageValidationException extends Exception {}

List<String> problems = new List<String>();
List<String> passed = new List<String>();

Set<String> QB_USAGE_SKUS = new Set<String>{
    'QB-DB', 'QB-DB-TOKEN', 'QB-CMT-TKN-FLAT', 'QB-CMT-TKN-BND',
    'QB-CMT-TKN-EACH', 'QB-CMT-TKN-TIER', 'QB-QTY-CMT', 'QB-MTY-CMT',
    'QB-TOKENS-PACK', 'QB-DAT-THPT'
};

// UsageRatableSummary.Status values (262 dev guide). Only RatingComplete means
// the row is settled; the rest are either in flight or failed.
final String RATING_COMPLETE = 'RatingComplete';
final Set<String> NONTERMINAL_STATUSES = new Set<String>{
    'New', 'SummaryCreated', 'InProgress'
};

// ------------------------------------------------------------------ QB assets
// Resolved once and bound as a Set<Id>. TransactionJournal.ReferenceRecordId is
// POLYMORPHIC, and a semi-join against a polymorphic lookup does not resolve --
// it silently matches nothing while reporting success.
Map<Id, Asset> qbAssets = new Map<Id, Asset>([
    SELECT Id, Account.Name, Product2.StockKeepingUnit
    FROM Asset
    WHERE Product2.StockKeepingUnit IN :QB_USAGE_SKUS
]);
if (qbAssets.isEmpty()) {
    throw new RatedUsageValidationException(
        'No QuantumBit usage assets exist -- build them with '
        + 'scripts/build_quote_to_asset.py before validating rated usage.');
}
Set<Id> qbAssetIds = qbAssets.keySet();

// ------------------------------------------------------------------ journals
// Every journal must have been absorbed into a summary. A journal left Pending
// is the signature of the most common failure: its period's UsageSummary had
// already reached RatableSummaryComplete, which NEVER reopens, so the usage is
// stranded permanently with no error reported anywhere.
List<TransactionJournal> journals = [
    SELECT Id, Status, StartDate, EndDate, UsageResourceId, UsageResource.Code,
           AccountId, Account.Name, Quantity
    FROM TransactionJournal
    WHERE UsageType = 'UsageManagement'
      AND ReferenceRecordId IN :qbAssetIds
];
if (journals.isEmpty()) {
    throw new RatedUsageValidationException(
        'No TransactionJournal records against QuantumBit usage assets -- run '
        + 'scripts/apex/consumeUsageProfile.apex first.');
}

// Correlate the summaries to THIS run: the account+resource pairs the journals
// touched, and the date window they cover. Without this, a rated row from an
// earlier demo can satisfy the arithmetic section while the usage just uploaded
// never rated at all.
Set<String> journalKeys = new Set<String>();   // accountId|usageResourceId
Datetime windowStart, windowEnd;               // TransactionJournal.StartDate is a Datetime
List<String> stranded = new List<String>();
for (TransactionJournal j : journals) {
    journalKeys.add(j.AccountId + '|' + j.UsageResourceId);
    if (j.StartDate != null) {
        if (windowStart == null || j.StartDate < windowStart) windowStart = j.StartDate;
        if (windowEnd == null || j.StartDate > windowEnd) windowEnd = j.StartDate;
    }
    if (j.Status != 'Processed') {
        stranded.add(j.Account.Name + '/' + j.UsageResource.Code + ' ('
            + String.valueOf(j.StartDate).left(10) + ', ' + j.Status + ')');
    }
}
if (!stranded.isEmpty()) {
    problems.add('TransactionJournal rows never aggregated (' + stranded.size() + '): '
        + String.join(stranded, ', ')
        + ' -- their period almost certainly closed before the usage was recorded. A summary'
        + ' at RatableSummaryComplete never reopens; consume BEFORE orchestrating that period.');
} else {
    passed.add('all ' + journals.size() + ' QuantumBit transaction journals were aggregated');
}

// ------------------------------------------------------------------- summaries
// Consumption that reached a summary must actually carry a rated amount.
// Widen the window by a day at each end so a summary whose period boundary sits
// either side of the journal timestamps is still considered in scope.
Datetime windowFrom = windowStart == null ? null : windowStart.addDays(-1);
Datetime windowTo   = windowEnd   == null ? null : windowEnd.addDays(1);

List<UsageRatableSummary> rated = [
    SELECT Id, Account.Name, AccountId, UsageResourceId, UsageResource.Code,
           StartDateTime, EndDateTime, TierQuantity, OverageQuantity,
           NetUnitRate, TotalAmount, Status
    FROM UsageRatableSummary
    WHERE Asset.Product2.StockKeepingUnit IN :QB_USAGE_SKUS
      AND (StartDateTime = null OR StartDateTime <= :windowTo)
      AND (EndDateTime = null OR EndDateTime >= :windowFrom)
];

// Keep only rows belonging to an account+resource this run actually produced.
List<UsageRatableSummary> inScope = new List<UsageRatableSummary>();
for (UsageRatableSummary r : rated) {
    if (journalKeys.contains(r.AccountId + '|' + r.UsageResourceId)) inScope.add(r);
}
if (inScope.isEmpty()) {
    problems.add('No UsageRatableSummary covers the account/resource/period this run recorded. '
        + 'Either the orchestration has not finished (re-run it and wait), or every journal '
        + 'stranded -- see above.');
} else {
    // Rating must have SETTLED. A row still InProgress/SummaryCreated can satisfy
    // the arithmetic while drawdown is untouched, which would report success
    // before the asynchronous workflow finishes.
    List<String> unsettled = new List<String>();
    List<String> failedRating = new List<String>();
    List<UsageRatableSummary> settled = new List<UsageRatableSummary>();
    for (UsageRatableSummary r : inScope) {
        String label = r.Account.Name + '/' + r.UsageResource.Code + ' (' + r.Status + ')';
        if (r.Status == 'RatingFailed') {
            failedRating.add(label);
        } else if (NONTERMINAL_STATUSES.contains(r.Status)) {
            unsettled.add(label);
        } else if (r.Status == RATING_COMPLETE) {
            settled.add(r);
        }
        // 'Inactive' rows are neither settled nor in flight -- ignored on purpose.
    }
    if (!failedRating.isEmpty()) {
        problems.add('UsageRatableSummary rows with Status=RatingFailed ('
            + failedRating.size() + '): ' + String.join(failedRating, ', '));
    }
    if (!unsettled.isEmpty()) {
        problems.add('UsageRatableSummary rows have not finished rating ('
            + unsettled.size() + '): ' + String.join(unsettled, ', ')
            + ' -- orchestration has not settled. Re-run it and wait before validating.');
    }

    // A rated row must price what it OVERUSED. Per the 262 dev guide:
    //   NetUnitRate     -- rate per unit of usage entitlement OVERAGE
    //   OverageQuantity -- quantity of entitlements that were overused
    //   TotalAmount     -- total after calculating the OVERAGE at the net unit rate
    //   TierQuantity    -- the quantity that *impacts the net unit rate* (tier
    //                      selection), NOT the quantity billed
    // On an ordinary row OverageQuantity mirrors TierQuantity, so both appear to
    // work; they diverge exactly where a grant or commitment absorbs part of the
    // usage -- the scenarios this script exists to cover.
    List<UsageRatableSummary> withQty = new List<UsageRatableSummary>();
    for (UsageRatableSummary r : settled) {
        if (r.OverageQuantity != null && r.OverageQuantity > 0) withQty.add(r);
    }
    if (withQty.isEmpty() && unsettled.isEmpty() && failedRating.isEmpty()) {
        problems.add('No settled UsageRatableSummary carries an overage quantity for this run. '
            + 'If the usage was fully absorbed by a grant or commitment this is expected; '
            + 'otherwise the orchestration has not produced rated amounts.');
    }
    List<String> mismatched = new List<String>();
    Integer checkedRows = 0;
    for (UsageRatableSummary r : withQty) {
        if (r.NetUnitRate == null || r.TotalAmount == null) {
            mismatched.add(r.Account.Name + '/' + r.UsageResource.Code + ' has overage '
                + r.OverageQuantity + ' but no rate/amount');
            continue;
        }
        checkedRows++;
        Decimal expected = (r.OverageQuantity * r.NetUnitRate).setScale(4);
        Decimal actual = r.TotalAmount.setScale(4);
        // Tolerance absorbs the platform's own float noise (an exact 34,850 is
        // stored as 34849.9999998), not a genuine pricing difference.
        if ((expected - actual).abs() > 0.01) {
            mismatched.add(r.Account.Name + '/' + r.UsageResource.Code
                + ' overage=' + r.OverageQuantity + ' x rate=' + r.NetUnitRate
                + ' = ' + expected + ' but TotalAmount=' + actual
                + ' (tier=' + r.TierQuantity + ')');
        }
    }
    if (!mismatched.isEmpty()) {
        problems.add('UsageRatableSummary amount != overage quantity x net unit rate: '
            + String.join(mismatched, '; '));
    } else if (checkedRows > 0) {
        passed.add('all ' + checkedRows + ' settled rated summaries price at overage x net unit rate');
    }
}

// -------------------------------------------------------------------- buckets
// Where a commitment was linked, consumption must draw the COMMITMENT before the
// anchor grant. The reverse ordering silently bills at the undiscounted rate.
//
// Pairs are matched through the ACTUAL commitment->anchor relationship
// (UsageCmtAssetRelatedObj), not by account: an account can hold an unrelated
// commitment and anchor at the same time, and keying on account name both
// invents violations and lets multiple buckets overwrite each other.
Map<Id, Set<Id>> anchorToCommitments = new Map<Id, Set<Id>>();
for (UsageCmtAssetRelatedObj link : [
        SELECT AssetId, RelatedObjectId
        FROM UsageCmtAssetRelatedObj
        WHERE AssetId IN :qbAssetIds OR RelatedObjectId IN :qbAssetIds]) {
    if (!anchorToCommitments.containsKey(link.RelatedObjectId)) {
        anchorToCommitments.put(link.RelatedObjectId, new Set<Id>());
    }
    anchorToCommitments.get(link.RelatedObjectId).add(link.AssetId);
}

// Aggregate per ASSET -- an asset can have several buckets, so accumulate
// rather than overwrite.
Map<Id, Decimal> anchorConsumedByAsset = new Map<Id, Decimal>();
Map<Id, Decimal> commitBalanceByAsset = new Map<Id, Decimal>();
Map<Id, Decimal> commitConsumedByAsset = new Map<Id, Decimal>();
for (UsageEntitlementBucket b : [
        SELECT ConsumedEntitlement, BucketBalance,
               TransactionUsageEntitlement.AssetId,
               TransactionUsageEntitlement.UsageModelType
        FROM UsageEntitlementBucket
        WHERE TransactionUsageEntitlement.AssetId IN :qbAssetIds]) {
    Id assetId = b.TransactionUsageEntitlement.AssetId;
    String model = b.TransactionUsageEntitlement.UsageModelType;
    Decimal consumed = b.ConsumedEntitlement == null ? 0 : b.ConsumedEntitlement;
    Decimal balance = b.BucketBalance == null ? 0 : b.BucketBalance;
    if (model == 'Anchor') {
        anchorConsumedByAsset.put(assetId,
            (anchorConsumedByAsset.containsKey(assetId) ? anchorConsumedByAsset.get(assetId) : 0) + consumed);
    } else if (model == 'Commit') {
        commitBalanceByAsset.put(assetId,
            (commitBalanceByAsset.containsKey(assetId) ? commitBalanceByAsset.get(assetId) : 0) + balance);
        commitConsumedByAsset.put(assetId,
            (commitConsumedByAsset.containsKey(assetId) ? commitConsumedByAsset.get(assetId) : 0) + consumed);
    }
}

List<String> drawOrder = new List<String>();
Integer exercisedPairs = 0;
for (Id anchorAssetId : anchorToCommitments.keySet()) {
    Decimal anchorConsumed = anchorConsumedByAsset.containsKey(anchorAssetId)
        ? anchorConsumedByAsset.get(anchorAssetId) : 0;
    for (Id commitAssetId : anchorToCommitments.get(anchorAssetId)) {
        Decimal commitBalance = commitBalanceByAsset.containsKey(commitAssetId)
            ? commitBalanceByAsset.get(commitAssetId) : 0;
        Decimal commitConsumed = commitConsumedByAsset.containsKey(commitAssetId)
            ? commitConsumedByAsset.get(commitAssetId) : 0;
        if (commitConsumed > 0) exercisedPairs++;
        if (anchorConsumed > 0 && commitBalance > 0) {
            String acct = qbAssets.containsKey(anchorAssetId)
                ? qbAssets.get(anchorAssetId).Account.Name : String.valueOf(anchorAssetId);
            String commitSku = qbAssets.containsKey(commitAssetId)
                ? qbAssets.get(commitAssetId).Product2.StockKeepingUnit : String.valueOf(commitAssetId);
            drawOrder.add(acct + ': anchor grant drew ' + anchorConsumed
                + ' while linked commitment ' + commitSku + ' still had ' + commitBalance + ' available');
        }
    }
}
if (!drawOrder.isEmpty()) {
    problems.add('Anchor grant consumed before the commitment was exhausted (usage would bill '
        + 'at the undiscounted rate): ' + String.join(drawOrder, '; '));
} else if (exercisedPairs > 0) {
    // Only claim this passed when a commitment was ACTUALLY drawn down. An
    // untouched commitment proves nothing about ordering.
    passed.add('commitment buckets drew before anchor grants across '
        + exercisedPairs + ' exercised commitment/anchor pair(s)');
} else if (!anchorToCommitments.isEmpty()) {
    passed.add('SKIPPED commitment draw-order: ' + anchorToCommitments.size()
        + ' linked pair(s) exist but no commitment bucket was consumed');
} else {
    passed.add('SKIPPED commitment draw-order: no UsageCmtAssetRelatedObj links exist');
}

// --------------------------------------------------------------------- report
for (String s : passed) { System.debug('PASS: ' + s); }
if (!problems.isEmpty()) {
    String msg = 'Rated usage validation FAILED (' + problems.size() + ' problem(s)):';
    for (String p : problems) { msg += '\n  - ' + p; }
    msg += '\n\nPassed ' + passed.size() + ' other check(s). If the orchestration is still '
        + 'running, wait and re-run -- rating and drawdown only settle once a period COMPLETES, '
        + 'and the current billing period stays open.';
    throw new RatedUsageValidationException(msg);
}
System.debug('RATED USAGE VALIDATION PASSED -- ' + passed.size() + ' check(s).');
