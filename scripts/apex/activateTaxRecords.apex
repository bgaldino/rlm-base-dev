// One update per legal entity. On an org with Commerce B2B or B2C enabled, a TaxTreatment save
// whose rows span two or more legal entities fails with "invalid ID field" (see the qb-tax README).
Map<Id, List<TaxTreatment>> treatmentsByLegalEntity = new Map<Id, List<TaxTreatment>>();
for (TaxTreatment tt : [SELECT Id, Status, LegalEntityId FROM TaxTreatment WHERE Status != 'Active']) {
    tt.Status = 'Active';
    if (!treatmentsByLegalEntity.containsKey(tt.LegalEntityId)) {
        treatmentsByLegalEntity.put(tt.LegalEntityId, new List<TaxTreatment>());
    }
    treatmentsByLegalEntity.get(tt.LegalEntityId).add(tt);
}
for (List<TaxTreatment> treatments : treatmentsByLegalEntity.values()) {
    update treatments;
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