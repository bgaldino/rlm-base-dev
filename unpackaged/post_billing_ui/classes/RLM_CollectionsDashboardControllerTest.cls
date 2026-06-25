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

    // PaymentScheduleItem is Apex-createable (unlike Invoice/BillingScheduleGroup), so the
    // promise-summary aggregation can be exercised with real data. Two Draft items under a Draft
    // schedule drive the SUM(RequestedAmount)/COUNT(Id) GROUP BY Status path and the account filter.
    @isTest
    static void getPaymentPromiseSummary_withSeededItems_aggregatesByStatus() {
        Account acc = new Account(Name = 'RLM Promise Summary Test');
        insert acc;
        PaymentSchedule ps = new PaymentSchedule(Status = 'Draft', TotalRequestedAmount = 150);
        insert ps;
        insert new List<PaymentScheduleItem>{
            new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id,
                RequestedAmount = 100, TargetPaymentProcessingDate = Date.today(), Status = 'Draft'),
            new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id,
                RequestedAmount = 50, TargetPaymentProcessingDate = Date.today(), Status = 'Draft')
        };

        Test.startTest();
        Map<String, RLM_CollectionsDashboardController.PaymentPromiseBucket> unfiltered =
            bucketsByStatus(RLM_CollectionsDashboardController.getPaymentPromiseSummary(null, null));
        Map<String, RLM_CollectionsDashboardController.PaymentPromiseBucket> byAccount =
            bucketsByStatus(RLM_CollectionsDashboardController.getPaymentPromiseSummary(acc.Id, null));
        Test.stopTest();

        // The summary always returns all four buckets in fixed order.
        System.assertEquals(4, unfiltered.size(), 'Failed/Ready/Draft/Processing buckets are always present.');
        System.assertEquals(150, unfiltered.get('Draft').totalRequestedAmount,
            'Two Draft items of 100 + 50 sum to 150.');
        System.assertEquals(2, unfiltered.get('Draft').itemCount, 'Two Draft items counted.');
        System.assertEquals(0, unfiltered.get('Failed').totalRequestedAmount, 'No Failed items seeded.');

        System.assertEquals(150, byAccount.get('Draft').totalRequestedAmount,
            'Account-filtered Draft sum matches (both items belong to the account).');
        System.assertEquals(2, byAccount.get('Draft').itemCount, 'Account-filtered Draft count matches.');
    }

    private static Map<String, RLM_CollectionsDashboardController.PaymentPromiseBucket> bucketsByStatus(
        List<RLM_CollectionsDashboardController.PaymentPromiseBucket> buckets) {
        Map<String, RLM_CollectionsDashboardController.PaymentPromiseBucket> byStatus =
            new Map<String, RLM_CollectionsDashboardController.PaymentPromiseBucket>();
        for (RLM_CollectionsDashboardController.PaymentPromiseBucket b : buckets) {
            byStatus.put(b.status, b);
        }
        return byStatus;
    }
}
