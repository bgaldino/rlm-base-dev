/**
 * activateCustomerDemoBilling.apex
 *
 * Activates the customer demo BillingPolicy stack in dependency order:
 *   1. BillingTreatmentItem → Active
 *   2. BillingTreatment     → Active
 *   3. BillingPolicy        → Active (sets DefaultBillingTreatmentId if null)
 *
 * The billing plan loads all three objects as Draft (platform rejects Status=Active
 * on create). This script runs after insert_customer_demo_billing_data to make the
 * policy usable on orders.
 *
 * Scoped to policies whose name contains 'Billing' and whose treatment name contains
 * 'Billing Treatment' — safe to run on any customer-template billing stack.
 *
 * Idempotent: already-Active records are skipped without error.
 */

List<BillingPolicy> policies = [
    SELECT Id, Name, Status, DefaultBillingTreatmentId
    FROM BillingPolicy
    WHERE Status = 'Draft'
    AND Name NOT LIKE 'QB%'
    AND Name NOT LIKE 'SF-%'
];

if (policies.isEmpty()) {
    System.debug('activateCustomerDemoBilling: no Draft customer BillingPolicy records found — nothing to do.');
    return;
}

for (BillingPolicy bp : policies) {
    // Step 1: activate treatment items
    List<BillingTreatment> treatments = [
        SELECT Id, Name, Status FROM BillingTreatment WHERE BillingPolicyId = :bp.Id
    ];
    List<Id> treatmentIds = new List<Id>();
    for (BillingTreatment bt : treatments) treatmentIds.add(bt.Id);

    List<BillingTreatmentItem> items = [
        SELECT Id, Status FROM BillingTreatmentItem WHERE BillingTreatmentId IN :treatmentIds AND Status != 'Active'
    ];
    for (BillingTreatmentItem bti : items) bti.Status = 'Active';
    if (!items.isEmpty()) update items;

    // Step 2: activate treatments
    for (BillingTreatment bt : treatments) {
        if (bt.Status != 'Active') bt.Status = 'Active';
    }
    update treatments;

    // Step 3: set default treatment + activate policy
    if (bp.DefaultBillingTreatmentId == null && !treatments.isEmpty()) {
        bp.DefaultBillingTreatmentId = treatments[0].Id;
    }
    bp.Status = 'Active';
    update bp;

    System.debug('activateCustomerDemoBilling: activated ' + bp.Name +
        ' (' + treatments.size() + ' treatment(s), ' + items.size() + ' item(s))');
}
