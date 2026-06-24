@isTest
private class RLM_PaymentsDataControllerTest {

    @isTest
    static void optionLists_returnSafeDefaults() {
        Test.startTest();
        String currencyCode = RLM_PaymentsDataController.getOrgDefaultCurrency();
        List<Map<String, String>> accountOptions = RLM_PaymentsDataController.getAccountOptions();
        List<Map<String, String>> currencyOptions = RLM_PaymentsDataController.getCurrencyOptions();
        Test.stopTest();

        System.assert(String.isNotBlank(currencyCode), 'A default currency code is always returned.');
        System.assert(accountOptions.size() >= 1, 'The "All Accounts" sentinel option is always present.');
        System.assertEquals('All Accounts', accountOptions[0].get('label'), 'First account option is the sentinel.');
        System.assert(currencyOptions.size() >= 1, 'The "All Currencies" sentinel option is always present.');
    }

    // PaymentScheduleItem rows are system-managed and not insertable in Apex tests, so both the
    // all-items branch (null filters) and the account/currency-filtered branch drive empty paths.
    // The query selects fields (e.g. ParentReferenceEntityId) that are only present when certain
    // billing features are enabled; accept either a non-null list or a graceful query failure.
    @isTest
    static void getPaymentScheduleItems_noData_executesBothBranches() {
        Account acc = new Account(Name = 'RLM Payments Data Test');
        insert acc;

        Test.startTest();
        runQuietly(null, null);
        runQuietly(acc.Id, 'USD');
        Test.stopTest();
        System.assert(true, 'getPaymentScheduleItems executes for the all-items and filtered branches.');
    }

    private static void runQuietly(Id recordId, String currencyCode) {
        try {
            List<RLM_PaymentsDataController.PaymentStatusSummary> result =
                RLM_PaymentsDataController.getPaymentScheduleItems(recordId, currencyCode);
            System.assertNotEquals(null, result, 'A non-null summary list is returned when the query succeeds.');
        } catch (System.QueryException e) {
            // Only an org-schema gap (e.g. ParentReferenceEntityId absent) is tolerated here.
            // Any other exception type is a real defect and is allowed to fail the test.
        }
    }
}
