// Activate billing records in dependency order: BillingTreatmentItem -> BillingTreatment -> BillingPolicy.
// When the qb-billing data plan runs correctly (object set order sets BillingPolicyId and DefaultBillingTreatmentId),
// this task can be deprecated and activation done in the plan (e.g. set 2/3/4) only.

// Step 1: Activate BillingTreatmentItem
List<BillingTreatmentItem> billingTreatmentItems = [SELECT Id, Status FROM BillingTreatmentItem WHERE Status != 'Active'];
for (BillingTreatmentItem bti : billingTreatmentItems) {
    bti.Status = 'Active';
}
update billingTreatmentItems;

// Step 2: Activate BillingTreatment (only those with at least one Active BillingTreatmentItem)
Set<Id> treatmentIdsWithActiveItem = new Set<Id>();
for (AggregateResult ar : [SELECT BillingTreatmentId FROM BillingTreatmentItem WHERE Status = 'Active' AND BillingTreatmentId != null GROUP BY BillingTreatmentId]) {
    treatmentIdsWithActiveItem.add((Id)ar.get('BillingTreatmentId'));
}
List<BillingTreatment> billingTreatments = [SELECT Id, Status FROM BillingTreatment WHERE Status != 'Active' AND Id IN :treatmentIdsWithActiveItem];
for (BillingTreatment bt : billingTreatments) {
    bt.Status = 'Active';
}
update billingTreatments;

// Step 3: Activate BillingPolicy only when DefaultBillingTreatment is Active and belongs to this policy (not orphaned)
Set<Id> activeTreatmentIds = new Set<Id>();
for (BillingTreatment bt : [SELECT Id FROM BillingTreatment WHERE Status = 'Active']) {
    activeTreatmentIds.add(bt.Id);
}
List<BillingPolicy> billingPolicies = [SELECT Id, Status, DefaultBillingTreatmentId FROM BillingPolicy WHERE Status != 'Active' AND DefaultBillingTreatmentId IN :activeTreatmentIds];
Map<Id, Id> treatmentToPolicy = new Map<Id, Id>();
for (BillingTreatment t : [SELECT Id, BillingPolicyId FROM BillingTreatment WHERE Id IN :activeTreatmentIds AND BillingPolicyId != null]) {
    treatmentToPolicy.put(t.Id, t.BillingPolicyId);
}
List<BillingPolicy> toActivate = new List<BillingPolicy>();
for (BillingPolicy bp : billingPolicies) {
    if (treatmentToPolicy.get(bp.DefaultBillingTreatmentId) == bp.Id) {
        bp.Status = 'Active';
        toActivate.add(bp);
    }
}
update toActivate;
