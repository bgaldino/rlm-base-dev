@isTest
private class RLM_BillingCaseMetricsControllerTest {

    // With no Cases or Disputes, every aggregate resolves to zero. Dispute is a license-gated
    // extension; the controller degrades gracefully whether or not it is present in the org.
    @isTest
    static void getMetrics_noData_returnsZeroedKeys() {
        Test.startTest();
        Map<String, Object> result = RLM_BillingCaseMetricsController.getMetrics();
        Test.stopTest();

        System.assertNotEquals(null, result, 'A non-null metrics map should always be returned.');
        System.assert(result.containsKey('openBillingCases'), 'openBillingCases key expected.');
        System.assert(result.containsKey('openDisputes'), 'openDisputes key expected.');
        System.assert(result.containsKey('totalDisputedAmount'), 'totalDisputedAmount key expected.');
        System.assert(result.containsKey('disputedInvoices'), 'disputedInvoices key expected.');

        System.assertEquals(0, (Integer) result.get('openBillingCases'), 'No billing cases -> zero.');
        System.assertEquals(0, (Integer) result.get('openDisputes'), 'No disputes -> zero.');
        System.assertEquals(0, (Integer) result.get('disputedInvoices'), 'No disputed invoices -> zero.');
        System.assertNotEquals(null, result.get('totalDisputedAmount'), 'Disputed amount should default to zero, not null.');
    }
}
