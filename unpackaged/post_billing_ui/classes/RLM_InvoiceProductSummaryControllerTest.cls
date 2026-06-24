@isTest
private class RLM_InvoiceProductSummaryControllerTest {

    private static Id fakeInvoiceId() {
        return Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
    }

    // Invoices/InvoiceLines are system-managed and not insertable in Apex tests. A non-existent
    // invoice makes the single-row Invoice query throw, surfaced as an AuraHandledException.
    @isTest
    static void getInvoiceProductSummary_unknownInvoice_throws() {
        Boolean threw = false;
        Test.startTest();
        try {
            RLM_InvoiceProductSummaryController.getInvoiceProductSummary(fakeInvoiceId());
        } catch (AuraHandledException e) {
            threw = true;
        }
        Test.stopTest();
        System.assert(threw, 'A non-existent invoice should raise an AuraHandledException.');
    }

    // No invoice lines -> nothing to update; the method must return without writing any records.
    @isTest
    static void saveLineAttributes_unknownInvoice_noOp() {
        Test.startTest();
        Integer rowsBefore = Limits.getDmlRows();
        RLM_InvoiceProductSummaryController.saveLineAttributes(fakeInvoiceId());
        Integer rowsAfter = Limits.getDmlRows();
        Test.stopTest();
        System.assertEquals(rowsBefore, rowsAfter,
            'A non-existent invoice has no lines, so no records may be updated.');
    }
}
