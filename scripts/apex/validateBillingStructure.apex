// Run after Pass 1 (insert) and before Pass 2/3 (activation).
// Fails if any BillingTreatment has null BillingPolicyId so we never activate with broken parent links.
// Once BillingTreatments are Active, BillingPolicyId cannot be fixed without deactivating first.

// Apex cannot construct the abstract built-in Exception -- `new Exception(msg)` is a
// compile error ("Type cannot be constructed: Exception"), which made this script fail
// to compile on every run. A custom subclass is required.
public class BillingStructureException extends Exception {}

List<BillingTreatment> missingPolicy = [
    SELECT Id, Name
    FROM BillingTreatment
    WHERE BillingPolicyId = null
];
if (!missingPolicy.isEmpty()) {
    List<String> names = new List<String>();
    for (BillingTreatment bt : missingPolicy) {
        names.add(bt.Name);
    }
    throw new BillingStructureException(
        'BillingTreatment records must have BillingPolicyId set before activation. '
        + 'The following records have null BillingPolicyId: ' + String.join(names, ', ')
        + '. Re-run Pass 1 (insert only) and ensure BillingPolicy.Name in the source resolves; do not run Pass 2/3 until this is fixed.'
    );
}
