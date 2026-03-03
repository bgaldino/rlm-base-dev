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

// 2. Delete RateCardEntry first, then any remaining RateAdjustmentByTier.
//
// RCE-before-RABT deletion order is intentional and required. An alternative approach —
// deleting RABT before RCE to respect FK dependency order — was evaluated, tested, and
// failed. Platform constraint: Salesforce rejects RABT deletion when its parent RCE is
// Inactive (INVALID_INPUT: "You can't delete this rate adjustment record because the
// related rate card entry is inactive"). Step 1 of this script deactivates Active RCEs
// to Inactive, which triggers this constraint for any subsequent RABT delete. Deleting
// RCE first cascades deletion of its child RABTs — the RABT query below is a safety-net
// no-op in normal operation. RABT-before-RCE only works when RCEs are still Draft (never
// deactivated), which is not guaranteed after prepare_rating runs.
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
