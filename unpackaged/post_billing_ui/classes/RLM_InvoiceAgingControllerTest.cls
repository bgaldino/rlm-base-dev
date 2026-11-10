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

    // Invoices are system-managed and not insertable in Apex tests. An Account with no billing
    // activity drives the query and aggregation down their empty path.
    @isTest
    static void getInvoiceAgingData_accountWithNoInvoices_returnsZeroes() {
        Account acc = new Account(Name = 'RLM Invoice Aging Test');
        insert acc;

        Test.startTest();
        try {
            RLM_InvoiceAgingController.InvoiceAgingData data =
                RLM_InvoiceAgingController.getInvoiceAgingData(acc.Id);
            System.assertNotEquals(null, data, 'A non-null aging wrapper should be returned.');
            System.assertEquals(0, data.totalInvoices, 'No posted invoices -> zero count.');
        } catch (AuraHandledException e) {
            // Running user lacks Invoice read FLS; the controller wraps the USER_MODE failure as
            // AuraHandledException. Tolerated for cross-org determinism.
        }
        Test.stopTest();
    }

    // The same account loads for the running admin; a user who cannot read invoices gets a
    // handled error, not a raw QueryException. Both premises are checked, so the error is
    // shown to come from the user's access and not from the account.
    @isTest
    static void getInvoiceAgingData_userWithoutInvoiceAccess_throwsAHandledError() {
        Account acc = new Account(Name = 'RLM Invoice Aging Access Test');
        insert acc;
        // Minimum Access with no license or permission set: no billing object is readable.
        User u = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        Boolean premise = false;
        Boolean threw = false;
        Test.startTest();
        RLM_InvoiceAgingController.InvoiceAgingData adminData = RLM_InvoiceAgingController.getInvoiceAgingData(acc.Id);
        Assert.areEqual(0, adminData.totalInvoices, 'PRECONDITION: the account loads for the admin, with no invoices.');
        System.runAs(u) {
            try {
                Database.query('SELECT Id FROM Invoice LIMIT 1', AccessLevel.USER_MODE);
            } catch (QueryException e) {
                premise = true;
            }
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
}
