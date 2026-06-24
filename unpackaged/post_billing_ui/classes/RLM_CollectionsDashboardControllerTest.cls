@isTest
private class RLM_CollectionsDashboardControllerTest {

    // Every dashboard entrypoint is defensive: each catches internally and returns a populated
    // wrapper/list even when the underlying collections objects hold no data or are license-gated.
    // An Account with no billing activity exercises the account-filtered branches.
    @isTest
    static void allEntrypoints_noData_returnNonNull() {
        Account acc = new Account(Name = 'RLM Collections Dashboard Test');
        insert acc;

        Test.startTest();
        System.assert(String.isNotBlank(RLM_CollectionsDashboardController.getOrgDefaultCurrency()),
            'A default currency is always returned.');

        List<Map<String, String>> accountOptions = RLM_CollectionsDashboardController.getAccountOptions();
        System.assert(accountOptions.size() >= 1, 'The "All Accounts" sentinel option is present.');

        List<Map<String, String>> currencyOptions = RLM_CollectionsDashboardController.getCurrencyOptions();
        System.assert(currencyOptions.size() >= 1, 'The "All Currencies" sentinel option is present.');

        System.assertNotEquals(null,
            RLM_CollectionsDashboardController.getPaymentPromiseSummary(null, null),
            'Promise summary returns a non-null list (no filter).');
        System.assertNotEquals(null,
            RLM_CollectionsDashboardController.getPaymentPromiseSummary(acc.Id, 'USD'),
            'Promise summary returns a non-null list (account filter).');

        System.assertNotEquals(null,
            RLM_CollectionsDashboardController.getDashboardCards(null, null),
            'Dashboard cards return a non-null wrapper (no filter).');
        System.assertNotEquals(null,
            RLM_CollectionsDashboardController.getDashboardCards(acc.Id, 'USD'),
            'Dashboard cards return a non-null wrapper (account filter).');

        System.assertNotEquals(null,
            RLM_CollectionsDashboardController.getWorklist(null, null),
            'Worklist returns a non-null wrapper (no filter).');
        System.assertNotEquals(null,
            RLM_CollectionsDashboardController.getWorklist(acc.Id, 'USD'),
            'Worklist returns a non-null wrapper (account filter).');

        System.assertNotEquals(null,
            RLM_CollectionsDashboardController.getCollectionPlanTasks(acc.Id),
            'Collection plan tasks return a non-null list.');
        System.assertNotEquals(null,
            RLM_CollectionsDashboardController.getMyCollectionPlans(),
            'My collection plans return a non-null list.');
        System.assertNotEquals(null,
            RLM_CollectionsDashboardController.getCollectionsProgress(),
            'Collections progress returns a non-null wrapper.');
        Test.stopTest();
    }
}
