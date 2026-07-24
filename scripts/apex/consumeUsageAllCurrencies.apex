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

final Decimal COMPUTE_MINUTES = 500;   // UR-CPUTIME  -- crosses QB-DB's 300+ override tier
final Decimal STORAGE_TB = 20;         // UR-DATASTORAGE
final String ORCHESTRATION_FLOW = 'RLM_OrchestrateUsageManagement';

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
    throw new System.NoDataFoundException();
}

Integer uploaded = 0;
List<String> failures = new List<String>();

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
        e.transactionDate = Date.today();
        entries.add(e);
    }

    if (entries.isEmpty()) {
        // Resource labels did not match the codes above -- resolve by code directly.
        for (ProductUsageResource pur : [
                SELECT UsageResourceId, UsageResource.Code
                FROM ProductUsageResource
                WHERE Product.StockKeepingUnit = 'QB-DB'
                  AND UsageResource.Code IN :qtyByResource.keySet()
                  AND Status = 'Active']) {
            RLM_UsageUploaderController.UsageEntry e = new RLM_UsageUploaderController.UsageEntry();
            e.usageResourceId = pur.UsageResourceId;
            e.usageResourceName = pur.UsageResource.Code;
            e.quantity = qtyByResource.get(pur.UsageResource.Code);
            e.transactionDate = Date.today();
            entries.add(e);
        }
    }

    if (entries.isEmpty()) {
        failures.add(a.CurrencyIsoCode + ': no usage resources resolved for the asset');
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

System.debug('CONSUME: uploaded ' + uploaded + ' journal(s) across ' + assets.size() + ' currency asset(s).');
if (!failures.isEmpty()) {
    System.debug('CONSUME: WARNINGS -- ' + String.join(failures, ' | '));
}

// Kick off the rating/drawdown orchestration. Asynchronous: give it time to
// finish before running validateRatedUsage.apex.
String status = RLM_UsageOrchestrationController.startOrchestration(ORCHESTRATION_FLOW);
System.debug('CONSUME: orchestration (' + ORCHESTRATION_FLOW + ') -> ' + status);
System.debug('CONSUME: wait for processing, then run scripts/apex/validateRatedUsage.apex');
