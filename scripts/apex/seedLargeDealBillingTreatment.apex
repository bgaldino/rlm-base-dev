// Seeds the large-deal "Exclude from Billing" billing configuration used by the
// large_stx Prepare-for-Activation flow. Large deals (IsLargeDeal=true) cannot
// be billed (billing schedule creation is rejected) and the platform's
// LegalEntity treatment-selection resolver is not bulk-safe at large-deal scale.
// This seed provides a Default-selection policy + a treatment marked
// ExcludeFromBilling=Yes that the controller pre-stamps onto large-deal order
// items, turning billing-treatment resolution into a no-op.
//
// NOTE: A nonbillable treatment (ExcludeFromBilling=Yes) CANNOT have billing
// treatment items (platform validation), so unlike normal treatments it has no
// BillingTreatmentItem and activates directly. Activation order: treatment ->
// BillingPolicy (with DefaultBillingTreatmentId).
// Idempotent: re-runs are no-ops once the treatment exists and is Active.

final String POLICY_NAME = 'RLM Large Deal Policy';
final String TREATMENT_NAME = 'RLM Large Deal - Exclude from Billing';

// Idempotent + self-healing: the body below re-checks existence and status for
// BOTH the policy and the treatment, so a re-run repairs a partial prior run
// (e.g. treatment Active but the policy not yet Active / not linked) instead of
// early-returning on the treatment's status alone.

// 1) Policy (Draft, Default selection — no legal-entity lookup). Resolved FIRST so
//    the treatment lookup below can be scoped to THIS policy.
List<BillingPolicy> pols = [SELECT Id, Status, DefaultBillingTreatmentId FROM BillingPolicy WHERE Name = :POLICY_NAME LIMIT 1];
BillingPolicy pol = pols.isEmpty() ? null : pols[0];
if (pol == null) {
    pol = new BillingPolicy(
        Name = POLICY_NAME,
        Status = 'Draft',
        BillingTreatmentSelection = 'Default'
    );
    insert pol;
}

// 2) Treatment (Draft, ExcludeFromBilling=Yes, NO legal entity, NO items).
//    Name is NOT a unique key, so scope the lookup to this policy + ExcludeFromBilling.
//    Reusing an unrelated same-named treatment (a billable one, or one under a
//    different policy) would make the DefaultBillingTreatmentId update below fail
//    validation ("default treatment must belong to the policy") or activate the wrong
//    config. A same-named treatment outside this policy is left untouched; we create
//    our own under POLICY_NAME.
List<BillingTreatment> existing = [
    SELECT Id, Status FROM BillingTreatment
    WHERE Name = :TREATMENT_NAME AND ExcludeFromBilling = 'Yes' AND BillingPolicyId = :pol.Id
    LIMIT 1
];
BillingTreatment trt = existing.isEmpty() ? null : existing[0];
if (trt == null) {
    trt = new BillingTreatment(
        Name = TREATMENT_NAME,
        Status = 'Draft',
        BillingPolicyId = pol.Id,
        ExcludeFromBilling = 'Yes',
        IsMilestoneBilling = false
    );
    insert trt;
}

// A nonbillable treatment can't have items — remove any left by a prior partial run.
List<BillingTreatmentItem> strayItems = [SELECT Id FROM BillingTreatmentItem WHERE BillingTreatmentId = :trt.Id];
if (!strayItems.isEmpty()) {
    delete strayItems;
}

// 3) Activate in dependency order: treatment -> policy
if (trt.Status != 'Active') {
    trt.Status = 'Active';
    update trt;
}
if (pol.Status != 'Active' || pol.DefaultBillingTreatmentId != trt.Id) {
    pol.DefaultBillingTreatmentId = trt.Id;
    pol.Status = 'Active';
    update pol;
}

System.debug('SEED done policyId=' + pol.Id + ' treatmentId=' + trt.Id);
