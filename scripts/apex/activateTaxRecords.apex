List<TaxTreatment> taxTreatments = [SELECT Id, Status FROM TaxTreatment WHERE Status != 'Active'];
for (TaxTreatment tt : taxTreatments) {
    tt.Status = 'Active';
}
if (!taxTreatments.isEmpty()) {
    update taxTreatments;
}

Map<Id, Id> treatmentByPolicyId = new Map<Id, Id>();
for (TaxTreatment tt : [
    SELECT Id, IsTaxable, TaxPolicyId
    FROM TaxTreatment
    WHERE TaxPolicyId != null
    ORDER BY IsTaxable DESC, CreatedDate ASC, Id ASC
]) {
    if (tt.TaxPolicyId != null) {
        // Keep the first row per policy from the deterministic order above.
        if (!treatmentByPolicyId.containsKey(tt.TaxPolicyId)) {
            treatmentByPolicyId.put(tt.TaxPolicyId, tt.Id);
        }
    }
}

List<TaxPolicy> taxPolicies = [SELECT Id, Name, Status, DefaultTaxTreatmentId FROM TaxPolicy];
List<TaxPolicy> toUpdate = new List<TaxPolicy>();
for (TaxPolicy tp : taxPolicies) {
    Boolean changed = false;
    if (tp.DefaultTaxTreatmentId == null && treatmentByPolicyId.containsKey(tp.Id)) {
        tp.DefaultTaxTreatmentId = treatmentByPolicyId.get(tp.Id);
        changed = true;
    }
    if (tp.Status != 'Active') {
        tp.Status = 'Active';
        changed = true;
    }
    if (changed) {
        toUpdate.add(tp);
    }
}
if (!toUpdate.isEmpty()) {
    update toUpdate;
}