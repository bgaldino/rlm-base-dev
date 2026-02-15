// Deletes draft billing-related records only. Use before re-running the billing data plan.
// Run with: cci task run delete_draft_billing_records --org <alias>
//
// CONSTRAINT: Once BillingTreatmentItem or BillingTreatment is moved out of Draft (e.g. Active),
// they cannot be deleted ever. So we only delete records that are still Draft.
// We never delete draft BillingPolicy that are still referenced by any BillingTreatment
// (Active or Draft), so Active BT are never orphaned and re-runs can match by composite.

// 1. Clear default treatment on draft policies
List<BillingPolicy> draftPolicies = [SELECT Id, DefaultBillingTreatmentId FROM BillingPolicy WHERE Status = 'Draft'];
for (BillingPolicy bp : draftPolicies) {
    bp.DefaultBillingTreatmentId = null;
}
update draftPolicies;

Set<Id> draftPolicyIds = new Set<Id>();
for (BillingPolicy bp : draftPolicies) {
    draftPolicyIds.add(bp.Id);
}

// 2. Delete only DRAFT BillingTreatmentItem under BillingTreatments that reference a draft BillingPolicy
//    (Active BTI cannot be deleted ever.)
List<BillingTreatmentItem> draftItemsUnderDraftPolicy = [SELECT Id FROM BillingTreatmentItem WHERE Status = 'Draft' AND BillingTreatment.BillingPolicyId IN :draftPolicyIds];
delete draftItemsUnderDraftPolicy;

// 3. Delete only DRAFT BillingTreatment that reference a draft BillingPolicy
//    (Active BT cannot be deleted ever.)
List<BillingTreatment> draftTreatmentsUnderDraftPolicy = [SELECT Id FROM BillingTreatment WHERE Status = 'Draft' AND BillingPolicyId IN :draftPolicyIds];
delete draftTreatmentsUnderDraftPolicy;

// 4. Delete any remaining draft BillingTreatmentItem and draft BillingTreatment (e.g. orphans)
List<BillingTreatmentItem> draftItems = [SELECT Id FROM BillingTreatmentItem WHERE Status = 'Draft'];
delete draftItems;
List<BillingTreatment> draftTreatments = [SELECT Id FROM BillingTreatment WHERE Status = 'Draft'];
delete draftTreatments;

// 5. Delete only draft BillingPolicy that have NO BillingTreatments left (Active or Draft).
//    Never delete a draft BP that is still referenced by any BT, or Active BT become orphaned
//    and the next run inserts duplicate BillingTreatments.
Set<Id> policyIdsWithTreatments = new Set<Id>();
for (BillingTreatment bt : [SELECT BillingPolicyId FROM BillingTreatment WHERE BillingPolicyId IN :draftPolicyIds]) {
    policyIdsWithTreatments.add(bt.BillingPolicyId);
}
List<BillingPolicy> draftPoliciesToDelete = new List<BillingPolicy>();
for (BillingPolicy bp : draftPolicies) {
    if (!policyIdsWithTreatments.contains(bp.Id)) {
        draftPoliciesToDelete.add(bp);
    }
}
delete draftPoliciesToDelete;

// 6. Delete PaymentTermItem for draft PaymentTerms (PaymentTermItem has no Status; delete by parent)
List<Id> draftTermIds = new List<Id>();
for (PaymentTerm pt : [SELECT Id FROM PaymentTerm WHERE Status = 'Draft']) {
    draftTermIds.add(pt.Id);
}
List<PaymentTermItem> termItemsToDelete = [SELECT Id FROM PaymentTermItem WHERE PaymentTermId IN :draftTermIds];
delete termItemsToDelete;

// 7. Delete draft PaymentTerm
List<PaymentTerm> draftTerms = [SELECT Id FROM PaymentTerm WHERE Status = 'Draft'];
delete draftTerms;

System.debug('Deleted draft billing records: BillingTreatmentItem=' + (draftItemsUnderDraftPolicy.size() + draftItems.size()) + ', BillingTreatment=' + (draftTreatmentsUnderDraftPolicy.size() + draftTreatments.size()) + ', BillingPolicy=' + draftPoliciesToDelete.size() + ', PaymentTermItem=' + termItemsToDelete.size() + ', PaymentTerm=' + draftTerms.size());
