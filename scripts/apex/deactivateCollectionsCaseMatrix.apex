/**
 * Disable the DetermineCaseReasonAndRelatedAttributes decision-matrix version
 * BEFORE (re)deploying the DecisionMatrixDefinition in deploy_post_collections.
 *
 * Why: a metadata deploy can't migrate a matrix version while an active (enabled)
 * version with that name already exists -- so a second run of prepare_collections
 * fails with "We can't migrate version DetermineCaseReasonAndRelatedAttributes_V1
 * because an active version with that name already exists." Disabling the version
 * first makes the redeploy idempotent; seed_collections_case_matrix re-enables it
 * afterward. Mirrors the deactivate_expression_sets-before-deploy pattern.
 *
 * Idempotent and safe on a first run: if the matrix doesn't exist yet (it's
 * deployed by deploy_post_collections, which runs after this), this is a no-op.
 */
List<CalculationMatrix> matrices = [
    SELECT Id FROM CalculationMatrix WHERE UniqueName = 'DetermineCaseReasonAndRelatedAttributes' LIMIT 1
];
if (matrices.isEmpty()) {
    System.debug('DEACTIVATE_CASE_MATRIX: matrix not present yet (first run) — nothing to disable.');
} else {
    List<CalculationMatrixVersion> enabledVersions = [
        SELECT Id, IsEnabled FROM CalculationMatrixVersion
        WHERE CalculationMatrixId = :matrices[0].Id AND IsEnabled = true
    ];
    for (CalculationMatrixVersion v : enabledVersions) {
        v.IsEnabled = false;
    }
    if (!enabledVersions.isEmpty()) {
        update enabledVersions;
    }
    System.debug('DEACTIVATE_CASE_MATRIX: disabled ' + enabledVersions.size() + ' active version(s).');
}
