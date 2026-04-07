/**
 * Apex controller for the Billing Case Metrics LWC.
 * Aggregates open billing cases, disputes, and disputed invoice data.
 *
 * Dispute object fields (IsClosed, DisputedAmount, InvoiceId) were removed
 * in release 262. Queries use Schema describe to check field availability
 * before executing.
 */
public with sharing class RLM_BillingCaseMetricsController {

    @AuraEnabled(cacheable=true)
    public static Map<String, Object> getMetrics() {
        Map<String, Object> result = new Map<String, Object>();

        result.put('openBillingCases', countOpenBillingCases());

        Map<String, Object> disputeMetrics = queryDisputeMetrics();
        result.put('openDisputes', disputeMetrics.get('openDisputes'));
        result.put('totalDisputedAmount', disputeMetrics.get('totalDisputedAmount'));
        result.put('disputedInvoices', disputeMetrics.get('disputedInvoices'));

        return result;
    }

    private static Integer countOpenBillingCases() {
        try {
            List<AggregateResult> caseAgg = [
                SELECT COUNT(Id) cnt
                FROM Case
                WHERE IsClosed = false
                AND Type = 'Billing'
            ];
            return (Integer) caseAgg[0].get('cnt');
        } catch (Exception e) {
            return 0;
        }
    }

    private static Map<String, Object> queryDisputeMetrics() {
        Map<String, Object> metrics = new Map<String, Object>{
            'openDisputes' => 0,
            'totalDisputedAmount' => (Decimal) 0,
            'disputedInvoices' => 0
        };

        if (!Schema.getGlobalDescribe().containsKey('Dispute')) {
            return metrics;
        }

        Map<String, Schema.SObjectField> disputeFields =
            Schema.getGlobalDescribe().get('Dispute').getDescribe().fields.getMap();

        Boolean hasIsClosed = disputeFields.containsKey('IsClosed');
        Boolean hasDisputedAmount = disputeFields.containsKey('DisputedAmount');
        Boolean hasInvoiceId = disputeFields.containsKey('InvoiceId');

        if (hasIsClosed) {
            try {
                String selectClause = 'SELECT COUNT(Id) cnt';
                if (hasDisputedAmount) {
                    selectClause += ', SUM(DisputedAmount) totalAmt';
                }
                List<AggregateResult> disputeAgg = Database.query(
                    selectClause + ' FROM Dispute WHERE IsClosed = false'
                );
                metrics.put('openDisputes', (Integer) disputeAgg[0].get('cnt'));
                if (hasDisputedAmount) {
                    Object amt = disputeAgg[0].get('totalAmt');
                    metrics.put('totalDisputedAmount', amt != null ? (Decimal) amt : 0);
                }
            } catch (Exception e) { /* field removed or object inaccessible */ }

            if (hasInvoiceId) {
                try {
                    List<AggregateResult> invAgg = Database.query(
                        'SELECT COUNT_DISTINCT(InvoiceId) cnt ' +
                        'FROM Dispute WHERE IsClosed = false AND InvoiceId != null'
                    );
                    metrics.put('disputedInvoices', (Integer) invAgg[0].get('cnt'));
                } catch (Exception e) { /* field removed or object inaccessible */ }
            }
        }

        return metrics;
    }
}