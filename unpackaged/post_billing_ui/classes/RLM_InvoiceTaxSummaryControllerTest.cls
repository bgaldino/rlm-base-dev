@isTest
private class RLM_InvoiceTaxSummaryControllerTest {

    // An InvoiceLineTax row needs an InvoiceLine, which cannot be created in Apex tests; a null id
    // and a well-formed but non-existent Invoice id both drive the empty aggregate path.
    @isTest
    static void getTaxSummaryByInvoice_nullId_returnsEmptyList() {
        Test.startTest();
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows =
            RLM_InvoiceTaxSummaryController.getTaxSummaryByInvoice(null);
        Test.stopTest();
        System.assertNotEquals(null, rows, 'A non-null list should always be returned.');
        System.assertEquals(0, rows.size(), 'A null invoice id short-circuits to an empty list.');
    }

    @isTest
    static void getTaxSummaryByInvoice_unknownInvoice_returnsEmptyList() {
        Id fakeInvoice = Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
        Test.startTest();
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows =
            RLM_InvoiceTaxSummaryController.getTaxSummaryByInvoice(fakeInvoice);
        Test.stopTest();
        System.assertNotEquals(null, rows, 'A non-null list should always be returned.');
        System.assertEquals(0, rows.size(), 'No tax rows exist for a non-existent invoice.');
    }

    // The positive path as a billing operations user rather than the deploying admin
    // (RLM_BillingUI is assigned only after this bundle deploys): the user can run the tax
    // query's exact field list in USER_MODE, and an unknown invoice returns an empty list.
    @isTest
    static void getTaxSummaryByInvoice_billingOperationsUser_runsTheQuery() {
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
        Id fakeInvoice = Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
        String readError;
        List<RLM_InvoiceTaxSummaryController.TaxSummaryRow> rows;
        Test.startTest();
        System.runAs(u) {
            try {
                Database.query(
                    'SELECT TaxName, TaxAmount, CurrencyIsoCode FROM InvoiceLineTax '
                    + 'WHERE InvoiceLine.InvoiceId != null LIMIT 1',
                    AccessLevel.USER_MODE);
            } catch (QueryException e) {
                readError = e.getMessage();
            }
            Assert.isNull(readError,
                'PRECONDITION: a billing operations user can run the tax query\'s fields: ' + readError);
            rows = RLM_InvoiceTaxSummaryController.getTaxSummaryByInvoice(fakeInvoice);
        }
        Test.stopTest();
        Assert.isNotNull(rows, 'The tax summary list is returned.');
        Assert.areEqual(0, rows.size(), 'No tax rows exist for a non-existent invoice.');
    }

    // Coverage-only check of the TaxSummaryRow constructor: it keeps each argument in its own
    // field. (The aggregate mapping that calls it needs InvoiceLineTax rows, whose required
    // InvoiceLine cannot be created in a test, so it is not covered here.)
    // Documented, not pinned (no InvoiceLineTax row can be created): the controller's
    // SUM(TaxAmount) ... GROUP BY TaxName, CurrencyIsoCode returns each total in the corporate
    // currency, but labels it with the group's CurrencyIsoCode, so a non-corporate tax line's
    // total would be shown under the wrong currency.
    @isTest
    static void taxSummaryRow_coverageOnlyConstructorCheck() {
        RLM_InvoiceTaxSummaryController.TaxSummaryRow row =
            new RLM_InvoiceTaxSummaryController.TaxSummaryRow('State Sales Tax', 12.50, 'EUR');
        Assert.areEqual('State Sales Tax', row.taxName, 'The tax name is kept.');
        Assert.areEqual(12.50, row.totalTaxAmount, 'The tax total is kept.');
        Assert.areEqual('EUR', row.currencyIsoCode, 'The currency of the total is kept.');
    }
}
