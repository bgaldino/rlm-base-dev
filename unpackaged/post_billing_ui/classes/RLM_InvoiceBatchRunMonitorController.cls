public with sharing class RLM_InvoiceBatchRunMonitorController {

    @AuraEnabled
    public static Map<String, Integer> getInvoiceStatusCounts(String invoiceBatchRunId) {
        Map<String, Integer> counts = new Map<String, Integer>{
            'Draft' => 0,
            'Pending' => 0,
            'Posted' => 0,
            'Error' => 0
        };

        if (String.isBlank(invoiceBatchRunId)) {
            return counts;
        }

        List<AggregateResult> results = [
            SELECT Status, COUNT(Id) cnt
            FROM Invoice
            WHERE InvoiceBatchRunId = :invoiceBatchRunId
            WITH USER_MODE
            GROUP BY Status
        ];

        for (AggregateResult ar : results) {
            addCount(counts, (String) ar.get('Status'), (Integer) ar.get('cnt'));
        }

        return counts;
    }

    // Records one status's count. Takes values, not an AggregateResult, so a test can pass
    // counts for invoices, which Apex cannot insert.
    @TestVisible
    private static void addCount(Map<String, Integer> counts, String status, Integer cnt) {
        if (status != null) {
            counts.put(status, cnt);
        }
    }
}