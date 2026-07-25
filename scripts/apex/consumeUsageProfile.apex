// Record the QuantumBit monthly usage profile against every anchor asset.
//
// The declared profile, which every documented demo figure is derived from:
//
//     CPU time      5,000 min  x 5 tokens/min  = 25,000 tokens
//     Data storage     50 TB   x 10 tokens/TB  =    500 tokens
//                                              ----------------
//                                                 25,500 tokens
//
// Set MULTIPLIER to 3 for the overage scenarios (76,500 tokens against a 25,000
// commitment plus a 10,000 anchor grant), or 1 for everything else.
//
// ⚠ TWO RULES, BOTH UNRECOVERABLE IF BROKEN:
//
//  1. Run this BEFORE orchestrating the target period. A UsageSummary that has
//     reached RatableSummaryComplete never reopens, and the first orchestration
//     pass on an account closes every past period EMPTY. Journals that arrive
//     afterwards stay Pending forever -- never aggregated, never rated, and
//     nothing reports an error; the rated summary simply reads zero.
//  2. Book into a PAST period. Drawdown and final rating only settle once a
//     period completes, and the current billing period stays open indefinitely,
//     so usage booked into it sits at InProgress with the buckets untouched --
//     which reads as "full discount, no drawdown" and is not a real result.
//
// Usage is ALWAYS recorded against the ANCHOR. A commitment is a rate modifier,
// not a consumption target: journals uploaded to a commit asset stay Pending
// forever. Resource codes differ per anchor, so the profile is expressed per SKU.
//
// Then: scripts/qb_usage.py orchestrate, then scripts/apex/validateRatedUsage.apex.

public class UsageConsumeException extends Exception {}

final Integer MULTIPLIER = 1;                              // 3 = overage scenarios
final Date USAGE_DATE = Date.newInstance(2026, 6, 15);     // must be a PAST period
final Set<String> ONLY_ACCOUNTS = new Set<String>();       // empty = every anchor

Map<String, Map<String, Decimal>> profile = new Map<String, Map<String, Decimal>>{
    'QB-DB'       => new Map<String, Decimal>{
        'UR-CPUTIME'     => 5000 * MULTIPLIER, 'UR-DATASTORAGE'     => 50 * MULTIPLIER},
    'QB-DB-TOKEN' => new Map<String, Decimal>{
        'UR-CPUTIME-TKN' => 5000 * MULTIPLIER, 'UR-DATASTORAGE-TKN' => 50 * MULTIPLIER}
};

// Resolve resources ONCE per anchor rather than per asset -- the set is identical
// for every asset of a given product, and querying inside the asset loop burns a
// SOQL call apiece on top of the two getUsageResourcesForAsset calls that
// bulkUploadUsage already makes.
Map<String, Map<String, Id>> resByAnchor = new Map<String, Map<String, Id>>();
for (ProductUsageResource pur : [SELECT UsageResourceId, UsageResource.Code,
                                        Product.StockKeepingUnit
                                 FROM ProductUsageResource
                                 WHERE Product.StockKeepingUnit IN :profile.keySet()
                                   AND Status = 'Active']) {
    String sku = pur.Product.StockKeepingUnit;
    if (!resByAnchor.containsKey(sku)) resByAnchor.put(sku, new Map<String, Id>());
    resByAnchor.get(sku).put(pur.UsageResource.Code, pur.UsageResourceId);
}

List<Asset> anchors = [SELECT Id, Account.Name, Product2.StockKeepingUnit FROM Asset
                       WHERE Product2.StockKeepingUnit IN :profile.keySet()
                       ORDER BY Account.Name];
if (anchors.isEmpty()) {
    throw new System.NoDataFoundException();
}

Integer uploaded = 0;
List<String> failures = new List<String>();

for (Asset a : anchors) {
    String sku = a.Product2.StockKeepingUnit;
    if (!ONLY_ACCOUNTS.isEmpty() && !ONLY_ACCOUNTS.contains(a.Account.Name)) { continue; }

    List<RLM_UsageUploaderController.UsageEntry> entries =
        new List<RLM_UsageUploaderController.UsageEntry>();
    for (String code : profile.get(sku).keySet()) {
        Id resourceId = resByAnchor.containsKey(sku) ? resByAnchor.get(sku).get(code) : null;
        if (resourceId == null) {
            failures.add(a.Account.Name + '/' + code + ': no Active ProductUsageResource');
            continue;
        }
        RLM_UsageUploaderController.UsageEntry e = new RLM_UsageUploaderController.UsageEntry();
        e.usageResourceId = resourceId;
        e.usageResourceName = code;
        e.quantity = profile.get(sku).get(code);
        e.transactionDate = USAGE_DATE;
        entries.add(e);
    }
    if (entries.isEmpty()) { continue; }

    try {
        RLM_UsageUploaderController.BulkUploadResult res =
            RLM_UsageUploaderController.bulkUploadUsage(a.Id, entries);
        uploaded += res.successCount;
        if (res.errorCount > 0) {
            failures.add(a.Account.Name + '/' + sku + ': ' + String.join(res.errors, '; '));
        }
        System.debug('CONSUME ' + a.Account.Name + ' / ' + sku + ' -> '
            + res.successCount + ' journal(s), ' + res.errorCount + ' error(s)');
    } catch (Exception ex) {
        failures.add(a.Account.Name + '/' + sku + ': ' + ex.getMessage());
    }
}

System.debug('CONSUME: ' + uploaded + ' journal(s) at x' + MULTIPLIER
    + ' on ' + String.valueOf(USAGE_DATE));

// Fail loudly rather than leaving a partial consume to be discovered later as an
// apparent rating defect.
if (!failures.isEmpty()) {
    throw new UsageConsumeException('consumeUsageProfile: ' + failures.size()
        + ' failure(s) -- ' + String.join(failures, ' | ')
        + '. Fix these and re-run; rating an incomplete consume produces results '
        + 'that look like rating defects.');
}
