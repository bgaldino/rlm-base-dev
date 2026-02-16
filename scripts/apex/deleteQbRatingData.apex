// Delete qb-rating data in dependency order.
// Safe for empty orgs (no-op) and re-runs.
// Does NOT touch Product2, UnitOfMeasure, UnitOfMeasureClass, or UsageResource.
//
// Many objects have Status fields (Draft > Active > Inactive).
// Active records cannot be deleted; they must be set to Inactive first.
// PUR deactivation uses partial success + iteration due to platform constraint:
// "can't deactivate a PUR when related PURs on the same Product are active."

// 1. Deactivate Active PUGs
List<ProductUsageGrant> activePugs = [SELECT Id, Status FROM ProductUsageGrant WHERE Status = 'Active'];
if (!activePugs.isEmpty()) {
    for (ProductUsageGrant p : activePugs) { p.Status = 'Inactive'; }
    Database.update(activePugs, false);
    System.debug('Deactivated ' + activePugs.size() + ' Active PUGs.');
}

// 2. Delete all PUGs
List<ProductUsageGrant> allPugs = [SELECT Id FROM ProductUsageGrant];
if (!allPugs.isEmpty()) { delete allPugs; System.debug('Deleted ' + allPugs.size() + ' PUGs.'); }
else { System.debug('No PUGs to delete.'); }

// 3. Delete ProductUsageResourcePolicy
List<ProductUsageResourcePolicy> purps = [SELECT Id FROM ProductUsageResourcePolicy];
if (!purps.isEmpty()) { delete purps; System.debug('Deleted ' + purps.size() + ' PURPs.'); }
else { System.debug('No PURPs to delete.'); }

// 4. Delete RatingFrequencyPolicy
List<RatingFrequencyPolicy> rfps = [SELECT Id FROM RatingFrequencyPolicy];
if (!rfps.isEmpty()) { delete rfps; System.debug('Deleted ' + rfps.size() + ' RatingFrequencyPolicy.'); }

// 5. Delete UsagePrdGrantBindingPolicy
List<UsagePrdGrantBindingPolicy> ugbps = [SELECT Id FROM UsagePrdGrantBindingPolicy];
if (!ugbps.isEmpty()) { delete ugbps; System.debug('Deleted ' + ugbps.size() + ' UsagePrdGrantBindingPolicy.'); }

// 6. Deactivate Active PURs iteratively (platform constraint requires iteration)
for (Integer pass = 1; pass <= 5; pass++) {
    List<ProductUsageResource> activePurs = [SELECT Id, Status FROM ProductUsageResource WHERE Status = 'Active'];
    if (activePurs.isEmpty()) break;
    for (ProductUsageResource p : activePurs) { p.Status = 'Inactive'; }
    List<Database.SaveResult> results = Database.update(activePurs, false);
    Integer ok = 0;
    for (Database.SaveResult sr : results) { if (sr.isSuccess()) ok++; }
    System.debug('PUR deactivation pass ' + pass + ': ' + ok + '/' + activePurs.size() + ' succeeded.');
}

// 7. Delete all PURs
List<ProductUsageResource> allPurs = [SELECT Id FROM ProductUsageResource];
if (!allPurs.isEmpty()) { delete allPurs; System.debug('Deleted ' + allPurs.size() + ' PURs.'); }
else { System.debug('No PURs to delete.'); }

// 8. Deactivate and delete UsageGrantRenewalPolicy
List<UsageGrantRenewalPolicy> activeRenewals = [SELECT Id, Status FROM UsageGrantRenewalPolicy WHERE Status = 'Active'];
if (!activeRenewals.isEmpty()) {
    for (UsageGrantRenewalPolicy r : activeRenewals) { r.Status = 'Inactive'; }
    update activeRenewals;
}
List<UsageGrantRenewalPolicy> renewals = [SELECT Id FROM UsageGrantRenewalPolicy];
if (!renewals.isEmpty()) { delete renewals; System.debug('Deleted ' + renewals.size() + ' UsageGrantRenewalPolicy.'); }

// 9. Deactivate and delete UsageGrantRolloverPolicy
List<UsageGrantRolloverPolicy> activeRollovers = [SELECT Id, Status FROM UsageGrantRolloverPolicy WHERE Status = 'Active'];
if (!activeRollovers.isEmpty()) {
    for (UsageGrantRolloverPolicy r : activeRollovers) { r.Status = 'Inactive'; }
    update activeRollovers;
}
List<UsageGrantRolloverPolicy> rollovers = [SELECT Id FROM UsageGrantRolloverPolicy];
if (!rollovers.isEmpty()) { delete rollovers; System.debug('Deleted ' + rollovers.size() + ' UsageGrantRolloverPolicy.'); }

// 10. Delete UsageOveragePolicy (no Status field)
List<UsageOveragePolicy> overages = [SELECT Id FROM UsageOveragePolicy];
if (!overages.isEmpty()) { delete overages; System.debug('Deleted ' + overages.size() + ' UsageOveragePolicy.'); }

// 11. Delete UsageCommitmentPolicy (no Status field)
List<UsageCommitmentPolicy> commitments = [SELECT Id FROM UsageCommitmentPolicy];
if (!commitments.isEmpty()) { delete commitments; System.debug('Deleted ' + commitments.size() + ' UsageCommitmentPolicy.'); }

// 12. Deactivate and delete UsageResourceBillingPolicy
List<UsageResourceBillingPolicy> activeBillingPols = [SELECT Id, Status FROM UsageResourceBillingPolicy WHERE Status = 'Active'];
if (!activeBillingPols.isEmpty()) {
    for (UsageResourceBillingPolicy r : activeBillingPols) { r.Status = 'Inactive'; }
    update activeBillingPols;
}
List<UsageResourceBillingPolicy> billingPols = [SELECT Id FROM UsageResourceBillingPolicy];
if (!billingPols.isEmpty()) { delete billingPols; System.debug('Deleted ' + billingPols.size() + ' UsageResourceBillingPolicy.'); }

System.debug('qb-rating data cleanup complete.');
