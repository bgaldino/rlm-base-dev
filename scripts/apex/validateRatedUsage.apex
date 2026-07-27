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
public class RatedUsageValidationException extends Exception {
}

List<String> problems = new List<String>();
List<String> passed = new List<String>();

Set<String> QB_USAGE_SKUS = new Set<String>{
    'QB-DB',
    'QB-DB-TOKEN',
    'QB-CMT-TKN-FLAT',
    'QB-CMT-TKN-BND',
    'QB-CMT-TKN-EACH',
    'QB-CMT-TKN-TIER',
    'QB-QTY-CMT',
    'QB-MTY-CMT',
    'QB-TOKENS-PACK',
    'QB-DAT-THPT'
};

// ⚠ THE RUN UNDER TEST. Set these to the period the consume script recorded into
// (consumeUsageProfile.apex USAGE_DATE / consumeUsageAllCurrencies.apex USAGE_DATE).
//
// Without an explicit window this validator picks up EVERY historical journal for
// the QuantumBit assets: a pending journal left by an earlier demo fails a clean
// run, and old rated summaries satisfy the arithmetic while the usage just
// uploaded never rated at all. Deriving the window from the journals themselves
// does not help -- it then spans all prior runs by construction.
final Date USAGE_PERIOD_START = Date.newInstance(2026, 6, 1);
final Date USAGE_PERIOD_END = Date.newInstance(2026, 6, 30);

// UsageRatableSummary.Status values (262 dev guide). Only RatingComplete means
// the row is settled; the rest are either in flight or failed.
final String RATING_COMPLETE = 'RatingComplete';
final Set<String> NONTERMINAL_STATUSES = new Set<String>{ 'New', 'SummaryCreated', 'InProgress' };

// ------------------------------------------------------------------ QB assets
// Resolved once and bound as a Set<Id>. TransactionJournal.ReferenceRecordId is
// POLYMORPHIC, and a semi-join against a polymorphic lookup does not resolve --
// it silently matches nothing while reporting success.
Map<Id, Asset> qbAssets = new Map<Id, Asset>(
    [
        SELECT Id, Account.Name, Product2.StockKeepingUnit
        FROM Asset
        WHERE Product2.StockKeepingUnit IN :QB_USAGE_SKUS
    ]
);
if (qbAssets.isEmpty()) {
    throw new RatedUsageValidationException(
        'No QuantumBit usage assets exist -- build them with ' +
        'scripts/build_quote_to_asset.py before validating rated usage.'
    );
}
Set<Id> qbAssetIds = qbAssets.keySet();

// ------------------------------------------------------------------ journals
// Every journal must have been absorbed into a summary. A journal left Pending
// is the signature of the most common failure: its period's UsageSummary had
// already reached RatableSummaryComplete, which NEVER reopens, so the usage is
// stranded permanently with no error reported anywhere.
// Bounded by the DECLARED window, not by whatever history exists. TransactionJournal
// .StartDate is a Datetime, so the bounds are expanded to cover the whole end day.
// GMT, not newInstance(): billing-period boundaries are stored as UTC midnights, while
// newInstance() builds in the RUNNING USER's timezone. On a GMT-7 org that shifts the
// window 7h and it selects the NEXT period instead of the declared one.
Datetime windowFrom = Datetime.newInstanceGmt(USAGE_PERIOD_START, Time.newInstance(0, 0, 0, 0));
Datetime windowTo = Datetime.newInstanceGmt(USAGE_PERIOD_END.addDays(1), Time.newInstance(0, 0, 0, 0));

List<TransactionJournal> journals = [
    SELECT
        Id,
        Status,
        StartDate,
        EndDate,
        UsageResourceId,
        UsageResource.Code,
        AccountId,
        Account.Name,
        Quantity,
        ReferenceRecordId
    FROM TransactionJournal
    WHERE
        UsageType = 'UsageManagement'
        AND ReferenceRecordId IN :qbAssetIds
        AND StartDate >= :windowFrom
        AND StartDate < :windowTo
];
if (journals.isEmpty()) {
    throw new RatedUsageValidationException(
        'No TransactionJournal records against QuantumBit usage assets between ' +
            String.valueOf(USAGE_PERIOD_START) +
            ' and ' +
            String.valueOf(USAGE_PERIOD_END) +
            ' -- run scripts/apex/consumeUsageProfile.apex first, or correct ' +
            'USAGE_PERIOD_START/END to the period it recorded into.'
    );
}

// Correlate the summaries to THIS run by the asset+resource pairs the journals
// touched, within the declared window above.
// Keyed by ASSET, not account. An account can hold more than one asset for the
// same SKU/resource -- reachable via --allow-existing-asset in
// build_quote_to_asset.py -- and an account-level key lets a summary from one
// asset mark an unrated journal on another asset as covered.
Set<String> journalKeys = new Set<String>(); // assetId|usageResourceId
List<String> stranded = new List<String>();
for (TransactionJournal j : journals) {
    journalKeys.add(j.ReferenceRecordId + '|' + j.UsageResourceId);
    if (j.Status != 'Processed') {
        stranded.add(
            j.Account.Name +
                '/' +
                j.UsageResource.Code +
                ' (' +
                String.valueOf(j.StartDate).left(10) +
                ', ' +
                j.Status +
                ')'
        );
    }
}
if (!stranded.isEmpty()) {
    problems.add(
        'TransactionJournal rows never aggregated (' +
            stranded.size() +
            '): ' +
            String.join(stranded, ', ') +
            ' -- their period almost certainly closed before the usage was recorded. A summary' +
            ' at RatableSummaryComplete never reopens; consume BEFORE orchestrating that period.'
    );
} else {
    passed.add('all ' + journals.size() + ' QuantumBit transaction journals were aggregated');
}

// ------------------------------------------------------------------- summaries
// Consumption that reached a summary must actually carry a rated amount. The
// summary must START INSIDE the declared window -- the same predicate the
// journals use above. Testing for mere overlap (even unpadded) always admits the
// ADJACENT OPEN period, which sits at InProgress by definition and never settles,
// so a correct run would be reported as "orchestration has not settled".
List<UsageRatableSummary> rated = [
    SELECT
        Id,
        Account.Name,
        AccountId,
        AssetId,
        UsageResourceId,
        UsageResource.Code,
        StartDateTime,
        EndDateTime,
        TierQuantity,
        OverageQuantity,
        NetUnitRate,
        TotalAmount,
        Status
    FROM UsageRatableSummary
    WHERE
        Asset.Product2.StockKeepingUnit IN :QB_USAGE_SKUS
        AND StartDateTime >= :windowFrom
        AND StartDateTime < :windowTo
];

// Keep only rows belonging to an asset+resource this run actually produced.
List<UsageRatableSummary> inScope = new List<UsageRatableSummary>();
for (UsageRatableSummary r : rated) {
    if (journalKeys.contains(r.AssetId + '|' + r.UsageResourceId))
        inScope.add(r);
}
// Per-KEY coverage, not merely "some summary exists". Checking only
// inScope.isEmpty() means one asset/resource stream (say one of seven
// currencies) can produce no summary at all while the others do, and the missing
// one passes unnoticed -- which is exactly the multicurrency failure mode.
Set<String> representedKeys = new Set<String>();
for (UsageRatableSummary r : inScope) {
    representedKeys.add(r.AssetId + '|' + r.UsageResourceId);
}
Set<String> uncoveredKeys = new Set<String>(journalKeys);
uncoveredKeys.removeAll(representedKeys);
if (!uncoveredKeys.isEmpty()) {
    // Resolve the ids to something readable.
    Map<String, String> labelByKey = new Map<String, String>();
    for (TransactionJournal j : journals) {
        labelByKey.put(
            j.ReferenceRecordId + '|' + j.UsageResourceId,
            j.Account.Name + '/' + j.UsageResource.Code + ' [asset ' + j.ReferenceRecordId + ']'
        );
    }
    List<String> uncovered = new List<String>();
    for (String k : uncoveredKeys) {
        uncovered.add(labelByKey.containsKey(k) ? labelByKey.get(k) : k);
    }
    problems.add(
        uncoveredKeys.size() +
            ' of ' +
            journalKeys.size() +
            ' recorded usage ' +
            'stream(s) produced NO UsageRatableSummary in this period: ' +
            String.join(uncovered, ', ') +
            ' -- that usage was recorded but never rated.'
    );
}

if (inScope.isEmpty()) {
    problems.add(
        'No UsageRatableSummary covers the account/resource/period this run recorded. ' +
            'Either the orchestration has not finished (re-run it and wait), or every journal ' +
            'stranded -- see above.'
    );
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
        problems.add(
            'UsageRatableSummary rows with Status=RatingFailed (' +
                failedRating.size() +
                '): ' +
                String.join(failedRating, ', ')
        );
    }
    if (!unsettled.isEmpty()) {
        problems.add(
            'UsageRatableSummary rows have not finished rating (' +
                unsettled.size() +
                '): ' +
                String.join(unsettled, ', ') +
                ' -- orchestration has not settled. Re-run it and wait before validating.'
        );
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
        if (r.OverageQuantity != null && r.OverageQuantity > 0)
            withQty.add(r);
    }
    // Zero overage is a LEGITIMATE settled result, not a failure: a grant or
    // commitment can absorb the usage entirely (scenario 6 records 50 GB against
    // the shipped 100 GB pack grant). Previously this was reported as a problem
    // while the message itself conceded it was expected -- so the validator could
    // not pass on every documented scenario.
    //
    // What must still be true is that the usage went SOMEWHERE: a settled summary
    // with no overage and no bucket consumption means nothing drew down at all.
    if (withQty.isEmpty() && !settled.isEmpty()) {
        // Scoped to the assets whose summaries actually settled in THIS run. Summing
        // across every QB asset let a bucket consumed by an earlier demo -- or by a
        // different asset entirely -- vouch for usage that never drew down.
        Set<Id> settledAssetIds = new Set<Id>();
        for (UsageRatableSummary r : settled) {
            settledAssetIds.add(r.AssetId);
        }
        Decimal totalConsumed = 0;
        for (AggregateResult ar : [
            SELECT SUM(ConsumedEntitlement) c
            FROM UsageEntitlementBucket
            WHERE TransactionUsageEntitlement.AssetId IN :settledAssetIds
        ]) {
            Decimal c = (Decimal) ar.get('c');
            if (c != null)
                totalConsumed += c;
        }
        if (totalConsumed > 0) {
            passed.add(
                settled.size() +
                    ' settled summar(ies) with zero overage -- usage was ' +
                    'fully absorbed by a grant/commitment (' +
                    totalConsumed +
                    ' drawn down)'
            );
        } else {
            problems.add(
                'Settled summaries carry no overage AND no bucket was drawn down -- ' +
                    'the usage reached a summary but nothing consumed it. Expected either an ' +
                    'overage amount or grant/commitment drawdown.'
            );
        }
    } else if (withQty.isEmpty() && unsettled.isEmpty() && failedRating.isEmpty()) {
        problems.add(
            'No settled UsageRatableSummary exists for this run at all -- the ' +
            'orchestration has not produced rated amounts.'
        );
    }
    List<String> mismatched = new List<String>();
    Integer checkedRows = 0;
    for (UsageRatableSummary r : withQty) {
        if (r.NetUnitRate == null || r.TotalAmount == null) {
            mismatched.add(
                r.Account.Name +
                    '/' +
                    r.UsageResource.Code +
                    ' has overage ' +
                    r.OverageQuantity +
                    ' but no rate/amount'
            );
            continue;
        }
        checkedRows++;
        Decimal expected = (r.OverageQuantity * r.NetUnitRate).setScale(4);
        Decimal actual = r.TotalAmount.setScale(4);
        // Tolerance absorbs the platform's own float noise (an exact 34,850 is
        // stored as 34849.9999998), not a genuine pricing difference.
        if ((expected - actual).abs() > 0.01) {
            mismatched.add(
                r.Account.Name +
                    '/' +
                    r.UsageResource.Code +
                    ' overage=' +
                    r.OverageQuantity +
                    ' x rate=' +
                    r.NetUnitRate +
                    ' = ' +
                    expected +
                    ' but TotalAmount=' +
                    actual +
                    ' (tier=' +
                    r.TierQuantity +
                    ')'
            );
        }
    }
    if (!mismatched.isEmpty()) {
        problems.add(
            'UsageRatableSummary amount != overage quantity x net unit rate: ' + String.join(mismatched, '; ')
        );
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
    WHERE AssetId IN :qbAssetIds OR RelatedObjectId IN :qbAssetIds
]) {
    if (!anchorToCommitments.containsKey(link.RelatedObjectId)) {
        anchorToCommitments.put(link.RelatedObjectId, new Set<Id>());
    }
    anchorToCommitments.get(link.RelatedObjectId).add(link.AssetId);
}

// Aggregate per ASSET -- an asset can have several buckets, so accumulate
// rather than overwrite.
//
// SCOPE LIMIT: unlike the journal and summary queries above, this is NOT bounded by
// the declared window. UsageEntitlementBucket does carry EffectiveStartDateTime /
// EffectiveEndDateTime, so it could be -- but a bucket's effective period is not
// necessarily the rating period, and choosing the predicate blind is how the summary
// query above ended up selecting the WRONG period. So: consume into ONE period per
// asset. Re-consuming the same asset into a second period sums both periods' buckets
// here and the draw-order assertion below is then evaluated against cross-period
// totals, which is not what it claims to check.
Map<Id, Decimal> anchorConsumedByAsset = new Map<Id, Decimal>();
Map<Id, Decimal> commitBalanceByAsset = new Map<Id, Decimal>();
Map<Id, Decimal> commitConsumedByAsset = new Map<Id, Decimal>();
for (UsageEntitlementBucket b : [
    SELECT
        ConsumedEntitlement,
        BucketBalance,
        TransactionUsageEntitlement.AssetId,
        TransactionUsageEntitlement.UsageModelType
    FROM UsageEntitlementBucket
    WHERE TransactionUsageEntitlement.AssetId IN :qbAssetIds
]) {
    Id assetId = b.TransactionUsageEntitlement.AssetId;
    String model = b.TransactionUsageEntitlement.UsageModelType;
    Decimal consumed = b.ConsumedEntitlement == null ? 0 : b.ConsumedEntitlement;
    Decimal balance = b.BucketBalance == null ? 0 : b.BucketBalance;
    if (model == 'Anchor') {
        anchorConsumedByAsset.put(
            assetId,
            (anchorConsumedByAsset.containsKey(assetId) ? anchorConsumedByAsset.get(assetId) : 0) + consumed
        );
    } else if (model == 'Commit') {
        commitBalanceByAsset.put(
            assetId,
            (commitBalanceByAsset.containsKey(assetId) ? commitBalanceByAsset.get(assetId) : 0) + balance
        );
        commitConsumedByAsset.put(
            assetId,
            (commitConsumedByAsset.containsKey(assetId) ? commitConsumedByAsset.get(assetId) : 0) + consumed
        );
    }
}

List<String> drawOrder = new List<String>();
Integer exercisedPairs = 0;
for (Id anchorAssetId : anchorToCommitments.keySet()) {
    Decimal anchorConsumed = anchorConsumedByAsset.containsKey(anchorAssetId)
        ? anchorConsumedByAsset.get(anchorAssetId)
        : 0;
    for (Id commitAssetId : anchorToCommitments.get(anchorAssetId)) {
        Decimal commitBalance = commitBalanceByAsset.containsKey(commitAssetId)
            ? commitBalanceByAsset.get(commitAssetId)
            : 0;
        Decimal commitConsumed = commitConsumedByAsset.containsKey(commitAssetId)
            ? commitConsumedByAsset.get(commitAssetId)
            : 0;
        if (commitConsumed > 0)
            exercisedPairs++;
        if (anchorConsumed > 0 && commitBalance > 0) {
            String acct = qbAssets.containsKey(anchorAssetId)
                ? qbAssets.get(anchorAssetId).Account.Name
                : String.valueOf(anchorAssetId);
            String commitSku = qbAssets.containsKey(commitAssetId)
                ? qbAssets.get(commitAssetId).Product2.StockKeepingUnit
                : String.valueOf(commitAssetId);
            drawOrder.add(
                acct +
                    ': anchor grant drew ' +
                    anchorConsumed +
                    ' while linked commitment ' +
                    commitSku +
                    ' still had ' +
                    commitBalance +
                    ' available'
            );
        }
    }
}
if (!drawOrder.isEmpty()) {
    problems.add(
        'Anchor grant consumed before the commitment was exhausted (usage would bill ' +
            'at the undiscounted rate): ' +
            String.join(drawOrder, '; ')
    );
} else if (exercisedPairs > 0) {
    // Only claim this passed when a commitment was ACTUALLY drawn down. An
    // untouched commitment proves nothing about ordering.
    passed.add(
        'commitment buckets drew before anchor grants across ' + exercisedPairs + ' exercised commitment/anchor pair(s)'
    );
} else if (!anchorToCommitments.isEmpty()) {
    passed.add(
        'SKIPPED commitment draw-order: ' +
            anchorToCommitments.size() +
            ' linked pair(s) exist but no commitment bucket was consumed'
    );
} else {
    passed.add('SKIPPED commitment draw-order: no UsageCmtAssetRelatedObj links exist');
}

// --------------------------------------------------------------------- report
for (String s : passed) {
    System.debug('PASS: ' + s);
}
if (!problems.isEmpty()) {
    String msg = 'Rated usage validation FAILED (' + problems.size() + ' problem(s)):';
    for (String p : problems) {
        msg += '\n  - ' + p;
    }
    msg +=
        '\n\nPassed ' +
        passed.size() +
        ' other check(s). If the orchestration is still ' +
        'running, wait and re-run -- rating and drawdown only settle once a period COMPLETES, ' +
        'and the current billing period stays open.';
    throw new RatedUsageValidationException(msg);
}
System.debug('RATED USAGE VALIDATION PASSED -- ' + passed.size() + ' check(s).');
