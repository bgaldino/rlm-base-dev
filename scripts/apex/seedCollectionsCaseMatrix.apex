/**
 * Seed the Collections "Create Case for Collection" Business Rules Engine setup.
 *
 * Idempotent. Safe to re-run. Wired into the prepare_collections flow (gated on
 * the `collections` feature flag).
 *
 * What it does:
 *   1. Seeds the five sample CollectionPlanReason records (CPR01-CPR05) from the
 *      Salesforce Help doc "Create and Activate a Decision Matrix to Create a Case
 *      for a Collection Plan" (ind.collections_create_decision_matrix_create_case).
 *   2. Populates and activates the DetermineCaseReasonAndRelatedAttributes decision
 *      matrix (schema deployed as DecisionMatrixDefinition metadata) with the five
 *      Code -> Reason/Priority/Type rows from the same doc.
 *   3. Self-checks the matrix at runtime and aborts loudly if it doesn't resolve.
 *
 * Decision Matrix Row note: CalculationMatrixRow.Name is a platform-computed,
 * content-derived hash used for runtime matching. It is NOT auto-computed on plain
 * DML insert, but it IS portable across orgs (verified: identical content yields the
 * identical hash regardless of org/matrix/column IDs). The hashes below were captured
 * from a Designer CSV import of the doc's sample rows; re-using them lets us rebuild
 * the matrix headlessly. If you change the row CONTENT (Code/Reason/Priority/Type),
 * you must re-import via the Decision Matrix Designer (Upload CSV File) and re-capture
 * the new Name hashes -- see datasets/collections/decision_matrix_case_rows.csv.
 */

// ── 1. Sample CollectionPlanReason records ──────────────────────────────────
Map<String, String> reasonNames = new Map<String, String>{
    'CPR01' => 'Missed payments',
    'CPR02' => 'Bounced checks',
    'CPR03' => 'High-risk borrower',
    'CPR04' => 'Deceased account',
    'CPR05' => 'Bankruptcy'
};
Map<String, String> reasonDescs = new Map<String, String>{
    'CPR01' => 'The borrower has missed one or more payment deadlines, and the outstanding amount is more than 60 days past the due date.',
    'CPR02' => 'Payments made by the borrower have been returned due to insufficient funds or other issues.',
    'CPR03' => 'The borrower has a history of making late or partial payments due to seasonal income or low credit scores.',
    'CPR04' => 'Delinquent or missed payments due to the unexpected death of the borrower.',
    'CPR05' => 'The borrower has experienced a significant change in their financial situation affecting their ability to repay.'
};
Set<String> existingReasonCodes = new Set<String>();
for (CollectionPlanReason r : [SELECT Code FROM CollectionPlanReason WHERE Code IN :reasonNames.keySet()]) {
    existingReasonCodes.add(r.Code);
}
List<CollectionPlanReason> reasonsToInsert = new List<CollectionPlanReason>();
for (String code : reasonNames.keySet()) {
    if (existingReasonCodes.contains(code)) {
        continue;
    }
    reasonsToInsert.add(new CollectionPlanReason(
        Name = reasonNames.get(code),
        Code = code,
        Description = reasonDescs.get(code),
        IsActive = true
    ));
}
if (!reasonsToInsert.isEmpty()) {
    insert reasonsToInsert;
}
System.debug('SEED_CPR inserted=' + reasonsToInsert.size() + ' existing=' + existingReasonCodes.size());

// ── 2. Decision matrix rows ─────────────────────────────────────────────────
// Name(hash) -> { Code, Reason, Priority } ; Type is always 'Collections'.
Map<String, List<String>> rowData = new Map<String, List<String>>{
    'ceb7594b2ef20a20fa5ca30a856edf05' => new List<String>{ 'CPR01', 'Missed Payments',    'Medium' },
    '5e2a0b3c2d78800fb13ff604e3cb8ee1' => new List<String>{ 'CPR02', 'Bounced Checks',     'High'   },
    '6b750dec273296145dd1247ccb8c636e' => new List<String>{ 'CPR03', 'High-Risk Borrower', 'Medium' },
    '5c13c3108e81827ab7e16c3cded9cbe1' => new List<String>{ 'CPR04', 'Deceased Account',   'High'   },
    'be75e7f8101c1e58d1c928b2e718db7b' => new List<String>{ 'CPR05', 'Bankruptcy',         'High'   }
};

List<CalculationMatrix> matrices = [
    SELECT Id FROM CalculationMatrix WHERE UniqueName = 'DetermineCaseReasonAndRelatedAttributes' LIMIT 1
];
if (matrices.isEmpty()) {
    throw new System.AsyncException('DetermineCaseReasonAndRelatedAttributes matrix not found. Deploy the DecisionMatrixDefinition (deploy_post_collections) before running this seed.');
}
CalculationMatrixVersion version = [
    SELECT Id, IsEnabled, Rank FROM CalculationMatrixVersion
    WHERE CalculationMatrixId = :matrices[0].Id AND VersionNumber = 1 LIMIT 1
];

Set<String> existingRowNames = new Set<String>();
for (CalculationMatrixRow row : [SELECT Name FROM CalculationMatrixRow WHERE CalculationMatrixVersionId = :version.Id]) {
    existingRowNames.add(row.Name);
}
List<CalculationMatrixRow> rowsToInsert = new List<CalculationMatrixRow>();
for (String hashName : rowData.keySet()) {
    if (existingRowNames.contains(hashName)) {
        continue;
    }
    List<String> d = rowData.get(hashName);
    rowsToInsert.add(new CalculationMatrixRow(
        Name = hashName,
        CalculationMatrixVersionId = version.Id,
        InputData = JSON.serialize(new Map<String, Object>{ 'Code' => d[0] }),
        OutputData = JSON.serialize(new Map<String, Object>{ 'Reason' => d[1], 'Priority' => d[2], 'Type' => 'Collections' })
    ));
}
if (!rowsToInsert.isEmpty()) {
    // Rows can't be modified while the version is enabled.
    if (version.IsEnabled) {
        version.IsEnabled = false;
        update version;
    }
    insert rowsToInsert;
}
System.debug('SEED_MATRIX_ROWS inserted=' + rowsToInsert.size() + ' existing=' + existingRowNames.size());

// Activate the version (highest-rank enabled version is used at runtime).
if (!version.IsEnabled || version.Rank != 1) {
    version.IsEnabled = true;
    version.Rank = 1;
    update version;
}

// ── 3. Runtime self-check ───────────────────────────────────────────────────
Invocable.Action action = Invocable.Action.createCustomAction('runDecisionMatrix', 'DetermineCaseReasonAndRelatedAttributes');
action.setInvocationParameter('Code', 'CPR01');
List<Invocable.Action.Result> results = action.invoke();
String reason = (String) results[0].getOutputParameters().get('Reason');
if (!results[0].isSuccess() || reason != 'Missed Payments') {
    throw new System.AsyncException('Collections case matrix self-check FAILED: expected Reason=Missed Payments for Code=CPR01, got success=' + results[0].isSuccess() + ' reason=' + reason + '. If this org computed different row hashes, re-import datasets/collections/decision_matrix_case_rows.csv via the Decision Matrix Designer and re-capture the Name hashes in this script.');
}
System.debug('SEED_MATRIX_SELFCHECK OK: CPR01 -> ' + JSON.serialize(results[0].getOutputParameters()));
