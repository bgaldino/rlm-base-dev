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

    // The all-items branch (null filters) always returns one summary per tracked status with zero
    // totals when there is no data.
    @isTest
    static void getPaymentScheduleItems_noData_returnsZeroedSummaries() {
        Test.startTest();
        List<RLM_PaymentsDataController.PaymentStatusSummary> summaries =
            RLM_PaymentsDataController.getPaymentScheduleItems(null, null);
        Test.stopTest();

        System.assertEquals(5, summaries.size(),
            'Failed/Ready/Applied/Draft/Processing summaries are always returned.');
        for (RLM_PaymentsDataController.PaymentStatusSummary s : summaries) {
            System.assertEquals(0, s.itemCount, 'No data -> zero items for ' + s.status);
            System.assertEquals(0, s.totalRequestedAmount, 'No data -> zero total for ' + s.status);
        }
    }

    // PaymentScheduleItem is Apex-createable, so the per-status summarization can be exercised with
    // real data. Two Draft items for an account drive the account-filtered branch and addItem().
    @isTest
    static void getPaymentScheduleItems_seededDraftItems_summarized() {
        Account acc = new Account(Name = 'RLM PSI Summary Test');
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
        List<RLM_PaymentsDataController.PaymentStatusSummary> summaries =
            RLM_PaymentsDataController.getPaymentScheduleItems(acc.Id, null);
        Test.stopTest();

        RLM_PaymentsDataController.PaymentStatusSummary draft = null;
        for (RLM_PaymentsDataController.PaymentStatusSummary s : summaries) {
            if (s.status == 'Draft') { draft = s; }
        }
        System.assertNotEquals(null, draft, 'A Draft summary should be present.');
        System.assertEquals(2, draft.itemCount, 'Two Draft items were seeded.');
        System.assertEquals(150, draft.totalRequestedAmount, 'Draft requested total is 100 + 50.');
    }

    // PaymentScheduleItem is Apex-createable, so the account-options aggregate (GROUP BY
    // PaymentAccountId) can be exercised with real data: a seeded item's account must appear.
    @isTest
    static void getAccountOptions_withSeededItem_includesAccount() {
        Account acc = new Account(Name = 'RLM Payments Account Option Test');
        insert acc;
        PaymentSchedule ps = new PaymentSchedule(Status = 'Draft', TotalRequestedAmount = 100);
        insert ps;
        insert new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id,
            RequestedAmount = 100, TargetPaymentProcessingDate = Date.today(), Status = 'Draft');

        Test.startTest();
        List<Map<String, String>> options = RLM_PaymentsDataController.getAccountOptions();
        Test.stopTest();

        Boolean found = false;
        for (Map<String, String> option : options) {
            if (option.get('value') == String.valueOf(acc.Id)) {
                found = true;
                System.assertEquals('RLM Payments Account Option Test', option.get('label'),
                    'The account label should match the seeded account name.');
            }
        }
        System.assert(found, 'An account with a PaymentScheduleItem should appear in the options.');
        System.assert(options.size() >= 2, 'Sentinel "All Accounts" plus the seeded account.');
    }
}
