@isTest
private class RLM_InvoiceAgingControllerTest {

    @isTest
    static void getInvoiceAgingData_nullAccount_returnsEmptyData() {
        Test.startTest();
        RLM_InvoiceAgingController.InvoiceAgingData data =
            RLM_InvoiceAgingController.getInvoiceAgingData(null);
        Test.stopTest();
        System.assertNotEquals(null, data, 'A non-null aging wrapper should always be returned.');
        System.assertEquals(0, data.totalInvoices, 'A null account id short-circuits to zero invoices.');
    }

    // Invoices cannot be created in Apex tests. An Account with no billing activity drives the
    // query and aggregation down their empty path. It runs as a billing operations user rather
    // than the deploying admin: RLM_BillingUI is assigned only after this bundle deploys.
    @isTest
    static void getInvoiceAgingData_accountWithNoInvoices_returnsZeroes() {
        // The controller filters invoices by this id and never reads Account itself.
        Account acc = new Account(Name = 'RLM Invoice Aging Test');
        insert acc;
        User u = billingOperationsUser();

        RLM_InvoiceAgingController.InvoiceAgingData data;
        Test.startTest();
        System.runAs(u) {
            String readError = invoiceReadError();
            Assert.isNull(readError, 'PRECONDITION: a billing operations user can read the aging fields of Invoice: ' + readError);
            data = RLM_InvoiceAgingController.getInvoiceAgingData(acc.Id);
        }
        Test.stopTest();
        Assert.isNotNull(data, 'A non-null aging wrapper should be returned.');
        Assert.areEqual(0, data.totalInvoices, 'No posted invoices -> zero count.');
    }

    // The same account loads for a billing operations user; a user who cannot read invoices
    // gets a handled error, not a raw QueryException. Both premises are checked, so the error is
    // shown to come from the user's access and not from the account.
    @isTest
    static void getInvoiceAgingData_userWithoutInvoiceAccess_throwsAHandledError() {
        // The controller filters invoices by this id and never reads Account itself.
        Account acc = new Account(Name = 'RLM Invoice Aging Access Test');
        insert acc;
        User billingUser = billingOperationsUser();
        // Minimum Access with no license or permission set: no billing object is readable.
        User u = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        Boolean premise = false;
        Boolean threw = false;
        Test.startTest();
        System.runAs(billingUser) {
            String readError = invoiceReadError();
            Assert.isNull(readError, 'PRECONDITION: a billing operations user can read the aging fields of Invoice: ' + readError);
            Assert.areEqual(0, RLM_InvoiceAgingController.getInvoiceAgingData(acc.Id).totalInvoices,
                'PRECONDITION: the account loads for a billing operations user, with no invoices.');
        }
        System.runAs(u) {
            premise = invoiceReadError() != null;
            try {
                RLM_InvoiceAgingController.getInvoiceAgingData(acc.Id);
            } catch (AuraHandledException e) {
                threw = true;
            }
        }
        Test.stopTest();
        Assert.isTrue(premise, 'PRECONDITION: this user must be unable to read Invoice.');
        Assert.isTrue(threw, 'An unreadable invoice query must surface as an AuraHandledException.');
    }

    private static User billingOperationsUser() {
        return RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
    }

    // The controller's own field list, run in USER_MODE: returns its error, or null if it runs.
    private static String invoiceReadError() {
        try {
            Database.query(
                'SELECT Id, InvoiceNumber, DaysInvoiceOpen, DaysInvoiceOverdue, TotalAmountWithTax, Balance, '
                + 'DueDate, InvoiceDate, CurrencyIsoCode, Status, SettlementStatus FROM Invoice '
                + 'WHERE BillingAccountId != null LIMIT 1',
                AccessLevel.USER_MODE);
            return null;
        } catch (QueryException e) {
            return e.getMessage();
        }
    }

    // Invoices cannot be inserted in Apex, so these build them with JSON.deserialize, read-only
    // aging fields included, and pass them to the method the controller calls with its query.
    private static Invoice invoice(Decimal balance, Decimal daysOpen, Decimal daysOverdue, String currencyCode) {
        return (Invoice) JSON.deserialize(JSON.serialize(new Map<String, Object>{
            'Balance' => balance, 'DaysInvoiceOpen' => daysOpen, 'DaysInvoiceOverdue' => daysOverdue,
            'CurrencyIsoCode' => currencyCode
        }), Invoice.class);
    }

    // Each invoice lands in one age bucket by days open (30 and 60 start the next bucket; a blank
    // age counts as 0), is overdue when its overdue days are above zero, and adds its balance.
    @isTest
    static void processInvoiceData_bucketsByAgeAndTotalsTheBalance() {
        List<Invoice> invoices = new List<Invoice>{
            invoice(100, 10, 0, 'EUR'),
            invoice(50, 30, 5, 'EUR'),
            invoice(null, 60, null, null),
            invoice(25.5, null, -1, null)
        };

        Test.startTest();
        RLM_InvoiceAgingController.InvoiceAgingData data = RLM_InvoiceAgingController.processInvoiceData(invoices);
        Test.stopTest();

        Assert.areEqual(4, data.totalInvoices, 'Every invoice is counted');
        Assert.areEqual(1, data.overdueInvoices, 'Only positive overdue days count as overdue');
        Assert.areEqual(175.5, data.totalAmount, 'The balances add up; a blank balance adds nothing');
        Assert.areEqual(25, data.averageAge, 'The average age is (10 + 30 + 60 + 0) / 4');
        Assert.areEqual(2, data.lessThan30, 'Ages 10 and blank (0) are under 30 days');
        Assert.areEqual(1, data.days30To60, 'Age 30 starts the 30-60 bucket');
        Assert.areEqual(1, data.moreThan60, 'Age 60 starts the over-60 bucket');
        Assert.areEqual('EUR', data.currencyCode, 'The currency comes from the invoices');
        Assert.areEqual(invoices, data.invoices, 'The invoices are returned for the table');
    }

    // No invoices, or invoices without a currency, leave the defaults: zero counts and USD.
    @isTest
    static void processInvoiceData_defaultsWhenThereIsNothingToCount() {
        Test.startTest();
        RLM_InvoiceAgingController.InvoiceAgingData fromNull = RLM_InvoiceAgingController.processInvoiceData(null);
        RLM_InvoiceAgingController.InvoiceAgingData fromEmpty =
            RLM_InvoiceAgingController.processInvoiceData(new List<Invoice>());
        RLM_InvoiceAgingController.InvoiceAgingData noCurrency =
            RLM_InvoiceAgingController.processInvoiceData(new List<Invoice>{ invoice(10, 5, 0, null) });
        Test.stopTest();

        Assert.areEqual(0, fromNull.totalInvoices, 'No invoices: zero count');
        Assert.areEqual(0, fromEmpty.totalAmount, 'No invoices: zero amount');
        Assert.isTrue(fromEmpty.invoices.isEmpty(), 'No invoices: an empty list, never null');
        Assert.areEqual('USD', noCurrency.currencyCode, 'An invoice without a currency leaves the USD default');
        Assert.areEqual(5, noCurrency.averageAge, 'One invoice: its own age is the average');
    }
}
