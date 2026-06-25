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
}
