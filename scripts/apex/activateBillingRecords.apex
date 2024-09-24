// Step 1: Query BillingTreatmentItem records that need to be updated
List<BillingTreatmentItem> billingTreatmentItems = [SELECT Id, Status FROM BillingTreatmentItem WHERE Status != 'Active'];

// Step 2: Update BillingTreatmentItem records to Active
for (BillingTreatmentItem bti : billingTreatmentItems) {
    bti.Status = 'Active';
}
update billingTreatmentItems;

// Step 3: Query BillingTreatment records that need to be updated
List<BillingTreatment> billingTreatments = [SELECT Id, Status FROM BillingTreatment WHERE Status != 'Active'];

// Step 4: Update BillingTreatment records to Active
for (BillingTreatment bt : billingTreatments) {
    bt.Status = 'Active';
}
update billingTreatments;

// Step 5: Query BillingPolicy records that need to be updated
List<BillingPolicy> billingPolicies = [SELECT Id, Status FROM BillingPolicy WHERE Status != 'Active'];

// Step 6: Update BillingPolicy records to Active
for (BillingPolicy bp : billingPolicies) {
    bp.Status = 'Active';
}
update billingPolicies;