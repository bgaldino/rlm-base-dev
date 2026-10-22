// Create quarterly Maintenance Plan + MaintenanceAsset + MaintenanceWorkRule for Michael Reyes.
List<Account> accounts = [SELECT Id FROM Account WHERE Name = 'Michael Reyes' LIMIT 1];
if (accounts.isEmpty()) {
    System.debug('No Michael Reyes account');
} else {
    Id accountId = accounts[0].Id;
    List<Asset> planAssets = [
        SELECT Id, Name FROM Asset
        WHERE AccountId = :accountId
            AND Product2.StockKeepingUnit IN ('RTK-ESSENTIAL','RTK-HOME-PROT','RTK-HOME-PROT-PLUS')
        ORDER BY CreatedDate DESC LIMIT 1
    ];
    if (!planAssets.isEmpty()) {
        Asset planAsset = planAssets[0];
        WorkType quarterly = [SELECT Id FROM WorkType WHERE Name = 'Quarterly Pest Visit' LIMIT 1];
        List<MaintenancePlan> existing = [
            SELECT Id FROM MaintenancePlan WHERE AccountId = :accountId AND WorkTypeId = :quarterly.Id LIMIT 1
        ];
        MaintenancePlan mp;
        if (existing.isEmpty()) {
            mp = new MaintenancePlan(
                AccountId = accountId,
                WorkTypeId = quarterly.Id,
                StartDate = Date.today(),
                GenerationTimeframe = 12,
                GenerationTimeframeType = 'Months',
                NextSuggestedMaintenanceDate = Date.today().addDays(90),
                DoesAutoGenerateWorkOrders = true,
                WorkOrderGenerationMethod = 'WorkOrderPerAsset'
            );
            insert mp;
        } else {
            mp = existing[0];
        }
        if ([SELECT COUNT() FROM MaintenanceAsset WHERE MaintenancePlanId = :mp.Id AND AssetId = :planAsset.Id] == 0) {
            insert new MaintenanceAsset(MaintenancePlanId = mp.Id, AssetId = planAsset.Id, WorkTypeId = quarterly.Id);
        }
        if ([SELECT COUNT() FROM MaintenanceWorkRule WHERE ParentMaintenancePlanId = :mp.Id] == 0) {
            insert new MaintenanceWorkRule(
                ParentMaintenancePlanId = mp.Id,
                Title = 'Quarterly Pest Visit',
                WorkTypeId = quarterly.Id,
                SortOrder = 1,
                RecurrencePattern = 'FREQ=MONTHLY;INTERVAL=3'
            );
        }
        System.debug('Maintenance plan ready: ' + mp.Id);
    }
}
System.debug('setupRtkGrow complete');
