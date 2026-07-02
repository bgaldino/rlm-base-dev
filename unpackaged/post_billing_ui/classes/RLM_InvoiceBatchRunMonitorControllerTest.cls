@isTest
private class RLM_InvoiceBatchRunMonitorControllerTest {

    @isTest
    static void getInvoiceStatusCounts_blank_returnsZeroedMap() {
        Test.startTest();
        Map<String, Integer> counts =
            RLM_InvoiceBatchRunMonitorController.getInvoiceStatusCounts('');
        Test.stopTest();
        System.assertEquals(4, counts.size(), 'All four status buckets should be present.');
        System.assertEquals(0, counts.get('Draft'), 'Blank id -> zero Draft.');
        System.assertEquals(0, counts.get('Pending'), 'Blank id -> zero Pending.');
        System.assertEquals(0, counts.get('Posted'), 'Blank id -> zero Posted.');
        System.assertEquals(0, counts.get('Error'), 'Blank id -> zero Error.');
    }

    @isTest
    static void getInvoiceStatusCounts_nullId_returnsZeroedMap() {
        Test.startTest();
        Map<String, Integer> counts =
            RLM_InvoiceBatchRunMonitorController.getInvoiceStatusCounts(null);
        Test.stopTest();
        System.assertEquals(0, counts.get('Posted'), 'Null id should short-circuit to zeros.');
    }

    // Exercise the aggregate-query path with a correctly-typed but nonexistent batch-run id
    // so the GROUP BY query runs and returns no rows (rather than throwing). Guarded on the
    // object being present in this org variant.
    @isTest
    static void getInvoiceStatusCounts_unknownBatchRun_returnsZeroedMap() {
        Schema.SObjectType ibrType = Schema.getGlobalDescribe().get('InvoiceBatchRun');
        if (ibrType == null) {
            return; // InvoiceBatchRun not provisioned in this org variant
        }
        Id fakeId = Id.valueOf(ibrType.getDescribe().getKeyPrefix() + '000000000000');
        Test.startTest();
        Map<String, Integer> counts =
            RLM_InvoiceBatchRunMonitorController.getInvoiceStatusCounts(String.valueOf(fakeId));
        Test.stopTest();
        System.assertEquals(0, counts.get('Posted'),
            'An unknown batch-run id should yield no posted invoices.');
    }
}
