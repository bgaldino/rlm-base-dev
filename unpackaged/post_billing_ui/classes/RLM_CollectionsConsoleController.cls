public with sharing class RLM_CollectionsConsoleController {

    @AuraEnabled(cacheable=true)
    public static List<DelinquentWrapper> getHighValueDelinquents() {
        List<Invoice> invoices = [
            SELECT Id, BillingAccountId, Balance,
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
            loadRelatedRecords(invoiceIds, latestPtpByInvoice, collectionPlanByInvoice,
                collectionPlanIdByInvoice, disputeReasonByInvoice);
        }

        // Names are read apart from the invoices: a BillingAccount.Name relationship in the invoice
        // query would fail the whole query for a user who cannot read Account.
        Set<Id> accountIds = new Set<Id>();
        for (Invoice inv : invoices) {
            if (inv.BillingAccountId != null) accountIds.add(inv.BillingAccountId);
        }
        return buildDelinquents(
            invoices, latestPtpByInvoice, collectionPlanByInvoice,
            collectionPlanIdByInvoice, disputeReasonByInvoice, RLM_AccountNames.forIds(accountIds)
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
        Map<Id, String> disputeReasonByInvoice,
        Map<Id, String> accountNames
    ) {
        List<DelinquentWrapper> results = new List<DelinquentWrapper>();
        for (Invoice inv : invoices) {
            DelinquentWrapper w = new DelinquentWrapper();
            w.Id = inv.Id;
            w.businessAccount = inv.BillingAccountId != null && accountNames.containsKey(inv.BillingAccountId) ? accountNames.get(inv.BillingAccountId) : '—';
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

    // Fills the promise-to-pay, collection plan and dispute maps for the invoices. Takes the ids
    // so a test can run the queries for invoices that do not exist (Apex cannot insert one).
    @TestVisible
    private static void loadRelatedRecords(
        Set<Id> invoiceIds,
        Map<Id, Date> latestPtpByInvoice,
        Map<Id, String> collectionPlanByInvoice,
        Map<Id, Id> collectionPlanIdByInvoice,
        Map<Id, String> disputeReasonByInvoice
    ) {
        // Each column's query is guarded on its own: a user who cannot read payment schedules (for
        // example, without a billing role's permissions) or collection plan items (without the
        // collections license), where the object reads as "not supported", still gets the
        // delinquent rows, without that column.
        try {
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
            latestPtpByInvoice.putAll(latestPromiseDates(schedules));
        } catch (QueryException e) {
            columnSkipped('promise-to-pay date', e);
        }

        try {
            List<CollectionPlanItem> planItems = [
                SELECT InvoiceId, CollectionPlanId, CollectionPlan.Name
                FROM CollectionPlanItem
                WHERE InvoiceId IN :invoiceIds
                WITH USER_MODE
            ];
            addFirstCollectionPlans(planItems, collectionPlanByInvoice, collectionPlanIdByInvoice);
        } catch (QueryException e) {
            columnSkipped('collection plan', e);
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
                disputeReasonByInvoice.putAll(disputeReasons(disputes));
            } catch (Exception e) {
                // Dispute / Dispute.InvoiceId not available (billing dispute feature
                // not provisioned in this org) — omit dispute reasons.
                System.debug(LoggingLevel.WARN, 'RLM_CollectionsConsoleController dispute reason query skipped: ' + e.getMessage());
            }
        }
    }

    // A column the user cannot read is left empty for every row; the reason goes to the debug log.
    private static void columnSkipped(String column, Exception e) {
        System.debug(LoggingLevel.WARN, 'RLM_CollectionsConsoleController ' + column + ' column skipped: ' + e.getMessage());
    }

    // Each invoice's latest promise-to-pay date: the newest dated item across its payment
    // schedules (each schedule's subquery returns its newest item). Takes rows so a test can
    // pass schedules on invoices, which Apex cannot insert.
    @TestVisible
    private static Map<Id, Date> latestPromiseDates(List<PaymentSchedule> schedules) {
        Map<Id, Date> latestPtpByInvoice = new Map<Id, Date>();
        for (PaymentSchedule ps : schedules) {
            if (!ps.PaymentScheduleItems.isEmpty()) {
                Id invoiceId = ps.ReferenceEntityId;
                Date itemDate = ps.PaymentScheduleItems[0].TargetPaymentProcessingDate;
                if (!latestPtpByInvoice.containsKey(invoiceId) || itemDate > latestPtpByInvoice.get(invoiceId)) {
                    latestPtpByInvoice.put(invoiceId, itemDate);
                }
            }
        }
        return latestPtpByInvoice;
    }

    // The first collection plan found for each invoice, by name and by id. Takes rows so a test
    // can pass plan items on invoices, which Apex cannot insert.
    @TestVisible
    private static void addFirstCollectionPlans(
        List<CollectionPlanItem> planItems,
        Map<Id, String> collectionPlanByInvoice,
        Map<Id, Id> collectionPlanIdByInvoice
    ) {
        for (CollectionPlanItem cpi : planItems) {
            if (!collectionPlanByInvoice.containsKey(cpi.InvoiceId)) {
                collectionPlanByInvoice.put(cpi.InvoiceId, cpi.CollectionPlan.Name);
                collectionPlanIdByInvoice.put(cpi.InvoiceId, cpi.CollectionPlanId);
            }
        }
    }

    // The first dispute's reason for each invoice: its type, then " - " and its subtype when it
    // has one. Takes rows so a test can pass disputes on invoices, which Apex cannot insert.
    @TestVisible
    private static Map<Id, String> disputeReasons(List<Dispute> disputes) {
        Map<Id, String> disputeReasonByInvoice = new Map<Id, String>();
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
        return disputeReasonByInvoice;
    }

    /**
     * True only when the Dispute object exists AND exposes the named field in this
     * org. Dispute and its InvoiceId/CaseId lookups are license-gated billing
     * extensions absent from a baseline build, so callers must gate dynamic SOQL
     * on this before referencing those fields.
     */
    @TestVisible
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