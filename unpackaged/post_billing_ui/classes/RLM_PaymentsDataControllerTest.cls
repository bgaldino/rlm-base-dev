@isTest
private class RLM_PaymentsDataControllerTest {

    @isTest
    static void optionLists_returnSafeDefaults() {
        Test.startTest();
        String currencyCode = RLM_PaymentsDataController.getOrgDefaultCurrency();
        List<Map<String, String>> accountOptions = RLM_PaymentsDataController.getAccountOptions();
        List<Map<String, String>> currencyOptions = RLM_PaymentsDataController.getCurrencyOptions();
        Test.stopTest();

        System.assert(String.isNotBlank(currencyCode), 'A default currency code is always returned.');
        System.assert(accountOptions.size() >= 1, 'The "All Accounts" sentinel option is always present.');
        System.assertEquals('All Accounts', accountOptions[0].get('label'), 'First account option is the sentinel.');
        System.assert(currencyOptions.size() >= 1, 'The "All Currencies" sentinel option is always present.');
    }

    // The all-items branch (null filters) always returns one summary per tracked status with zero
    // totals when there is no data.
    @isTest
    static void getPaymentScheduleItems_noData_returnsZeroedSummaries() {
        Test.startTest();
        List<RLM_PaymentsDataController.PaymentStatusSummary> summaries =
            RLM_PaymentsDataController.getPaymentScheduleItems(null, null);
        Test.stopTest();

        System.assertEquals(5, summaries.size(),
            'Failed/Ready/Applied/Draft/Processing summaries are always returned.');
        for (RLM_PaymentsDataController.PaymentStatusSummary s : summaries) {
            System.assertEquals(0, s.itemCount, 'No data -> zero items for ' + s.status);
            System.assertEquals(0, s.totalRequestedAmount, 'No data -> zero total for ' + s.status);
        }
    }

    // PaymentScheduleItem is Apex-createable, so the per-status summarization can be exercised with
    // real data. Two Draft items for an account drive the account-filtered branch and addItem().
    @isTest
    static void getPaymentScheduleItems_seededDraftItems_summarized() {
        Account acc = new Account(Name = 'RLM PSI Summary Test');
        insert acc;
        PaymentSchedule ps = new PaymentSchedule(Status = 'Draft', TotalRequestedAmount = 150);
        insert ps;
        insert new List<PaymentScheduleItem>{
            new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id,
                RequestedAmount = 100, TargetPaymentProcessingDate = Date.today(), Status = 'Draft'),
            new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id,
                RequestedAmount = 50, TargetPaymentProcessingDate = Date.today(), Status = 'Draft')
        };

        Test.startTest();
        List<RLM_PaymentsDataController.PaymentStatusSummary> summaries =
            RLM_PaymentsDataController.getPaymentScheduleItems(acc.Id, null);
        Test.stopTest();

        RLM_PaymentsDataController.PaymentStatusSummary draft = null;
        for (RLM_PaymentsDataController.PaymentStatusSummary s : summaries) {
            if (s.status == 'Draft') { draft = s; }
        }
        System.assertNotEquals(null, draft, 'A Draft summary should be present.');
        System.assertEquals(2, draft.itemCount, 'Two Draft items were seeded.');
        System.assertEquals(150, draft.totalRequestedAmount, 'Draft requested total is 100 + 50.');
    }

    // PaymentScheduleItem is Apex-createable, so the account-options aggregate (GROUP BY
    // PaymentAccountId) can be exercised with real data: a seeded item's account must appear.
    @isTest
    static void getAccountOptions_withSeededItem_includesAccount() {
        Account acc = new Account(Name = 'RLM Payments Account Option Test');
        insert acc;
        PaymentSchedule ps = new PaymentSchedule(Status = 'Draft', TotalRequestedAmount = 100);
        insert ps;
        insert new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id,
            RequestedAmount = 100, TargetPaymentProcessingDate = Date.today(), Status = 'Draft');

        Test.startTest();
        List<Map<String, String>> options = RLM_PaymentsDataController.getAccountOptions();
        Test.stopTest();

        Boolean found = false;
        for (Map<String, String> option : options) {
            if (option.get('value') == String.valueOf(acc.Id)) {
                found = true;
                System.assertEquals('RLM Payments Account Option Test', option.get('label'),
                    'The account label should match the seeded account name.');
            }
        }
        System.assert(found, 'An account with a PaymentScheduleItem should appear in the options.');
        System.assert(options.size() >= 2, 'Sentinel "All Accounts" plus the seeded account.');
    }

    // PaymentLineInvoiceLine rows come only from the payment apply API, so the line-level merge
    // is exercised with in-memory rows. JSON builds them with the read-only invoice fields set.
    private static Id fakeId(Schema.SObjectType t, Integer n) {
        return Id.valueOf(t.getDescribe().getKeyPrefix() + String.valueOf(n).leftPad(12, '0'));
    }

    private static PaymentLineInvoiceLine lineApplication(Id paymentId, Id invoiceId, Decimal amount) {
        return (PaymentLineInvoiceLine) JSON.deserialize(JSON.serialize(new Map<String, Object>{
            'PaymentId' => paymentId,
            'Amount' => amount,
            'InvoiceLine' => new Map<String, Object>{
                'Invoice' => new Map<String, Object>{
                    'Id' => invoiceId, 'InvoiceNumber' => 'INV-' + invoiceId, 'TotalAmount' => 500, 'Balance' => 100
                }
            }
        }), PaymentLineInvoiceLine.class);
    }

    @isTest
    static void addLineLevelApplications_sumsLinesPerPaymentAndInvoice() {
        Id pay = fakeId(Payment.SObjectType, 1);
        Id inv1 = fakeId(Invoice.SObjectType, 1);
        Id inv2 = fakeId(Invoice.SObjectType, 2);
        Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>> m =
            new Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>>();

        RLM_PaymentsDataController.addLineLevelApplications(m, new List<PaymentLineInvoiceLine>{
            lineApplication(pay, inv1, 250), lineApplication(pay, inv1, 150), lineApplication(pay, inv2, 50)
        });

        System.assertEquals(2, m.get(pay).size(), 'One entry per invoice.');
        Map<Id, Decimal> applied = new Map<Id, Decimal>();
        for (RLM_PaymentsDataController.InvoiceWrapper iw : m.get(pay)) applied.put(iw.id, iw.appliedAmount);
        System.assertEquals(400, applied.get(inv1), 'Two lines of one invoice are summed.');
        System.assertEquals(50, applied.get(inv2), 'A second invoice keeps its own total.');
        System.assertEquals(100, m.get(pay)[0].balance, 'Invoice fields come from the related invoice.');
    }

    @isTest
    static void addLineLevelApplications_addsToHeaderLevelEntry() {
        Id pay = fakeId(Payment.SObjectType, 1);
        Id inv = fakeId(Invoice.SObjectType, 1);
        RLM_PaymentsDataController.InvoiceWrapper header = new RLM_PaymentsDataController.InvoiceWrapper(
            (Invoice) JSON.deserialize(JSON.serialize(new Map<String, Object>{ 'Id' => inv, 'Balance' => 100 }), Invoice.class));
        header.appliedAmount = 30;
        Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>> m =
            new Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>>{
                pay => new List<RLM_PaymentsDataController.InvoiceWrapper>{ header }
            };

        RLM_PaymentsDataController.addLineLevelApplications(m, new List<PaymentLineInvoiceLine>{ lineApplication(pay, inv, 20) });

        System.assertEquals(1, m.get(pay).size(), 'The invoice is listed once.');
        System.assertEquals(50, m.get(pay)[0].appliedAmount, 'Header 30 plus line 20.');
    }

    @isTest
    static void addHeaderLevelApplications_sumsRepeatApplicationsOfOneInvoice() {
        Id pay = fakeId(Payment.SObjectType, 1);
        Id inv = fakeId(Invoice.SObjectType, 1);
        List<PaymentLineInvoice> rows = new List<PaymentLineInvoice>();
        for (Decimal amount : new List<Decimal>{ 30, 45 }) {
            rows.add((PaymentLineInvoice) JSON.deserialize(JSON.serialize(new Map<String, Object>{
                'PaymentId' => pay, 'InvoiceId' => inv, 'Amount' => amount,
                'Invoice' => new Map<String, Object>{ 'Id' => inv, 'Balance' => 25, 'TotalAmount' => 100 }
            }), PaymentLineInvoice.class));
        }
        Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>> m =
            new Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>>();

        RLM_PaymentsDataController.addHeaderLevelApplications(m, rows);

        System.assertEquals(1, m.get(pay).size(), 'Two applications to one invoice are listed once.');
        System.assertEquals(75, m.get(pay)[0].appliedAmount, '30 + 45.');
        System.assertEquals(25, m.get(pay)[0].balance, 'Invoice fields come from the related invoice.');
    }

    @isTest
    static void addLineLevelApplications_skipsRowsWithoutAReadableInvoice() {
        Id pay = fakeId(Payment.SObjectType, 1);
        PaymentLineInvoiceLine orphan = (PaymentLineInvoiceLine) JSON.deserialize(
            JSON.serialize(new Map<String, Object>{ 'PaymentId' => pay, 'Amount' => 10 }), PaymentLineInvoiceLine.class);
        Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>> m =
            new Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>>();

        RLM_PaymentsDataController.addLineLevelApplications(m, new List<PaymentLineInvoiceLine>{ orphan });

        System.assert(m.isEmpty(), 'A row without its invoice is skipped, not a NullPointerException.');
    }
}
