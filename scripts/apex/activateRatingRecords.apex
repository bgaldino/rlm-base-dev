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
//   2.5. Remove duplicate PURs     (same Product+UsageResource+overlapping effective period; keeps one, deletes Draft dupes + their PUG/PURP children)
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
//   All queries filter on Status != 'Active', so re-running this script on an
//   already-activated org is a safe no-op.
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

// Step 2.5: Remove duplicate PURs (same Product + UsageResource + overlapping effective period).
// Re-running the rating data plan or partial runs can leave duplicate Draft PURs; the platform
// blocks activation with "effective period overlaps with an existing record". Keep one per
// (ProductId, UsageResourceId) overlapping set, delete Draft duplicates. Child records
// (ProductUsageResourcePolicy, ProductUsageGrant) must be deleted first.
// We must query all PURs (Active + non-Active) so we can detect overlaps between new Draft
// and existing Active; if we only queried non-Active we would never mark those Drafts as duplicates.
List<ProductUsageResource> allPurs = [
    SELECT Id, ProductId, UsageResourceId, EffectiveStartDate, EffectiveEndDate, Status
    FROM ProductUsageResource
];
Set<Id> duplicatePurIds = new Set<Id>();
// Pairwise overlap check within allPurs. O(n^2) is acceptable for typical QB PUR counts (dozens to low hundreds).
for (Integer i = 0; i < allPurs.size(); i++) {
    ProductUsageResource a = allPurs[i];
    if (duplicatePurIds.contains(a.Id)) continue;
    for (Integer j = i + 1; j < allPurs.size(); j++) {
        ProductUsageResource b = allPurs[j];
        if (duplicatePurIds.contains(b.Id)) continue;
        if (a.ProductId != b.ProductId || a.UsageResourceId != b.UsageResourceId) continue;
        Date aStart = a.EffectiveStartDate != null ? ((Datetime)a.EffectiveStartDate).date() : Date.newInstance(1900, 1, 1);
        Date aEnd   = a.EffectiveEndDate   != null ? ((Datetime)a.EffectiveEndDate).date()   : Date.newInstance(4000, 12, 31);
        Date bStart = b.EffectiveStartDate != null ? ((Datetime)b.EffectiveStartDate).date() : Date.newInstance(1900, 1, 1);
        Date bEnd   = b.EffectiveEndDate   != null ? ((Datetime)b.EffectiveEndDate).date()   : Date.newInstance(4000, 12, 31);
        Boolean overlaps = (aStart <= bEnd) && (aEnd >= bStart);
        if (!overlaps) continue;
        if (a.Status == 'Active' && b.Status != 'Active') {
            duplicatePurIds.add(b.Id);
        } else if (b.Status == 'Active' && a.Status != 'Active') {
            duplicatePurIds.add(a.Id);
        } else if (a.Id < b.Id) {
            duplicatePurIds.add(b.Id);
        } else {
            duplicatePurIds.add(a.Id);
        }
    }
}
if (!duplicatePurIds.isEmpty()) {
    List<ProductUsageResource> purToDelete = new List<ProductUsageResource>();
    for (ProductUsageResource pur : allPurs) {
        if (duplicatePurIds.contains(pur.Id) && pur.Status == 'Draft') {
            purToDelete.add(pur);
        }
    }
    if (!purToDelete.isEmpty()) {
        Set<Id> purIdsToDelete = new Set<Id>();
        for (ProductUsageResource pur : purToDelete) purIdsToDelete.add(pur.Id);
        List<ProductUsageGrant> pugDelete = [SELECT Id FROM ProductUsageGrant WHERE ProductUsageResourceId IN :purIdsToDelete];
        List<ProductUsageResourcePolicy> purpDelete = [SELECT Id FROM ProductUsageResourcePolicy WHERE ProductUsageResourceId IN :purIdsToDelete];
        if (!pugDelete.isEmpty()) { delete pugDelete; System.debug('Deleted ' + pugDelete.size() + ' ProductUsageGrant(s) for duplicate PUR(s).'); }
        if (!purpDelete.isEmpty()) { delete purpDelete; System.debug('Deleted ' + purpDelete.size() + ' ProductUsageResourcePolicy(s) for duplicate PUR(s).'); }
        delete purToDelete;
        System.debug('Deleted ' + purToDelete.size() + ' duplicate Draft PUR(s) (overlapping effective period).');
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
