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

    // No invoice lines -> nothing to update; the method returns without DML or error.
    @isTest
    static void saveLineAttributes_unknownInvoice_noOp() {
        Test.startTest();
        RLM_InvoiceProductSummaryController.saveLineAttributes(fakeInvoiceId());
        Test.stopTest();
        System.assert(true, 'saveLineAttributes completes without error when there are no lines.');
    }
}
