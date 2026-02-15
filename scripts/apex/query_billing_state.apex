// Run with: cci task run query_billing_state --org beta
// Validates billing record state after prepare_billing (source/target comparison). Check debug logs for output.

List<PaymentTerm> pts = [SELECT Id, Name, IsDefault, Status FROM PaymentTerm ORDER BY Name];
System.debug('PaymentTerm count: ' + pts.size());
for (PaymentTerm pt : pts) {
    System.debug('  ' + pt.Name + ' | IsDefault=' + pt.IsDefault + ' | Status=' + pt.Status);
}

List<BillingTreatment> bts = [SELECT Id, Name, Status FROM BillingTreatment ORDER BY Name];
System.debug('BillingTreatment count: ' + bts.size());
Map<Id, Integer> btIdToActiveCount = new Map<Id, Integer>();
for (AggregateResult ar : [SELECT BillingTreatmentId bid, COUNT(Id) cnt FROM BillingTreatmentItem WHERE Status = 'Active' AND BillingTreatmentId != null GROUP BY BillingTreatmentId]) {
    btIdToActiveCount.put((Id)ar.get('bid'), (Integer)ar.get('cnt'));
}
for (BillingTreatment bt : bts) {
    Integer activeItems = btIdToActiveCount.get(bt.Id) != null ? btIdToActiveCount.get(bt.Id) : 0;
    System.debug('  ' + bt.Name + ' | Status=' + bt.Status + ' | ActiveBTICount=' + activeItems);
}

List<BillingPolicy> bps = [SELECT Id, Name, Status, DefaultBillingTreatmentId FROM BillingPolicy ORDER BY Name];
System.debug('BillingPolicy count: ' + bps.size());
for (BillingPolicy bp : bps) {
    System.debug('  ' + bp.Name + ' | Status=' + bp.Status + ' | HasDefaultTreatment=' + (bp.DefaultBillingTreatmentId != null));
}

List<BillingTreatmentItem> btis = [SELECT Id, Name, Status, BillingTreatmentId FROM BillingTreatmentItem ORDER BY BillingTreatmentId, Name];
System.debug('BillingTreatmentItem count: ' + btis.size());
for (BillingTreatmentItem bti : btis) {
    System.debug('  ' + bti.Name + ' | Status=' + bti.Status + ' | BillingTreatmentId=' + bti.BillingTreatmentId);
}
