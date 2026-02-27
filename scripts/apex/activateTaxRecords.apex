List<TaxTreatment> taxTreatments = [SELECT Id, Status FROM TaxTreatment WHERE Status != 'Active'];
for (TaxTreatment tt : taxTreatments) {
    tt.Status = 'Active';
}
if (!taxTreatments.isEmpty()) {
    update taxTreatments;
}

Map<Id, Id> treatmentByPolicyId = new Map<Id, Id>();
for (TaxTreatment tt : [SELECT Id, TaxPolicyId FROM TaxTreatment]) {
    if (tt.TaxPolicyId != null) {
        treatmentByPolicyId.put(tt.TaxPolicyId, tt.Id);
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