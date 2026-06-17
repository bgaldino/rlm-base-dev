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
            GROUP BY Status
        ];

        for (AggregateResult ar : results) {
            String status = (String) ar.get('Status');
            Integer cnt = (Integer) ar.get('cnt');
            if (status != null) {
                counts.put(status, cnt);
            }
        }

        return counts;
    }
}