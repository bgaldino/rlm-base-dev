public with sharing class RLM_CollectionsConsoleController {

    @AuraEnabled(cacheable=true)
    public static List<DelinquentWrapper> getHighValueDelinquents() {
        List<DelinquentWrapper> results = new List<DelinquentWrapper>();

        List<Invoice> invoices = [
            SELECT Id, BillingAccountId, BillingAccount.Name, Balance,
                   DaysInvoiceOverdue, DocumentNumber
            FROM Invoice
            WHERE Balance > 2000 AND DaysInvoiceOverdue > 30
            ORDER BY Balance DESC
            LIMIT 50
        ];

        Set<Id> invoiceIds = new Set<Id>();
        for (Invoice inv : invoices) {
            invoiceIds.add(inv.Id);
        }

        Map<Id, Date> latestPtpByInvoice = new Map<Id, Date>();
        Map<Id, String> collectionPlanByInvoice = new Map<Id, String>();
        Map<Id, Id> collectionPlanIdByInvoice = new Map<Id, Id>();
        Map<Id, String> disputeReasonByInvoice = new Map<Id, String>();

        if (!invoiceIds.isEmpty()) {
            List<PaymentSchedule> schedules = [
                SELECT Id, ReferenceEntityId,
                    (SELECT Id, TargetPaymentProcessingDate
                     FROM PaymentScheduleItems
                     WHERE TargetPaymentProcessingDate != NULL
                     ORDER BY TargetPaymentProcessingDate DESC
                     LIMIT 1)
                FROM PaymentSchedule
                WHERE ReferenceEntityId IN :invoiceIds
            ];
            for (PaymentSchedule ps : schedules) {
                if (!ps.PaymentScheduleItems.isEmpty()) {
                    Id invoiceId = ps.ReferenceEntityId;
                    Date itemDate = ps.PaymentScheduleItems[0].TargetPaymentProcessingDate;
                    if (!latestPtpByInvoice.containsKey(invoiceId) || itemDate > latestPtpByInvoice.get(invoiceId)) {
                        latestPtpByInvoice.put(invoiceId, itemDate);
                    }
                }
            }

            List<CollectionPlanItem> planItems = [
                SELECT InvoiceId, CollectionPlanId, CollectionPlan.Name
                FROM CollectionPlanItem
                WHERE InvoiceId IN :invoiceIds
            ];
            for (CollectionPlanItem cpi : planItems) {
                if (!collectionPlanByInvoice.containsKey(cpi.InvoiceId)) {
                    collectionPlanByInvoice.put(cpi.InvoiceId, cpi.CollectionPlan.Name);
                    collectionPlanIdByInvoice.put(cpi.InvoiceId, cpi.CollectionPlanId);
                }
            }

            // Query disputes linked to these invoices for the dispute-reason display.
            // Dispute.InvoiceId is a billing-extension field the Apex compiler in some
            // org configs does not surface for *static* SOQL (the same constraint that
            // drove the dynamic-query pattern in RLM_BillingCaseMetricsController). Use
            // dynamic SOQL + dynamic field access so the class compiles regardless, and
            // resolve InvoiceId at runtime. (The org's custom Dispute.Invoice__c field is
            // not part of this repo; the standard InvoiceId lookup is used instead.)
            List<Dispute> disputes = Database.query(
                'SELECT InvoiceId, DisputeType, DisputeSubtype, Description ' +
                'FROM Dispute WHERE InvoiceId IN :invoiceIds',
                AccessLevel.USER_MODE
            );
            for (Dispute d : disputes) {
                Id dispInvoiceId = (Id) d.get('InvoiceId');
                if (!disputeReasonByInvoice.containsKey(dispInvoiceId)) {
                    String reason = d.DisputeType;
                    if (String.isNotBlank(d.DisputeSubtype)) {
                        reason += ' - ' + d.DisputeSubtype;
                    }
                    disputeReasonByInvoice.put(dispInvoiceId, reason);
                }
            }
        }

        for (Invoice inv : invoices) {
            DelinquentWrapper w = new DelinquentWrapper();
            w.Id = inv.Id;
            w.businessAccount = inv.BillingAccount != null ? inv.BillingAccount.Name : '';
            w.accountId = inv.BillingAccountId;
            w.balance = inv.Balance;
            w.overdueDays = inv.DaysInvoiceOverdue;
            w.invoiceBalance = inv.Balance;
            w.documentNumber = inv.DocumentNumber;
            w.disputeReason = disputeReasonByInvoice.containsKey(inv.Id) ? disputeReasonByInvoice.get(inv.Id) : '-';
            w.collectionPlanId = collectionPlanByInvoice.containsKey(inv.Id) ? collectionPlanByInvoice.get(inv.Id) : '';
            w.collectionPlanRecordId = collectionPlanIdByInvoice.get(inv.Id);
            w.ptpDate = latestPtpByInvoice.get(inv.Id);
            results.add(w);
        }

        return results;
    }

    public class DelinquentWrapper {
        @AuraEnabled public Id Id;
        @AuraEnabled public String businessAccount;
        @AuraEnabled public Id accountId;
        @AuraEnabled public Decimal balance;
        @AuraEnabled public Integer overdueDays;
        @AuraEnabled public Date ptpDate;
        @AuraEnabled public Decimal invoiceBalance;
        @AuraEnabled public String documentNumber;
        @AuraEnabled public String disputeReason;
        @AuraEnabled public String collectionPlanId;
        @AuraEnabled public Id collectionPlanRecordId;
    }
}