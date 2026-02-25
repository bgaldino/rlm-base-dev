List<TaxTreatment> taxTreatments = [SELECT Id, Status FROM TaxTreatment WHERE Status != 'Active'];
for (TaxTreatment tt : taxTreatments) {
    tt.Status = 'Active';
}
if (!taxTreatments.isEmpty()) {
    update taxTreatments;
}

Map<String, Id> treatmentByPolicy = new Map<String, Id>();
for (TaxTreatment tt : [SELECT Id, TaxPolicy.Name FROM TaxTreatment]) {
    if (tt.TaxPolicy != null) {
        treatmentByPolicy.put(tt.TaxPolicy.Name, tt.Id);
    }
}

List<TaxPolicy> taxPolicies = [SELECT Id, Name, Status, DefaultTaxTreatmentId FROM TaxPolicy];
List<TaxPolicy> toUpdate = new List<TaxPolicy>();
for (TaxPolicy tp : taxPolicies) {
    Boolean changed = false;
    if (tp.DefaultTaxTreatmentId == null && treatmentByPolicy.containsKey(tp.Name)) {
        tp.DefaultTaxTreatmentId = treatmentByPolicy.get(tp.Name);
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