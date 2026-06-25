@isTest
private class RLM_InvoiceSummaryControllerTest {

    // Invoices/DebitMemos/Disputes/PSIs are system-managed and not insertable in Apex tests.
    // An Account with no billing activity drives every query down its empty path, verifying
    // the summary is fully zero-initialized and the (USER_MODE) queries run clean.
    @isTest
    static void getInvoiceSummary_accountWithNoBilling_returnsZeroedSummary() {
        Account acc = new Account(Name = 'RLM Invoice Summary Test');
        insert acc;

        Test.startTest();
        RLM_InvoiceSummaryController.InvoiceSummaryData data =
            RLM_InvoiceSummaryController.getInvoiceSummary(acc.Id);
        Test.stopTest();

        System.assertNotEquals(null, data, 'A summary should always be returned.');
        System.assertEquals(0, data.totalDue, 'No invoices -> zero total due.');
        System.assertEquals(0, data.totalInvoices, 'No invoices -> zero invoice count.');
        System.assertEquals(0, data.openInvoices, 'No invoices -> zero open invoices.');
        System.assertEquals(0, data.overdueAmount, 'No invoices -> zero overdue amount.');
        System.assertEquals(0, data.overdueCount, 'No invoices -> zero overdue count.');
        System.assertEquals(0, data.disputeAmount, 'No disputes -> zero dispute amount.');
        System.assertEquals(0, data.disputeCount, 'No disputes -> zero dispute count.');
        System.assertEquals(0, data.debitAmount, 'No debit memos -> zero debit amount.');
        System.assertEquals(0, data.promiseToPayCount, 'No PSIs -> zero promise-to-pay count.');
        System.assertEquals(0, data.paidCount, 'No settled invoices -> zero paid count.');
        System.assertEquals(Date.today(), data.periodEnd,
            'With no invoices the period end defaults to today.');
    }

    // Exercises the classification seam with synthetic invoices: current vs overdue bucketing,
    // null-due-date handling (treated as current), totals, and period-window derivation.
    @isTest
    static void classifyInvoices_bucketsCurrentOverdueAndPeriod() {
        Date today = Date.today();
        List<SObject> invoices = new List<SObject>{
            synthInvoice(100, today.addDays(-10)), // overdue
            synthInvoice(50, today.addDays(10)),   // current
            synthInvoice(25, null)                 // no due date -> current bucket
        };

        RLM_InvoiceSummaryController.InvoiceSummaryData data =
            new RLM_InvoiceSummaryController.InvoiceSummaryData();
        data.totalDue = 0; data.openInvoices = 0;
        data.overdueAmount = 0; data.overdueCount = 0;
        data.currentAmount = 0; data.currentCount = 0;

        Test.startTest();
        RLM_InvoiceSummaryController.classifyInvoices(
            invoices, data, today, false, 'USD', new Map<String, Decimal>());
        Test.stopTest();

        System.assertEquals(175, data.totalDue, 'Sum of all balances.');
        System.assertEquals(3, data.openInvoices, 'All three are open.');
        System.assertEquals(3, data.totalInvoices, 'Total invoice count.');
        System.assertEquals(100, data.overdueAmount, 'Only the past-due invoice is overdue.');
        System.assertEquals(1, data.overdueCount, 'One overdue invoice.');
        System.assertEquals(75, data.currentAmount, 'Future-due + no-due-date are current.');
        System.assertEquals(2, data.currentCount, 'Two current invoices.');
        System.assertEquals(today.addDays(-10), data.periodStart, 'Earliest due date.');
        System.assertEquals(today.addDays(10), data.periodEnd, 'Latest due date.');
    }

    @isTest
    static void convertCurrency_coversIdentityAndCrossRate() {
        Map<String, Decimal> rates = new Map<String, Decimal>{ 'USD' => 1, 'EUR' => 0.5 };
        System.assertEquals(100,
            RLM_InvoiceSummaryController.convertCurrency(100, 'USD', 'USD', rates),
            'Same currency is a no-op.');
        System.assertEquals(0,
            RLM_InvoiceSummaryController.convertCurrency(0, 'EUR', 'USD', rates),
            'Zero amount short-circuits.');
        System.assertEquals(200,
            RLM_InvoiceSummaryController.convertCurrency(100, 'EUR', 'USD', rates),
            '100 EUR @0.5 -> 200 USD @1.0.');
    }

    private static Integer seq = 0;

    private static Id mintInvoiceId() {
        seq++;
        String suffix = String.valueOf(seq);
        while (suffix.length() < 12) {
            suffix = '0' + suffix;
        }
        return Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + suffix);
    }

    // Invoice fields aren't writeable on a constructed sObject; build via JSON to set
    // Balance and DueDate for the classification logic.
    private static SObject synthInvoice(Decimal balance, Date dueDate) {
        Map<String, Object> m = new Map<String, Object>{
            'attributes' => new Map<String, Object>{ 'type' => 'Invoice' },
            'Id'         => mintInvoiceId(),
            'Balance'    => balance
        };
        if (dueDate != null) {
            m.put('DueDate', dueDate);
        }
        return (SObject) JSON.deserialize(JSON.serialize(m), Invoice.class);
    }
}
