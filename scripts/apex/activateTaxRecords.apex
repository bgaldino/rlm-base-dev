// Step 1: Query TaxTreatment records that need to be updated
List<TaxTreatment> taxTreatments = [SELECT Id, Status FROM TaxTreatment WHERE Status != 'Active'];

// Step 2: Update TaxTreatment records to Active
for (TaxTreatment tt : taxTreatments) {
    tt.Status = 'Active';
}
update taxTreatments;

// Step 3: Query TaxPolicy records that need to be updated
List<TaxPolicy> taxPolicies = [SELECT Id, Status FROM TaxPolicy WHERE Status != 'Active'];

// Step 4: Update TaxPolicy records to Active
for (TaxPolicy tp : taxPolicies) {
    tp.Status = 'Active';
}
update taxPolicies;