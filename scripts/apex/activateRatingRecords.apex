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
//   1. UnitOfMeasureClass → Active  (safety net; SFDMU Pass 2 should do this)
//   2. UsageResource → Active       (safety net; SFDMU Pass 2 should do this)
//   3. Non-Token PUR without TokenResourceId → Active
//      (Currency PURs, unique-resource PURs: QB-DAT-THPT;UR-DATAXFR, QB-MTY-CMT;UR-USD)
//   4. Commitment-type PUR with clear+activate → Active
//      (CommitmentQuantity / CommitmentSpend products: QB-QTY-CMT, QB-MTY-CMT)
//   5. Token PUR → Active
//      (QB-DB;QB-TOKEN, QB-DB-TOKEN;QB-TOKEN, QB-CMT-TKN-*;QB-TOKEN, QB-TOKENS-PACK;QB-TOKEN)
//   6. Non-Token PUR with TokenResourceId → Active
//      (QB-DB;UR-*, QB-DB-TOKEN;UR-*, QB-CMT-TKN-*;UR-*)
//   7. ProductUsageGrant → Active
//
// API 260 Platform Behaviors:
//   - Auto-population: When the QB-TOKEN UsageResource is Active, the platform
//     auto-populates TokenResourceId on ALL PURs whose UsageResource (e.g.,
//     UR-CPUTIME, UR-DATASTORAGE) is shared with any product that has a Token PUR.
//     This happens at DML time (insert and update) and cannot be prevented.
//
//   - Commitment conflict: CommitmentQuantity and CommitmentSpend products cannot
//     have TokenResourceId set. But the auto-population forces it. The workaround
//     is "clear+activate": set TokenResourceId=null AND Status='Active' in a
//     SINGLE DML update. The platform accepts this because the null is applied
//     before the activation validation runs. The platform re-populates
//     TokenResourceId after the record is Active, which is accepted.
//
//   - Anchor products need Token PUR: Products with UsageModelType='Anchor'
//     (e.g., QB-DB) require a Token PUR (QB-DB;QB-TOKEN) before their non-Token
//     PURs can be activated. This is new in API 260 (not required in 258).
//
//   - CommitmentSpend + Usage PURs: QB-MTY-CMT;UR-CPUTIME and
//     QB-MTY-CMT;UR-DATASTORAGE cannot be activated in API 260 even with the
//     clear+activate workaround. These optional PURs (IsOptional=true) are
//     excluded from the data plan. This is a 258→260 migration gap.
//
//   - Currency PUR dependency: CommitmentSpend products (QB-MTY-CMT) require
//     their Currency-category PUR (QB-MTY-CMT;UR-USD) to be Active before
//     any Usage-category PURs can be activated.
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

// Step 3: Activate non-Token PUR WITHOUT TokenResourceId
// This includes Currency-category PURs (e.g., QB-MTY-CMT;UR-USD) and PURs for
// products with unique resources (e.g., QB-DAT-THPT;UR-DATAXFR). These must be
// active before commitment Usage PURs that depend on a Currency PUR being active.
List<ProductUsageResource> noTokenResPurs = [
    SELECT Id, Status
    FROM ProductUsageResource
    WHERE Status != 'Active'
    AND TokenResourceId = null
    AND UsageResource.Category != 'Token'
];
if (!noTokenResPurs.isEmpty()) {
    for (ProductUsageResource pur : noTokenResPurs) { pur.Status = 'Active'; }
    update noTokenResPurs;
    System.debug('Activated ' + noTokenResPurs.size() + ' non-Token PUR (no TokenResourceId).');
} else {
    System.debug('All non-Token PUR (no TokenResourceId) records are already Active.');
}

// Step 4: Activate commitment-type product PURs using clear+activate approach.
// API 260 auto-populates TokenResourceId on Draft PURs when Token UsageResource is Active.
// Commitment products (CommitmentQuantity/CommitmentSpend) can't have TokenResourceId,
// but clearing it AND setting Status='Active' in a single DML bypasses the validation.
List<ProductUsageResource> commitPurs = [
    SELECT Id, Status, TokenResourceId
    FROM ProductUsageResource
    WHERE Status != 'Active'
    AND TokenResourceId != null
    AND UsageResource.Category != 'Token'
    AND Product.UsageModelType IN ('CommitmentQuantity', 'CommitmentSpend')
];
if (!commitPurs.isEmpty()) {
    for (ProductUsageResource pur : commitPurs) {
        pur.TokenResourceId = null;
        pur.Status = 'Active';
    }
    update commitPurs;
    System.debug('Clear+activated ' + commitPurs.size() + ' commitment-type PUR(s).');
} else {
    System.debug('No commitment-type PURs need clear+activate.');
}

// Step 5: Activate Token PURs (UsageResource.Category='Token')
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

// Step 6: Activate remaining PUR with TokenResourceId
// These are non-Token PURs for Anchor/Commit/Pack products whose Token PUR is now Active.
List<ProductUsageResource> withTokenResPurs = [
    SELECT Id, Status
    FROM ProductUsageResource
    WHERE Status != 'Active'
    AND TokenResourceId != null
];
if (!withTokenResPurs.isEmpty()) {
    for (ProductUsageResource pur : withTokenResPurs) { pur.Status = 'Active'; }
    update withTokenResPurs;
    System.debug('Activated ' + withTokenResPurs.size() + ' PUR (with TokenResourceId).');
} else {
    System.debug('All PUR (with TokenResourceId) records are already Active.');
}

// Step 7: Activate ProductUsageGrant
List<ProductUsageGrant> pugs = [SELECT Id, Status FROM ProductUsageGrant WHERE Status != 'Active'];
if (!pugs.isEmpty()) {
    for (ProductUsageGrant pug : pugs) { pug.Status = 'Active'; }
    update pugs;
    System.debug('Activated ' + pugs.size() + ' ProductUsageGrant record(s).');
} else {
    System.debug('All ProductUsageGrant records are already Active.');
}
