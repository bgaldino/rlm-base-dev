/**
 * Apex controller for the Billing Case Metrics LWC.
 * Aggregates open billing cases, disputes, and disputed invoice data.
 *
 * The Dispute object and its fields (Status, DisputedAmount, InvoiceId) are
 * license-gated billing extensions: present at runtime when the Revenue Cloud
 * Billing license / Billing Operations User permission set are assigned, but not
 * surfaced to the Apex compiler for static SOQL. Queries therefore use Schema
 * describe to check availability and dynamic SOQL (USER_MODE) to execute, so the
 * class compiles in every org and degrades gracefully where Dispute is absent.
 */
public with sharing class RLM_BillingCaseMetricsController {

    // The last dispute query failure, for tests: the metrics swallow it and show zero,
    // so without this a broken query is indistinguishable from no disputes.
    @TestVisible
    private static String lastDisputeQueryError;

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
                WITH USER_MODE
            ];
            return (Integer) caseAgg[0].get('cnt');
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'RLM_BillingCaseMetricsController.countOpenBillingCases failed: ' + e.getMessage());
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

        // Dispute has no IsClosed field. Open means Status is not 'Closed', the rule
        // RLM_OnAccountBillingController uses.
        Boolean hasStatus = disputeFields.containsKey('Status');
        Boolean hasDisputedAmount = disputeFields.containsKey('DisputedAmount');
        Boolean hasInvoiceId = disputeFields.containsKey('InvoiceId');

        if (hasStatus) {
            try {
                String selectClause = 'SELECT COUNT(Id) cnt';
                if (hasDisputedAmount) {
                    selectClause += ', SUM(DisputedAmount) totalAmt';
                }
                List<AggregateResult> disputeAgg = Database.query(
                    selectClause + ' FROM Dispute WHERE Status != \'Closed\'', AccessLevel.USER_MODE
                );
                metrics.put('openDisputes', (Integer) disputeAgg[0].get('cnt'));
                if (hasDisputedAmount) {
                    Object amt = disputeAgg[0].get('totalAmt');
                    metrics.put('totalDisputedAmount', amt != null ? (Decimal) amt : 0);
                }
            } catch (Exception e) {
                // Dispute field not accessible (license/extension not enabled) — keep zero defaults.
                lastDisputeQueryError = e.getMessage();
                System.debug(LoggingLevel.WARN, 'RLM_BillingCaseMetricsController dispute aggregate failed: ' + e.getMessage());
            }

            if (hasInvoiceId) {
                try {
                    List<AggregateResult> invAgg = Database.query(
                        'SELECT COUNT_DISTINCT(InvoiceId) cnt ' +
                        'FROM Dispute WHERE Status != \'Closed\' AND InvoiceId != null', AccessLevel.USER_MODE
                    );
                    metrics.put('disputedInvoices', (Integer) invAgg[0].get('cnt'));
                } catch (Exception e) {
                    // Dispute.InvoiceId not accessible (license/extension not enabled) — keep zero default.
                    lastDisputeQueryError = e.getMessage();
                    System.debug(LoggingLevel.WARN, 'RLM_BillingCaseMetricsController disputed-invoice aggregate failed: ' + e.getMessage());
                }
            }
        }

        return metrics;
    }
}