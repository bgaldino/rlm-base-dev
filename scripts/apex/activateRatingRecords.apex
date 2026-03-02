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
//   2.5. Remove duplicate PURs with NO PUG/PURP children (survivor priority: Active > has-children > lower Id)
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
//   purIdsWithChildren is built before the overlap scan so child-bearing status informs
//   survivor selection (Active > has-children > lower Id). Only Draft PURs with no
//   PUG/PURP children are deleted; Active records and child-bearing records are never touched.
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
// Query Draft and Active PURs ordered by (ProductId, UsageResourceId, EffectiveStartDate) so
// overlapping duplicates within each Product+UsageResource group are adjacent — enables O(n)
// linear scan rather than O(n^2) nested loop. Both statuses are included because the survivor
// selection rule (Active > has-children > lower Id) requires seeing both in the same group.
// Inactive PURs are excluded: they only exist transiently during the delete-then-reinsert
// cleanup cycle and cannot participate in the activation-blocking overlap scenario.
//
// Preflight: aggregate by (ProductId, UsageResourceId) to find only groups with more than
// one Draft/Active PUR. Composite pair keys (productId:usageResourceId) are tracked so the
// candidate scope is precise — using independent Id sets would form a cross-product and fetch
// non-candidate pairs. All three SOQL queries below (PUG, PURP, PUR) are scoped to the
// candidate pairs, bounding SOQL row count and Apex heap on large orgs.
//
// purIdsWithChildren is built BEFORE the scan so child-bearing status can be used as a
// survivor-selection criterion — ensuring the record we intend to keep is always the one
// that survives and that the deletion filter and the scan agree on the same record.
Set<String> candidatePairKeys    = new Set<String>();
Set<Id>     candidateProductIds  = new Set<Id>();
Set<Id>     candidateResourceIds = new Set<Id>();
for (AggregateResult ar : [
    SELECT ProductId, UsageResourceId, COUNT(Id) cnt
    FROM ProductUsageResource
    WHERE Status IN ('Draft', 'Active')
    GROUP BY ProductId, UsageResourceId
    HAVING COUNT(Id) > 1
]) {
    Id pid = (Id) ar.get('ProductId');
    Id rid = (Id) ar.get('UsageResourceId');
    candidatePairKeys.add(pid + ':' + rid);
    candidateProductIds.add(pid);
    candidateResourceIds.add(rid);
}
if (candidatePairKeys.isEmpty()) {
    System.debug('Step 2.5: no (Product, UsageResource) group has more than one Draft/Active PUR — nothing to deduplicate.');
} else {
    Set<Id> purIdsWithChildren = new Set<Id>();
    for (AggregateResult ar : [
        SELECT ProductUsageResourceId purId
        FROM ProductUsageGrant
        WHERE ProductUsageResource.ProductId IN :candidateProductIds
        AND ProductUsageResource.UsageResourceId IN :candidateResourceIds
        GROUP BY ProductUsageResourceId
    ]) {
        purIdsWithChildren.add((Id)ar.get('purId'));
    }
    for (AggregateResult ar : [
        SELECT ProductUsageResourceId purId
        FROM ProductUsageResourcePolicy
        WHERE ProductUsageResource.ProductId IN :candidateProductIds
        AND ProductUsageResource.UsageResourceId IN :candidateResourceIds
        GROUP BY ProductUsageResourceId
    ]) {
        purIdsWithChildren.add((Id)ar.get('purId'));
    }
    // Broad SOQL filter (ProductId IN + UsageResourceId IN) bounds the row count to the
    // candidate scope. Apex post-filter on the exact composite pair key removes any
    // cross-product non-candidate records while preserving ORDER BY sort for the scan.
    List<ProductUsageResource> allPurs = new List<ProductUsageResource>();
    for (ProductUsageResource pur : [
        SELECT Id, ProductId, UsageResourceId, EffectiveStartDate, EffectiveEndDate, Status
        FROM ProductUsageResource
        WHERE Status IN ('Draft', 'Active')
        AND ProductId IN :candidateProductIds
        AND UsageResourceId IN :candidateResourceIds
        ORDER BY ProductId, UsageResourceId, EffectiveStartDate ASC NULLS FIRST, EffectiveEndDate ASC NULLS LAST
    ]) {
        if (candidatePairKeys.contains(pur.ProductId + ':' + pur.UsageResourceId)) {
            allPurs.add(pur);
        }
    }
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
        // Priority: (1) Active wins over Draft; (2) child-bearing (PUG/PURP) wins; (3) lower Id.
        // When the survivor changes, currentEnd is reset to the NEW survivor's range only.
        // Never extend currentEnd from the discarded record's range: doing so inflates the tracked
        // window and can cause a genuinely non-overlapping subsequent PUR to be falsely flagged.
        if (currentPur.Status == 'Active' && pur.Status != 'Active') {
            duplicatePurIds.add(pur.Id);
            // survivor unchanged: currentEnd already reflects survivor's range
        } else if (pur.Status == 'Active' && currentPur.Status != 'Active') {
            duplicatePurIds.add(currentPur.Id);
            currentPur   = pur;
            currentStart = purStart;
            currentEnd   = purEnd;  // reset to new survivor's range
        } else if (purIdsWithChildren.contains(currentPur.Id) && !purIdsWithChildren.contains(pur.Id)) {
            duplicatePurIds.add(pur.Id);
            // survivor unchanged: currentEnd already reflects survivor's range
        } else if (purIdsWithChildren.contains(pur.Id) && !purIdsWithChildren.contains(currentPur.Id)) {
            duplicatePurIds.add(currentPur.Id);
            currentPur   = pur;
            currentStart = purStart;
            currentEnd   = purEnd;  // reset to new survivor's range
        } else if (currentPur.Id < pur.Id) {
            // Note: Apex Id supports relational operators (<, >, <=, >=) per the Apex Language
            // Reference. This compiles and executes correctly — no String.compareTo() needed.
            duplicatePurIds.add(pur.Id);
            // survivor unchanged: currentEnd already reflects survivor's range
        } else {
            duplicatePurIds.add(currentPur.Id);
            currentPur   = pur;
            currentStart = purStart;
            currentEnd   = purEnd;  // reset to new survivor's range
        }
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
        } else {
            // Overlapping PURs were detected but none could be auto-deleted: either the
            // overlap involves Active PURs or Draft PURs that have PUG/PURP children.
            // Activation will likely fail with an "effective period overlaps" platform error
            // until these are resolved manually (deactivate or delete the overlapping PURs).
            System.debug(
                LoggingLevel.WARN,
                'Step 2.5: detected ' + duplicatePurIds.size() + ' overlapping PUR(s) by effective period ' +
                'but none were auto-deleted (overlapping record(s) are Active, or Draft with PUG/PURP children). ' +
                'Manual review required — activation may fail with "effective period overlaps".'
            );
        }
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
