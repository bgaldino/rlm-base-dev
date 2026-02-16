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
// Activation order (6 steps):
//   1. UnitOfMeasureClass → Active  (safety net; SFDMU Pass 2 handles this)
//   2. UsageResource → Active       (safety net; SFDMU Pass 2 handles this)
//   3. Pre-populate TokenResourceId on Draft non-Token PURs that are missing it
//   4. ALL non-Token PUR → clear+activate (TokenResourceId=null + Status='Active')
//   5. Token PUR → Active
//   6. ProductUsageGrant → Active
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
//     was non-null before the update. A null→null "clear" does NOT prevent
//     auto-population.
//
//   - Pre-populate + clear+activate: For PURs where TokenResourceId was not set
//     at insert time (QB-DB;UR-*, QB-QTY-CMT;UR-*), we first SET it to the
//     correct value (from UsageResource.TokenResourceId) while the PUR is Draft,
//     then use clear+activate. The non-null→null change prevents auto-population.
//
//   - CommitmentSpend + Usage PURs: QB-MTY-CMT;UR-CPUTIME and
//     QB-MTY-CMT;UR-DATASTORAGE cannot be activated in API 260. These
//     optional PURs are excluded from the data plan (258→260 migration gap).
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

// Step 3: Pre-populate TokenResourceId on Draft non-Token PURs where it's null.
// Some PURs (QB-DB;UR-*, QB-QTY-CMT;UR-*) don't get TokenResourceId auto-populated
// at SFDMU insert time. For clear+activate to work in Step 4, TokenResourceId must
// be non-null so the null assignment is a REAL change (not null→null no-op).
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

// Step 4: Activate ALL non-Token PURs using clear+activate approach.
// Now that all non-Token PURs have TokenResourceId set (from Step 3 or SFDMU insert),
// the clear+activate (non-null→null + Active) prevents auto-population during DML.
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

// Step 5: Activate Token PURs (UsageResource.Category='Token').
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
