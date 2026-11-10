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
}
