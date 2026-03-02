// Delete qb-rates data in dependency order.
// Safe for empty orgs (no-op) and re-runs.
// Does NOT touch Product2, ProductSellingModel, UnitOfMeasure, UnitOfMeasureClass, UsageResource, or Pricebook2.

// 1. Deactivate Active RateCardEntry (Active -> Inactive; platform allows only this transition)
List<RateCardEntry> activeRces = [SELECT Id, Status FROM RateCardEntry WHERE Status = 'Active'];
if (!activeRces.isEmpty()) {
    for (RateCardEntry rce : activeRces) { rce.Status = 'Inactive'; }
    update activeRces;
    System.debug('Deactivated ' + activeRces.size() + ' RateCardEntry records.');
}

// 2. Delete RateCardEntry (after deactivate; RABT may cascade or must be deleted while RCE is Draft in other flows). Then delete any remaining RABT.
List<RateCardEntry> rcesToDelete = [SELECT Id FROM RateCardEntry];
if (!rcesToDelete.isEmpty()) {
    delete rcesToDelete;
    System.debug('Deleted ' + rcesToDelete.size() + ' RateCardEntry records.');
}
List<RateAdjustmentByTier> rabts = [SELECT Id FROM RateAdjustmentByTier];
if (!rabts.isEmpty()) {
    delete rabts;
    System.debug('Deleted ' + rabts.size() + ' RateAdjustmentByTier records.');
}

// 3. Delete PriceBookRateCard (depends on RateCard)
List<PriceBookRateCard> pbrcs = [SELECT Id FROM PriceBookRateCard];
if (!pbrcs.isEmpty()) {
    delete pbrcs;
    System.debug('Deleted ' + pbrcs.size() + ' PriceBookRateCard records.');
} else {
    System.debug('No PriceBookRateCard records to delete.');
}

// 4. Delete RateCard
List<RateCard> rcs = [SELECT Id FROM RateCard];
if (!rcs.isEmpty()) {
    delete rcs;
    System.debug('Deleted ' + rcs.size() + ' RateCard records.');
} else {
    System.debug('No RateCard records to delete.');
}
