@isTest
private class RLM_InvoiceTaxSummaryControllerTest {

    // InvoiceLineTax rows are system-generated and not insertable in Apex tests; a null id
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

    // Each aggregate row becomes one TaxSummaryRow carrying the tax name, its total and the
    // currency it is in, which is what the LWC renders per tax.
    @isTest
    static void taxSummaryRow_carriesNameTotalAndCurrency() {
        Test.startTest();
        RLM_InvoiceTaxSummaryController.TaxSummaryRow row =
            new RLM_InvoiceTaxSummaryController.TaxSummaryRow('State Sales Tax', 12.50, 'EUR');
        Test.stopTest();
        Assert.areEqual('State Sales Tax', row.taxName, 'The tax name is kept.');
        Assert.areEqual(12.50, row.totalTaxAmount, 'The tax total is kept.');
        Assert.areEqual('EUR', row.currencyIsoCode, 'The currency of the total is kept.');
    }
}
