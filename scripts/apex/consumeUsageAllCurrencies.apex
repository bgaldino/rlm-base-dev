// Record identical usage against every currency's asset, then start the usage
// orchestration that rates it. Part 1 of the multicurrency consume->rate test;
// run validateRatedUsage.apex afterwards to assert the results.
//
// Uses the repo's supported ingestion path -- RLM_UsageUploaderController
// (post_utils), which writes TransactionJournal records and validates the
// resource/UoM pairing -- rather than hand-building UsageSummary rows, so the
// test exercises what the demo actually uses.
//
// The SAME quantity is recorded for every currency on purpose: rating must then
// differ only by each currency's rate, which is exactly the property under test.
// Any per-currency divergence beyond the rate is a bug.
//
// Idempotency: re-running adds more usage. Clear TransactionJournal /
// UsageSummary first if you want a clean comparison.

public class UsageConsumeException extends Exception {}

final Decimal COMPUTE_MINUTES = 500;   // UR-CPUTIME  -- crosses QB-DB's 300+ override tier
final Decimal STORAGE_TB = 20;         // UR-DATASTORAGE
final String ORCHESTRATION_FLOW = 'RLM_OrchestrateUsageManagement';

// MUST be a date inside a PAST, COMPLETED billing period. Drawdown and final
// rating only settle once a period completes, and the current billing period
// stays open indefinitely -- usage booked into it sits at InProgress with the
// buckets untouched, which reads as "full discount, no drawdown" and is not a
// real result. Date.today() was used here originally and is exactly that trap.
final Date USAGE_DATE = Date.newInstance(2026, 6, 15);

// The seven currencies this test claims to cover. Checked explicitly: a
// non-empty result is NOT proof of coverage -- a single USD asset would
// otherwise let the run report success while exercising one currency.
final Set<String> EXPECTED_CURRENCIES = new Set<String>{
    'USD', 'GBP', 'EUR', 'AUD', 'CAD', 'CHF', 'JPY'
};

Map<String, Decimal> qtyByResource = new Map<String, Decimal>{
    'UR-CPUTIME' => COMPUTE_MINUTES,
    'UR-DATASTORAGE' => STORAGE_TB
};

List<Asset> assets = [
    SELECT Id, CurrencyIsoCode, Account.Name
    FROM Asset
    WHERE Product2.StockKeepingUnit = 'QB-DB'
    ORDER BY CurrencyIsoCode
];
if (assets.isEmpty()) {
    // NoDataFoundException can only be thrown from a VisualForce/Aura
    // context -- from anonymous Apex it fails with a confusing platform
    // error instead of this message.
    throw new UsageConsumeException(
        'No QB-DB asset exists. Build the regional assets first with '
        + 'scripts/build_quote_to_asset.py.');
}

Set<String> foundCurrencies = new Set<String>();
for (Asset a : assets) {
    foundCurrencies.add(a.CurrencyIsoCode);
}
Set<String> missingCurrencies = new Set<String>(EXPECTED_CURRENCIES);
missingCurrencies.removeAll(foundCurrencies);
if (!missingCurrencies.isEmpty()) {
    throw new IllegalArgumentException(
        'consumeUsageAllCurrencies covers ' + EXPECTED_CURRENCIES.size()
        + ' currencies but no QB-DB asset exists for: ' + missingCurrencies
        + '. Build the missing regional asset(s) first -- running against a subset'
        + ' would report success without exercising those currencies.');
}

Integer uploaded = 0;
List<String> failures = new List<String>();

// Resolve the code -> resource mapping ONCE. It is the same QB-DB resource set for
// every asset, so querying it inside the loop burned a SOQL call per asset on top
// of the two getUsageResourcesForAsset calls each iteration already makes
// (directly, and again inside bulkUploadUsage) -- enough QB-DB assets and the run
// dies on the 100-query governor limit.
Map<String, Id> resourceIdByCode = new Map<String, Id>();
for (ProductUsageResource pur : [
        SELECT UsageResourceId, UsageResource.Code
        FROM ProductUsageResource
        WHERE Product.StockKeepingUnit = 'QB-DB'
          AND UsageResource.Code IN :qtyByResource.keySet()
          AND Status = 'Active']) {
    resourceIdByCode.put(pur.UsageResource.Code, pur.UsageResourceId);
}

for (Asset a : assets) {
    // Resolve this asset's usage resources through the same controller the UI uses,
    // so an unrated or mis-mapped resource surfaces here rather than silently.
    List<RLM_UsageUploaderController.UsageResourceWrapper> resources =
        RLM_UsageUploaderController.getUsageResourcesForAsset(a.Id);

    List<RLM_UsageUploaderController.UsageEntry> entries =
        new List<RLM_UsageUploaderController.UsageEntry>();

    for (RLM_UsageUploaderController.UsageResourceWrapper w : resources) {
        Decimal qty = qtyByResource.get(w.resourceName);
        if (qty == null) {
            // resourceName is the label; fall back to matching on the code via query below
            continue;
        }
        RLM_UsageUploaderController.UsageEntry e = new RLM_UsageUploaderController.UsageEntry();
        e.usageResourceId = w.resourceId;
        e.usageResourceName = w.resourceName;
        e.quantity = qty;
        e.transactionDate = USAGE_DATE;
        entries.add(e);
    }

    // Rebuild from the code map whenever the wrapper result is INCOMPLETE, not
    // merely empty. A partial match previously uploaded one of the two required
    // resources and still started orchestration, so the missing resource surfaced
    // later as an apparent rating defect rather than a consume that never ran.
    if (entries.size() != qtyByResource.size()) {
        entries.clear();
        for (String code : qtyByResource.keySet()) {
            Id resourceId = resourceIdByCode.get(code);
            if (resourceId == null) { continue; }
            RLM_UsageUploaderController.UsageEntry e = new RLM_UsageUploaderController.UsageEntry();
            e.usageResourceId = resourceId;
            e.usageResourceName = code;
            e.quantity = qtyByResource.get(code);
            e.transactionDate = USAGE_DATE;
            entries.add(e);
        }
    }

    // Require the full declared set. Anything less is a partial consume, and the
    // whole point of this script is that every currency records identical usage.
    if (entries.size() != qtyByResource.size()) {
        failures.add(a.CurrencyIsoCode + ': resolved ' + entries.size() + ' of '
            + qtyByResource.size() + ' required usage resources ('
            + qtyByResource.keySet() + ') -- check for an inactive or missing '
            + 'ProductUsageResource on QB-DB');
        continue;
    }

    RLM_UsageUploaderController.BulkUploadResult res =
        RLM_UsageUploaderController.bulkUploadUsage(a.Id, entries);
    uploaded += res.successCount;
    if (res.errorCount > 0) {
        failures.add(a.CurrencyIsoCode + ': ' + String.join(res.errors, '; '));
    }
    System.debug('CONSUME: ' + a.CurrencyIsoCode + ' (' + a.Account.Name + ') -> '
        + res.successCount + ' journal(s), ' + res.errorCount + ' error(s)');
}

// Report the distinct currencies actually exercised, not the asset count: two
// assets in the same currency are not two currencies covered.
System.debug('CONSUME: uploaded ' + uploaded + ' journal(s) across '
    + foundCurrencies.size() + ' currenc' + (foundCurrencies.size() == 1 ? 'y' : 'ies')
    + ' (' + foundCurrencies + ') over ' + assets.size() + ' asset(s).');
// Fail BEFORE orchestration. Rating incomplete data and exiting successfully would
// send the user to validateRatedUsage.apex against a partial consume, where the
// missing currency looks like a rating defect rather than a consume that never ran.
if (!failures.isEmpty()) {
    throw new UsageConsumeException(
        'consumeUsageAllCurrencies: ' + failures.size() + ' asset(s) failed to record usage -- '
        + String.join(failures, ' | ')
        + '. Orchestration NOT started; fix these and re-run, otherwise the rating '
        + 'results would be validated against an incomplete consume.');
}

// Kick off the rating/drawdown orchestration. Asynchronous: give it time to
// finish before running validateRatedUsage.apex.
String status = RLM_UsageOrchestrationController.startOrchestration(ORCHESTRATION_FLOW);
System.debug('CONSUME: orchestration (' + ORCHESTRATION_FLOW + ') -> ' + status);
System.debug('CONSUME: wait for processing, then run scripts/apex/validateRatedUsage.apex');
