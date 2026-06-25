public with sharing class RLM_CollectionsConsoleController {

    @AuraEnabled(cacheable=true)
    public static List<DelinquentWrapper> getHighValueDelinquents() {
        List<Invoice> invoices = [
            SELECT Id, BillingAccountId, BillingAccount.Name, Balance,
                   DaysInvoiceOverdue, DocumentNumber
            FROM Invoice
            WHERE Balance > 2000 AND DaysInvoiceOverdue > 30
            WITH USER_MODE
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
                WITH USER_MODE
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
                WITH USER_MODE
            ];
            for (CollectionPlanItem cpi : planItems) {
                if (!collectionPlanByInvoice.containsKey(cpi.InvoiceId)) {
                    collectionPlanByInvoice.put(cpi.InvoiceId, cpi.CollectionPlan.Name);
                    collectionPlanIdByInvoice.put(cpi.InvoiceId, cpi.CollectionPlanId);
                }
            }

            // Query disputes linked to these invoices for the dispute-reason display.
            // Dispute and its InvoiceId lookup are license-gated billing extensions:
            // present at runtime only when the billing dispute feature is provisioned,
            // and not surfaced to the Apex compiler for static SOQL. In a baseline build
            // the field (and sometimes the object) is absent entirely, so guard with a
            // Schema describe and run dynamic SOQL (USER_MODE) inside try/catch — the
            // panel omits dispute reasons where the feature isn't enabled rather than
            // throwing. (The org's custom Dispute.Invoice__c field is not part of this
            // repo; the standard InvoiceId lookup is used instead.)
            if (disputeFieldAvailable('InvoiceId')) {
                try {
                    List<Dispute> disputes = Database.query(
                        'SELECT InvoiceId, DisputeType, DisputeSubtype, Description ' +
                        'FROM Dispute WHERE InvoiceId IN :invoiceIds',
                        AccessLevel.USER_MODE
                    );
                    for (Dispute d : disputes) {
                        Id dispInvoiceId = (Id) d.get('InvoiceId');
                        if (!disputeReasonByInvoice.containsKey(dispInvoiceId)) {
                            String reason = (String) d.get('DisputeType');
                            String subtype = (String) d.get('DisputeSubtype');
                            if (String.isNotBlank(subtype)) {
                                reason += ' - ' + subtype;
                            }
                            disputeReasonByInvoice.put(dispInvoiceId, reason);
                        }
                    }
                } catch (Exception e) {
                    // Dispute / Dispute.InvoiceId not available (billing dispute feature
                    // not provisioned in this org) — omit dispute reasons.
                    System.debug(LoggingLevel.WARN, 'RLM_CollectionsConsoleController dispute reason query skipped: ' + e.getMessage());
                }
            }
        }

        return buildDelinquents(
            invoices, latestPtpByInvoice, collectionPlanByInvoice,
            collectionPlanIdByInvoice, disputeReasonByInvoice
        );
    }

    /**
     * Assemble delinquent worklist wrappers from the queried invoices and the related-record
     * maps. Extracted so the projection logic can be unit-tested with synthetic in-memory
     * records (the underlying Invoice object is system-managed and not insertable in tests).
     */
    @TestVisible
    private static List<DelinquentWrapper> buildDelinquents(
        List<Invoice> invoices,
        Map<Id, Date> latestPtpByInvoice,
        Map<Id, String> collectionPlanByInvoice,
        Map<Id, Id> collectionPlanIdByInvoice,
        Map<Id, String> disputeReasonByInvoice
    ) {
        List<DelinquentWrapper> results = new List<DelinquentWrapper>();
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

    /**
     * True only when the Dispute object exists AND exposes the named field in this
     * org. Dispute and its InvoiceId/CaseId lookups are license-gated billing
     * extensions absent from a baseline build, so callers must gate dynamic SOQL
     * on this before referencing those fields.
     */
    private static Boolean disputeFieldAvailable(String fieldName) {
        if (!Schema.getGlobalDescribe().containsKey('Dispute')) {
            return false;
        }
        return Schema.getGlobalDescribe()
            .get('Dispute')
            .getDescribe()
            .fields.getMap()
            .containsKey(fieldName);
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