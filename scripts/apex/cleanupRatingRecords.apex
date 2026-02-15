// ============================================================================
// cleanupRatingRecords.apex
// ============================================================================
// Deletes all rating-related records in reverse dependency order for clean
// re-testing of the prepare_rating flow.
//
// Usage:
//   sf apex run --target-org <alias> --file scripts/apex/cleanupRatingRecords.apex
//   cci task run execute_anon --path scripts/apex/cleanupRatingRecords.apex --org <alias>
//
// Scope:
//   Deletes: ProductUsageGrant, ProductUsageResourcePolicy,
//            ProductUsageResource, UsagePrdGrantBindingPolicy,
//            RatingFrequencyPolicy, UsageOveragePolicy, UsageCommitmentPolicy
//   Does NOT delete: UnitOfMeasure, UnitOfMeasureClass (managed by qb-pcm),
//                    UsageResource, UsageResourceBillingPolicy (managed by qb-billing),
//                    UsageGrantRenewalPolicy, UsageGrantRolloverPolicy (managed by qb-billing)
//
// API 260 Notes:
//   - PUR deactivation must follow reverse activation order:
//     1. Non-Token PUR with TokenResourceId → Inactive
//     2. Token PUR → Inactive
//     3. Non-Token PUR without TokenResourceId → Inactive
//   - Active PURs cannot be deleted; must be set to Inactive first.
//   - Children (PUG, PURP) must be deleted before parent PUR.
// ============================================================================

// Step 1: Delete ProductUsageGrant (children of PUR)
List<ProductUsageGrant> activePugs = [SELECT Id, Status FROM ProductUsageGrant WHERE Status = 'Active'];
if (!activePugs.isEmpty()) {
    for (ProductUsageGrant p : activePugs) { p.Status = 'Inactive'; }
    update activePugs;
}
List<ProductUsageGrant> allPugs = [SELECT Id FROM ProductUsageGrant];
if (!allPugs.isEmpty()) { delete allPugs; System.debug('Deleted ' + allPugs.size() + ' ProductUsageGrant.'); }

// Step 2: Delete ProductUsageResourcePolicy (children of PUR)
List<ProductUsageResourcePolicy> allPurps = [SELECT Id FROM ProductUsageResourcePolicy];
if (!allPurps.isEmpty()) { delete allPurps; System.debug('Deleted ' + allPurps.size() + ' ProductUsageResourcePolicy.'); }

// Step 3: Deactivate PUR in reverse activation order, then delete
// 3a: Non-Token PUR with TokenResourceId → Inactive
List<ProductUsageResource> withTokPurs = [
    SELECT Id, Status FROM ProductUsageResource
    WHERE Status = 'Active' AND TokenResourceId != null AND UsageResource.Category != 'Token'
];
if (!withTokPurs.isEmpty()) {
    for (ProductUsageResource p : withTokPurs) { p.Status = 'Inactive'; }
    update withTokPurs;
    System.debug('Deactivated ' + withTokPurs.size() + ' PUR (with TokenResourceId).');
}

// 3b: Token PUR → Inactive
List<ProductUsageResource> tokPurs = [
    SELECT Id, Status FROM ProductUsageResource
    WHERE Status = 'Active' AND UsageResource.Category = 'Token'
];
if (!tokPurs.isEmpty()) {
    for (ProductUsageResource p : tokPurs) { p.Status = 'Inactive'; }
    update tokPurs;
    System.debug('Deactivated ' + tokPurs.size() + ' Token PUR.');
}

// 3c: Remaining Active PUR → Inactive
List<ProductUsageResource> remPurs = [
    SELECT Id, Status FROM ProductUsageResource WHERE Status = 'Active'
];
if (!remPurs.isEmpty()) {
    for (ProductUsageResource p : remPurs) { p.Status = 'Inactive'; }
    update remPurs;
    System.debug('Deactivated ' + remPurs.size() + ' remaining PUR.');
}

// 3d: Delete all PUR
List<ProductUsageResource> allPurs = [SELECT Id FROM ProductUsageResource];
if (!allPurs.isEmpty()) { delete allPurs; System.debug('Deleted ' + allPurs.size() + ' ProductUsageResource.'); }

// Step 4: Delete UsagePrdGrantBindingPolicy
List<UsagePrdGrantBindingPolicy> bindings = [SELECT Id FROM UsagePrdGrantBindingPolicy];
if (!bindings.isEmpty()) { delete bindings; System.debug('Deleted ' + bindings.size() + ' UsagePrdGrantBindingPolicy.'); }

// Step 5: Delete RatingFrequencyPolicy
List<RatingFrequencyPolicy> rfps = [SELECT Id FROM RatingFrequencyPolicy];
if (!rfps.isEmpty()) { delete rfps; System.debug('Deleted ' + rfps.size() + ' RatingFrequencyPolicy.'); }

// Step 6: Delete UsageOveragePolicy
List<UsageOveragePolicy> ops = [SELECT Id FROM UsageOveragePolicy];
if (!ops.isEmpty()) { delete ops; System.debug('Deleted ' + ops.size() + ' UsageOveragePolicy.'); }

// Step 7: Delete UsageCommitmentPolicy
List<UsageCommitmentPolicy> ucps = [SELECT Id FROM UsageCommitmentPolicy];
if (!ucps.isEmpty()) { delete ucps; System.debug('Deleted ' + ucps.size() + ' UsageCommitmentPolicy.'); }

// Step 8: Empty recycle bin for all deleted objects
Database.emptyRecycleBin([SELECT Id FROM ProductUsageGrant WHERE IsDeleted = true ALL ROWS]);
Database.emptyRecycleBin([SELECT Id FROM ProductUsageResourcePolicy WHERE IsDeleted = true ALL ROWS]);
Database.emptyRecycleBin([SELECT Id FROM ProductUsageResource WHERE IsDeleted = true ALL ROWS]);

System.debug('Rating cleanup complete.');
