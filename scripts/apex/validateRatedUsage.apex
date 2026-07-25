// Assert the RATED results of a usage run. Part 2 of the consume->rate test:
// run scripts/apex/consumeUsageAllCurrencies.apex first, wait for the
// orchestration to finish, then run this.
//
// consumeUsageAllCurrencies records usage and starts the asynchronous
// orchestration; on its own it proves only that journals were written. This
// script is the assertion half -- it checks that the journals actually became
// rated amounts, and that the amounts are arithmetically right.
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

// ------------------------------------------------------------------ journals
// Every journal must have been absorbed into a summary. A journal left Pending
// is the signature of the most common failure: its period's UsageSummary had
// already reached RatableSummaryComplete, which NEVER reopens, so the usage is
// stranded permanently with no error reported anywhere.
List<TransactionJournal> journals = [
    SELECT Id, Status, StartDate, UsageResource.Code, Account.Name, Quantity
    FROM TransactionJournal
    WHERE UsageType = 'UsageManagement'
];
if (journals.isEmpty()) {
    throw new RatedUsageValidationException(
        'No TransactionJournal records -- run scripts/apex/consumeUsageAllCurrencies.apex first.');
}
List<String> stranded = new List<String>();
for (TransactionJournal j : journals) {
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
    passed.add('all ' + journals.size() + ' transaction journals were aggregated');
}

// ------------------------------------------------------------------- summaries
// Consumption that reached a summary must actually carry a rated amount.
List<UsageRatableSummary> rated = [
    SELECT Id, Account.Name, UsageResource.Code, StartDateTime, TierQuantity,
           OverageQuantity, NetUnitRate, TotalAmount, Status
    FROM UsageRatableSummary
    WHERE Asset.Product2.StockKeepingUnit IN :QB_USAGE_SKUS
];
List<UsageRatableSummary> withQty = new List<UsageRatableSummary>();
for (UsageRatableSummary r : rated) {
    if (r.TierQuantity != null && r.TierQuantity > 0) withQty.add(r);
}
if (withQty.isEmpty()) {
    problems.add('No UsageRatableSummary carries a quantity. Either the orchestration has not '
        + 'finished (re-run it and wait), or every journal stranded -- see above.');
} else {
    // A rated row must price what it summarised: amount = quantity x unit rate.
    List<String> mismatched = new List<String>();
    Integer checkedRows = 0;
    for (UsageRatableSummary r : withQty) {
        if (r.NetUnitRate == null || r.TotalAmount == null) {
            mismatched.add(r.Account.Name + '/' + r.UsageResource.Code + ' has quantity '
                + r.TierQuantity + ' but no rate/amount');
            continue;
        }
        checkedRows++;
        Decimal expected = (r.TierQuantity * r.NetUnitRate).setScale(4);
        Decimal actual = r.TotalAmount.setScale(4);
        // Tolerance absorbs the platform's own float noise (an exact 34,850 is
        // stored as 34849.9999998), not a genuine pricing difference.
        if ((expected - actual).abs() > 0.01) {
            mismatched.add(r.Account.Name + '/' + r.UsageResource.Code + ' qty=' + r.TierQuantity
                + ' x rate=' + r.NetUnitRate + ' = ' + expected + ' but TotalAmount=' + actual);
        }
    }
    if (!mismatched.isEmpty()) {
        problems.add('UsageRatableSummary amount != quantity x rate: '
            + String.join(mismatched, '; '));
    } else {
        passed.add('all ' + checkedRows + ' rated summaries price at quantity x unit rate');
    }
}

// -------------------------------------------------------------------- buckets
// Where a commitment was linked, consumption must draw the COMMITMENT before the
// anchor grant. The reverse ordering silently bills at the undiscounted rate.
Map<Id, Decimal> consumedByBucket = new Map<Id, Decimal>();
Map<Id, String> bucketSku = new Map<Id, String>();
Map<Id, String> bucketAccount = new Map<Id, String>();
for (UsageEntitlementBucket b : [
        SELECT Id, ConsumedEntitlement, BucketBalance,
               TransactionUsageEntitlement.Product.StockKeepingUnit,
               TransactionUsageEntitlement.Account.Name,
               TransactionUsageEntitlement.UsageModelType
        FROM UsageEntitlementBucket
        WHERE TransactionUsageEntitlement.Product.StockKeepingUnit IN :QB_USAGE_SKUS]) {
    if (b.ConsumedEntitlement == null) continue;
    consumedByBucket.put(b.Id, b.ConsumedEntitlement);
    bucketSku.put(b.Id, b.TransactionUsageEntitlement.Product.StockKeepingUnit);
    bucketAccount.put(b.Id, b.TransactionUsageEntitlement.Account.Name);
}
// Accounts that hold a commitment whose bucket was consumed while the paired
// anchor grant was also consumed AND the commitment still had balance.
List<String> drawOrder = new List<String>();
Map<String, Decimal> anchorConsumed = new Map<String, Decimal>();
Map<String, Decimal> commitBalance = new Map<String, Decimal>();
for (UsageEntitlementBucket b : [
        SELECT ConsumedEntitlement, BucketBalance,
               TransactionUsageEntitlement.Product.StockKeepingUnit,
               TransactionUsageEntitlement.Account.Name,
               TransactionUsageEntitlement.UsageModelType
        FROM UsageEntitlementBucket
        WHERE TransactionUsageEntitlement.Product.StockKeepingUnit IN :QB_USAGE_SKUS
          AND BucketBalance != null]) {
    String acct = b.TransactionUsageEntitlement.Account.Name;
    String model = b.TransactionUsageEntitlement.UsageModelType;
    if (model == 'Anchor' && b.ConsumedEntitlement != null && b.ConsumedEntitlement > 0) {
        anchorConsumed.put(acct, b.ConsumedEntitlement);
    }
    if (model == 'Commit' && b.BucketBalance != null && b.BucketBalance > 0) {
        commitBalance.put(acct, b.BucketBalance);
    }
}
for (String acct : anchorConsumed.keySet()) {
    if (commitBalance.containsKey(acct)) {
        drawOrder.add(acct + ': anchor grant drew ' + anchorConsumed.get(acct)
            + ' while the commitment still had ' + commitBalance.get(acct) + ' available');
    }
}
if (!drawOrder.isEmpty()) {
    problems.add('Anchor grant consumed before the commitment was exhausted (usage would bill '
        + 'at the undiscounted rate): ' + String.join(drawOrder, '; '));
} else if (!consumedByBucket.isEmpty()) {
    passed.add('commitment buckets draw before anchor grants across '
        + (new Set<String>(bucketAccount.values())).size() + ' account(s)');
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
