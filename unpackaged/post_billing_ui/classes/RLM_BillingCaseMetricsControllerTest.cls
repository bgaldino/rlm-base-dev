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

    // Positive path for the open-billing-case count. Case is an insertable standard object, so an
    // open Case of Type 'Billing' should be reflected in the metric. Guarded to the orgs where
    // 'Billing' is a valid Case.Type picklist value: the CaseType value set this repo ships has
    // no 'Billing', so it runs only where an org adds that value itself.
    @isTest
    static void getMetrics_openBillingCase_isCounted() {
        if (!billingCaseTypeIsValid()) {
            System.debug(LoggingLevel.WARN, 'SKIPPED: this org has no active \'Billing\' Case Type; '
                + 'the repo\'s CaseType value set does not ship one.');
            return;
        }

        insert new Case(Subject = 'RLM Billing Case Metrics Test', Status = 'New', Type = 'Billing');

        Test.startTest();
        Map<String, Object> result = RLM_BillingCaseMetricsController.getMetrics();
        Test.stopTest();

        System.assertEquals(1, (Integer) result.get('openBillingCases'),
            'One open Type=Billing case should be counted.');
    }

    private static Boolean billingCaseTypeIsValid() {
        Schema.DescribeFieldResult typeField =
            Case.SObjectType.getDescribe().fields.getMap().get('Type').getDescribe();
        for (Schema.PicklistEntry entry : typeField.getPicklistValues()) {
            if (entry.isActive() && entry.getValue() == 'Billing') {
                return true;
            }
        }
        return false;
    }

    // Dispute is createable, so the dispute aggregates count real open disputes and sum their
    // amounts. SUM(DisputedAmount) is ungrouped, so the total is checked only where the running
    // user's currency is the corporate one (the disputes are created in it); the count always is.
    @isTest
    static void getMetrics_countsOpenDisputesAndSumsTheirAmounts() {
        String corporate = [SELECT IsoCode FROM CurrencyType WHERE IsCorporate = true LIMIT 1].IsoCode;
        Account a = new Account(Name = 'RLM Case Metrics Disputes');
        insert a;
        List<Decimal> amounts = new List<Decimal>{ 100, 50 };
        // One case per dispute: a dispute is raised from a case.
        List<Case> disputeCases = new List<Case>();
        for (Decimal amount : amounts) {
            disputeCases.add(new Case(AccountId = a.Id, Subject = 'RLM Case Metrics dispute ' + amount));
        }
        insert disputeCases;
        List<SObject> disputes = new List<SObject>();
        for (Integer i = 0; i < amounts.size(); i++) {
            SObject d = Schema.getGlobalDescribe().get('Dispute').newSObject();
            d.put('CurrencyIsoCode', corporate);
            d.put('AccountId', a.Id);
            d.put('CaseId', disputeCases[i].Id);
            d.put('ReceivedDate', Date.today());
            d.put('DisputedAmount', amounts[i]);
            disputes.add(d);
        }
        insert disputes;

        Test.startTest();
        Map<String, Object> result = RLM_BillingCaseMetricsController.getMetrics();
        Test.stopTest();

        Assert.isNull(RLM_BillingCaseMetricsController.lastDisputeQueryError,
            'Dispute query failed: ' + RLM_BillingCaseMetricsController.lastDisputeQueryError);
        Assert.areEqual(2, (Integer) result.get('openDisputes'), 'Both new disputes are open.');
        if (UserInfo.getDefaultCurrency() == corporate) {
            assertAmount(150, (Decimal) result.get('totalDisputedAmount'), 'The open disputes total 100 + 50.');
        } else {
            System.debug(LoggingLevel.WARN, 'SKIPPED: ungrouped currency aggregate depends on the running '
                + 'user\'s currency matching the corporate currency');
        }
    }

    // Compares amounts by value, so 150 and 150.00 match.
    private static void assertAmount(Decimal expected, Decimal actual, String message) {
        Assert.isTrue(actual != null && actual == expected,
            message + ' Expected ' + expected + ', got ' + actual + '.');
    }

    // A user who cannot query Dispute does not see the admin's open dispute: the dispute seeded
    // here is counted for the admin, so the zero this user gets comes from access.
    @isTest
    static void getMetrics_userWhoCannotReadDisputes_doesNotCountTheDispute() {
        User noAccess = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        Account a = new Account(Name = 'RLM Case Metrics unreadable');
        insert a;
        Case disputeCase = new Case(AccountId = a.Id, Subject = 'RLM Case Metrics unreadable dispute');
        insert disputeCase;
        SObject dispute = Schema.getGlobalDescribe().get('Dispute').newSObject();
        dispute.put('AccountId', a.Id);
        dispute.put('CaseId', disputeCase.Id);
        dispute.put('ReceivedDate', Date.today());
        insert dispute;
        Assert.areEqual(1, (Integer) RLM_BillingCaseMetricsController.getMetrics().get('openDisputes'),
            'PRECONDITION: the admin counts the open dispute.');

        Boolean canQuery = true;
        Map<String, Object> result;
        Test.startTest();
        System.runAs(noAccess) {
            try {
                Database.query('SELECT Id FROM Dispute LIMIT 1', AccessLevel.USER_MODE);
            } catch (Exception e) {
                canQuery = false;
            }
            result = RLM_BillingCaseMetricsController.getMetrics();
        }
        Test.stopTest();

        Assert.isFalse(canQuery, 'PRECONDITION: the user cannot query Dispute in user mode.');
        Assert.areEqual(0, (Integer) result.get('openDisputes'), 'The admin\'s open dispute is not counted.');
    }

    // A user who cannot query Case does not see the admin's open billing case, and gets a zero
    // rather than an error. It needs a 'Billing' Case Type, which the CaseType value set this
    // repo ships does not include; without one the test is skipped with a warning.
    @isTest
    static void getMetrics_userWhoCannotReadCases_doesNotCountABillingCase_whenTheBillingTypeExists() {
        if (!billingCaseTypeIsValid()) {
            System.debug(LoggingLevel.WARN, 'SKIPPED: this org has no active \'Billing\' Case Type; '
                + 'the repo\'s CaseType value set does not ship one.');
            return;
        }
        User noAccess = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        Case openCase = new Case(Subject = 'RLM Billing Case Metrics unreadable', Status = 'New', Type = 'Billing');
        insert openCase;
        Assert.areEqual(1, (Integer) RLM_BillingCaseMetricsController.getMetrics().get('openBillingCases'),
            'PRECONDITION: the admin counts the open billing case.');

        Boolean canQuery = true;
        Map<String, Object> result;
        Test.startTest();
        System.runAs(noAccess) {
            try {
                Database.query('SELECT Id FROM Case LIMIT 1', AccessLevel.USER_MODE);
            } catch (Exception e) {
                canQuery = false;
            }
            result = RLM_BillingCaseMetricsController.getMetrics();
        }
        Test.stopTest();

        Assert.isFalse(canQuery, 'PRECONDITION: the user cannot query Case in user mode.');
        Assert.areEqual(0, (Integer) result.get('openBillingCases'), 'The admin\'s open billing case is not counted.');
    }

    // The dispute aggregates swallow their errors and show zero, so the zero-path test passes
    // whether or not they run. As a billing role, which can read Dispute, they must run clean.
    @isTest
    static void getMetrics_asBillingRole_runsTheDisputeQueries() {
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
        // Each field gates part of the dispute logic: one the user can't see skips that part
        // without an error, so all three are checked first.
        // getMap() keys are lowercase.
        Set<String> hidden = new Set<String>{ 'status', 'disputedamount', 'invoiceid' };
        System.runAs(u) {
            hidden.removeAll(Schema.getGlobalDescribe().get('Dispute').getDescribe().fields.getMap().keySet());
            RLM_BillingCaseMetricsController.getMetrics();
        }
        Assert.isTrue(hidden.isEmpty(), 'Premise: Billing Operations can read Dispute fields, but not ' + hidden);
        Assert.isNull(RLM_BillingCaseMetricsController.lastDisputeQueryError,
            'Dispute query failed: ' + RLM_BillingCaseMetricsController.lastDisputeQueryError);
    }
}
