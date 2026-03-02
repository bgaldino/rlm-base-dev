// ============================================================================
// activateRatingRecords.apex
// ============================================================================
// Activates rating-related records in the correct dependency order for API 260.
// Called by the activate_rating_records task in the prepare_rating CCI flow.
//
// Usage:
//   cci task run activate_rating_records --org <alias>
//   sf apex run --target-org <alias> --file scripts/apex/activateRatingRecords.apex
//
// Activation order (7 steps):
//   1. UnitOfMeasureClass > Active  (safety net; SFDMU Pass 2 handles this)
//   2. UsageResource > Active       (safety net; SFDMU Pass 2 handles this)
//   2.5. Remove only duplicate PURs that have NO PUG/PURP children (so activation can succeed; we never delete PUG or PURP)
//   3. Pre-populate TokenResourceId on Draft non-Token PURs that are missing it
//   4. Token PUR > Active           (must precede Step 5; products with Token PURs
//                                    require them Active before usage PURs can activate)
//   5. ALL non-Token PUR > clear+activate (TokenResourceId=null + Status='Active')
//   6. ProductUsageGrant > Active
//
// API 260 Platform Behaviors:
//   - Auto-population: The platform auto-populates TokenResourceId on non-Token
//     PURs during DML (insert or update) when their UsageResource has a Token
//     association (UsageResource.TokenResourceId is set). This is independent
//     of QB-TOKEN's Status — it's based on the UsageResource relationship.
//
//   - Activation conflict: Auto-population fires during the same DML that sets
//     Status='Active', then fails because TokenResourceId "can't be edited
//     when the PUR is Active".
//
//   - Clear+activate workaround: Setting TokenResourceId=null AND Status='Active'
//     in a single DML prevents auto-population — BUT only when TokenResourceId
//     was non-null before the update. A null>null "clear" does NOT prevent
//     auto-population.
//
//   - Pre-populate + clear+activate: For PURs where TokenResourceId was not set
//     at insert time (QB-DB;UR-*, QB-QTY-CMT;UR-*), we first SET it to the
//     correct value (from UsageResource.TokenResourceId) while the PUR is Draft,
//     then use clear+activate. The non-null>null change prevents auto-population.
//
//   - CommitmentSpend + Usage PURs: QB-MTY-CMT;UR-CPUTIME and
//     QB-MTY-CMT;UR-DATASTORAGE cannot be activated in API 260. These
//     optional PURs are excluded from the data plan (258>260 migration gap).
//
// Idempotency:
//   Step 2.5 queries ALL PURs (including Active) so the overlap-detection logic can
//   correctly prefer Active over Draft when both exist for the same Product+UsageResource.
//   Only Draft PURs with no PUG/PURP children are deleted; Active records are never touched.
//   All other steps filter on Status != 'Active' and are safe no-ops when records are
//   already Active.
// ============================================================================

// Step 1: Activate UnitOfMeasureClass (safety net)
List<UnitOfMeasureClass> uomcs = [SELECT Id, Status FROM UnitOfMeasureClass WHERE Status != 'Active'];
if (!uomcs.isEmpty()) {
    for (UnitOfMeasureClass uomc : uomcs) { uomc.Status = 'Active'; }
    update uomcs;
    System.debug('Activated ' + uomcs.size() + ' UnitOfMeasureClass record(s).');
} else {
    System.debug('All UnitOfMeasureClass records are already Active.');
}

// Step 2: Activate UsageResource (safety net)
List<UsageResource> urs = [SELECT Id, Status FROM UsageResource WHERE Status != 'Active'];
if (!urs.isEmpty()) {
    for (UsageResource ur : urs) { ur.Status = 'Active'; }
    update urs;
    System.debug('Activated ' + urs.size() + ' UsageResource record(s).');
} else {
    System.debug('All UsageResource records are already Active.');
}

// Step 2.5: Remove only duplicate PURs that have NO PUG/PURP children.
// Re-running the plan can insert duplicate Draft PURs (same Product+UsageResource+overlapping period).
// The platform blocks activation with "effective period overlaps". We delete only duplicate PURs
// that have zero ProductUsageGrant and zero ProductUsageResourcePolicy children — so we never
// delete PUG or PURP. Duplicate PURs inserted on a second load have no children; the originals have them.
// Query all PURs ordered by (ProductId, UsageResourceId, EffectiveStartDate) so overlapping
// duplicates within each Product+UsageResource group are adjacent — enables O(n) linear scan
// rather than O(n^2) nested loop. Active PURs are included because the selection rule
// (Active wins over Draft) requires seeing both statuses in the same group.
List<ProductUsageResource> allPurs = [
    SELECT Id, ProductId, UsageResourceId, EffectiveStartDate, EffectiveEndDate, Status
    FROM ProductUsageResource
    ORDER BY ProductId, UsageResourceId, EffectiveStartDate ASC NULLS FIRST, EffectiveEndDate ASC NULLS LAST
];
Set<Id> duplicatePurIds = new Set<Id>();
ProductUsageResource currentPur = null;
Datetime currentStart = null;
Datetime currentEnd = null;
for (ProductUsageResource pur : allPurs) {
    // Start a new (ProductId, UsageResourceId) group, or initialise on the first record.
    if (currentPur == null ||
        currentPur.ProductId != pur.ProductId ||
        currentPur.UsageResourceId != pur.UsageResourceId) {
        currentPur   = pur;
        currentStart = pur.EffectiveStartDate != null ? (Datetime)pur.EffectiveStartDate : Datetime.newInstance(1900, 1, 1, 0, 0, 0);
        currentEnd   = pur.EffectiveEndDate   != null ? (Datetime)pur.EffectiveEndDate   : Datetime.newInstance(4000, 12, 31, 23, 59, 59);
        continue;
    }
    // Skip records already identified as duplicates.
    if (duplicatePurIds.contains(pur.Id)) continue;
    Datetime purStart = pur.EffectiveStartDate != null ? (Datetime)pur.EffectiveStartDate : Datetime.newInstance(1900, 1, 1, 0, 0, 0);
    Datetime purEnd   = pur.EffectiveEndDate   != null ? (Datetime)pur.EffectiveEndDate   : Datetime.newInstance(4000, 12, 31, 23, 59, 59);
    Boolean overlaps = (currentStart <= purEnd) && (currentEnd >= purStart);
    if (!overlaps) {
        // No overlap — this PUR starts a new non-overlapping period; it becomes the reference.
        currentPur   = pur;
        currentStart = purStart;
        currentEnd   = purEnd;
        continue;
    }
    // Overlapping PURs in the same group: decide which is the duplicate.
    // Rule: Active wins over Draft; ties broken by lower Id (earlier insert).
    if (currentPur.Status == 'Active' && pur.Status != 'Active') {
        duplicatePurIds.add(pur.Id);
    } else if (pur.Status == 'Active' && currentPur.Status != 'Active') {
        duplicatePurIds.add(currentPur.Id);
        currentPur   = pur;
        currentStart = purStart;
    } else if (currentPur.Id < pur.Id) {
        duplicatePurIds.add(pur.Id);
    } else {
        duplicatePurIds.add(currentPur.Id);
        currentPur   = pur;
        currentStart = purStart;
    }
    // Extend the survivor's effective end to cover any chained overlaps.
    if (purEnd > currentEnd) currentEnd = purEnd;
}
Set<Id> purIdsWithChildren = new Set<Id>();
for (AggregateResult ar : [SELECT ProductUsageResourceId purId FROM ProductUsageGrant GROUP BY ProductUsageResourceId]) {
    purIdsWithChildren.add((Id)ar.get('purId'));
}
for (AggregateResult ar : [SELECT ProductUsageResourceId purId FROM ProductUsageResourcePolicy GROUP BY ProductUsageResourceId]) {
    purIdsWithChildren.add((Id)ar.get('purId'));
}
if (!duplicatePurIds.isEmpty()) {
    List<ProductUsageResource> purToDelete = new List<ProductUsageResource>();
    for (ProductUsageResource pur : allPurs) {
        if (duplicatePurIds.contains(pur.Id) && pur.Status == 'Draft' && !purIdsWithChildren.contains(pur.Id)) {
            purToDelete.add(pur);
        }
    }
    if (!purToDelete.isEmpty()) {
        delete purToDelete;
        System.debug('Deleted ' + purToDelete.size() + ' duplicate Draft PUR(s) with no PUG/PURP children (effective period overlap).');
    }
}

// Step 3: Pre-populate TokenResourceId on Draft non-Token PURs where it's null.
// Some PURs (QB-DB;UR-*, QB-QTY-CMT;UR-*) don't get TokenResourceId auto-populated
// at SFDMU insert time. For clear+activate to work in Step 4, TokenResourceId must
// be non-null so the null assignment is a REAL change (not null>null no-op).
// We set it to the UsageResource's TokenResourceId value while the PUR is Draft.
List<ProductUsageResource> needsTokenRes = [
    SELECT Id, TokenResourceId, UsageResource.TokenResourceId
    FROM ProductUsageResource
    WHERE Status != 'Active'
    AND TokenResourceId = null
    AND UsageResource.Category != 'Token'
    AND UsageResource.TokenResourceId != null
];
if (!needsTokenRes.isEmpty()) {
    for (ProductUsageResource pur : needsTokenRes) {
        pur.TokenResourceId = pur.UsageResource.TokenResourceId;
    }
    List<Database.SaveResult> results = Database.update(needsTokenRes, false);
    Integer successCount = 0;
    for (Integer i = 0; i < results.size(); i++) {
        if (results[i].isSuccess()) {
            successCount++;
        } else {
            for (Database.Error err : results[i].getErrors()) {
                System.debug(LoggingLevel.ERROR, 'Failed to pre-populate TokenResourceId on PUR ' +
                    needsTokenRes[i].Id + ': ' + err.getMessage());
            }
        }
    }
    System.debug('Pre-populated TokenResourceId on ' + successCount + '/' + needsTokenRes.size() + ' Draft PUR(s).');
} else {
    System.debug('All non-Token PURs already have TokenResourceId set (or no Token association).');
}

// Step 4: Activate Token PURs (UsageResource.Category='Token').
// Token PURs must be activated BEFORE non-Token PURs because products with a
// Token PUR counterpart require it to be Active before their usage PURs can activate.
// Token PURs are not affected by TokenResourceId auto-population.
List<ProductUsageResource> tokenPurs = [
    SELECT Id, Status
    FROM ProductUsageResource
    WHERE Status != 'Active'
    AND UsageResource.Category = 'Token'
];
if (!tokenPurs.isEmpty()) {
    for (ProductUsageResource pur : tokenPurs) { pur.Status = 'Active'; }
    update tokenPurs;
    System.debug('Activated ' + tokenPurs.size() + ' Token PUR(s).');
} else {
    System.debug('All Token PURs are already Active.');
}

// Step 5: Activate ALL non-Token PURs using clear+activate approach.
// Now that all Token PURs are Active (Step 4) and all non-Token PURs have
// TokenResourceId set (from Step 3 or SFDMU insert), the clear+activate
// (non-null>null + Active) prevents auto-population during DML.
List<ProductUsageResource> nonTokenPurs = [
    SELECT Id, Status, TokenResourceId
    FROM ProductUsageResource
    WHERE Status != 'Active'
    AND UsageResource.Category != 'Token'
];
if (!nonTokenPurs.isEmpty()) {
    for (ProductUsageResource pur : nonTokenPurs) {
        pur.TokenResourceId = null;
        pur.Status = 'Active';
    }
    List<Database.SaveResult> results = Database.update(nonTokenPurs, false);
    Integer successCount = 0;
    for (Integer i = 0; i < results.size(); i++) {
        if (results[i].isSuccess()) {
            successCount++;
        } else {
            for (Database.Error err : results[i].getErrors()) {
                System.debug(LoggingLevel.ERROR, 'Failed to activate PUR ' +
                    nonTokenPurs[i].Id + ': ' + err.getMessage());
            }
        }
    }
    System.debug('Clear+activated ' + successCount + '/' + nonTokenPurs.size() + ' non-Token PUR(s).');
} else {
    System.debug('All non-Token PURs are already Active.');
}

// Step 6: Activate ProductUsageGrant
List<ProductUsageGrant> pugs = [SELECT Id, Status FROM ProductUsageGrant WHERE Status != 'Active'];
if (!pugs.isEmpty()) {
    for (ProductUsageGrant pug : pugs) { pug.Status = 'Active'; }
    List<Database.SaveResult> results = Database.update(pugs, false);
    Integer successCount = 0;
    for (Integer i = 0; i < results.size(); i++) {
        if (results[i].isSuccess()) {
            successCount++;
        } else {
            for (Database.Error err : results[i].getErrors()) {
                System.debug(LoggingLevel.ERROR, 'Failed to activate PUG ' +
                    pugs[i].Id + ': ' + err.getMessage());
            }
        }
    }
    System.debug('Activated ' + successCount + '/' + pugs.size() + ' ProductUsageGrant record(s).');
} else {
    System.debug('All ProductUsageGrant records are already Active.');
}
