/**
 * Apex controller for the Billing Case Metrics LWC.
 * Aggregates open billing cases, disputes, and disputed invoice data.
 */
public with sharing class RLM_BillingCaseMetricsController {

    @AuraEnabled(cacheable=true)
    public static Map<String, Object> getMetrics() {
        Map<String, Object> result = new Map<String, Object>();

        // Open Billing Cases: Cases with Type = 'Billing' and Status is open
        Integer openBillingCases = 0;
        try {
            List<AggregateResult> caseAgg = [
                SELECT COUNT(Id) cnt
                FROM Case
                WHERE IsClosed = false
                AND Type = 'Billing'
            ];
            openBillingCases = (Integer) caseAgg[0].get('cnt');
        } catch (Exception e) {
            // fallback
        }
        result.put('openBillingCases', openBillingCases);

        // Open Disputes
        Integer openDisputes = 0;
        Decimal totalDisputedAmount = 0;
        try {
            List<AggregateResult> disputeAgg = Database.query(
                'SELECT COUNT(Id) cnt, SUM(DisputedAmount) totalAmt ' +
                'FROM Dispute WHERE IsClosed = false'
            );
            openDisputes = (Integer) disputeAgg[0].get('cnt');
            Object amt = disputeAgg[0].get('totalAmt');
            totalDisputedAmount = amt != null ? (Decimal) amt : 0;
        } catch (Exception e) {
            // Dispute object might not be available
        }
        result.put('openDisputes', openDisputes);
        result.put('totalDisputedAmount', totalDisputedAmount);

        // Disputed Invoices: count of unique invoices linked to open disputes
        Integer disputedInvoices = 0;
        try {
            List<AggregateResult> invAgg = Database.query(
                'SELECT COUNT_DISTINCT(InvoiceId) cnt ' +
                'FROM Dispute WHERE IsClosed = false AND InvoiceId != null'
            );
            disputedInvoices = (Integer) invAgg[0].get('cnt');
        } catch (Exception e) {
            // fallback
        }
        result.put('disputedInvoices', disputedInvoices);

        return result;
    }
}