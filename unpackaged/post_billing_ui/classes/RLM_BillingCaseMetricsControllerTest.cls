/**
 * Tests for RLM_BillingCaseMetricsController.
 *
 * Documented, not pinned: the open-billing-cases metric counts Case Type 'Billing', which the
 * CaseType value set this repo ships does not include. Case.Type is unrestricted by default (see
 * billingCaseTypeIsBlocked), so a test (or an API load) can still create such a case, and the
 * tests here do; but on a repo-built org no case created through the UI has that type, so the
 * metric reads zero there.
 */
@isTest
private class RLM_BillingCaseMetricsControllerTest {

    // With no Cases or Disputes, every metric reads zero for the running admin. The dispute
    // reads may be refused and swallowed for the admin, so this does not show the dispute
    // queries ran; getMetrics_asBillingRole_runsTheDisputeQueries does. Dispute and its Status,
    // DisputedAmount and InvoiceId fields are required by this bundle (RLM_BillingUIAccessTest
    // checks them).
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
        assertAmount(0, (Decimal) result.get('totalDisputedAmount'), 'No disputes -> a zero disputed amount.');
    }

    // Positive path for the open-billing-case count. Case.Type is unrestricted by default (see
    // billingCaseTypeIsBlocked), so an open Case of Type 'Billing' can be created even where the
    // value is not listed (see the class header), and it is reflected in the metric.
    @isTest
    static void getMetrics_openBillingCase_isCounted() {
        if (billingCaseTypeIsBlocked()) {
            return;
        }
        insert new Case(Subject = 'RLM Billing Case Metrics Test', Status = 'New', Type = 'Billing');

        Test.startTest();
        Map<String, Object> result = RLM_BillingCaseMetricsController.getMetrics();
        Test.stopTest();

        System.assertEquals(1, (Integer) result.get('openBillingCases'),
            'One open Type=Billing case should be counted.');
    }

    // Dispute is createable, so the dispute aggregates count real open disputes and sum their
    // amounts, read by a Billing Operations user who owns them (see billingUser). SUM is
    // ungrouped, so the total is checked only where that user's currency is the corporate one
    // (the disputes are created in it); the count always is.
    @isTest
    static void getMetrics_countsOpenDisputesAndSumsTheirAmounts() {
        User reader = billingUser();
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
            d.put('OwnerId', reader.Id);
            d.put('AccountId', a.Id);
            d.put('CaseId', disputeCases[i].Id);
            d.put('ReceivedDate', Date.today());
            d.put('DisputedAmount', amounts[i]);
            disputes.add(d);
        }
        insert disputes;

        Map<String, Object> result;
        String readerCurrency;
        Test.startTest();
        System.runAs(reader) {
            result = RLM_BillingCaseMetricsController.getMetrics();
            readerCurrency = UserInfo.getDefaultCurrency();
        }
        Test.stopTest();

        Assert.isNull(RLM_BillingCaseMetricsController.lastDisputeQueryError,
            'Dispute query failed: ' + RLM_BillingCaseMetricsController.lastDisputeQueryError);
        Assert.areEqual(2, (Integer) result.get('openDisputes'), 'Both new disputes are open.');
        if (readerCurrency == corporate) {
            assertAmount(150, (Decimal) result.get('totalDisputedAmount'), 'The open disputes total 100 + 50.');
        } else {
            System.debug(LoggingLevel.WARN, 'SKIPPED: ungrouped currency aggregate depends on the running '
                + 'user\'s currency matching the corporate currency');
        }
    }

    // A user who cannot query Dispute does not see an open dispute: the dispute seeded here is
    // counted for the Billing Operations user who owns it. For this user either describe hides
    // Dispute.Status (so the controller skips the query) or the controller's user-mode query is
    // refused (it records the error); both are access refusals, so the zero does not come from
    // sharing.
    @isTest
    static void getMetrics_userWhoCannotReadDisputes_doesNotCountTheDispute() {
        User noAccess = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        User reader = billingUser();
        Account a = new Account(Name = 'RLM Case Metrics unreadable');
        insert a;
        Case disputeCase = new Case(AccountId = a.Id, Subject = 'RLM Case Metrics unreadable dispute');
        insert disputeCase;
        SObject dispute = Schema.getGlobalDescribe().get('Dispute').newSObject();
        dispute.put('AccountId', a.Id);
        dispute.put('CaseId', disputeCase.Id);
        dispute.put('ReceivedDate', Date.today());
        dispute.put('OwnerId', reader.Id);
        insert dispute;
        System.runAs(reader) {
            Assert.areEqual(1, (Integer) RLM_BillingCaseMetricsController.getMetrics().get('openDisputes'),
                'PRECONDITION: the billing user counts the open dispute.');
        }

        Boolean canQuery = true;
        Boolean statusVisible = false;
        Map<String, Object> result;
        RLM_BillingCaseMetricsController.lastDisputeQueryError = null;
        Test.startTest();
        System.runAs(noAccess) {
            try {
                Database.query('SELECT Id FROM Dispute LIMIT 1', AccessLevel.USER_MODE);
            } catch (Exception e) {
                canQuery = false;
            }
            Schema.SObjectType disputeType = Schema.getGlobalDescribe().get('Dispute');
            statusVisible = disputeType != null
                && disputeType.getDescribe().fields.getMap().containsKey('status');
            result = RLM_BillingCaseMetricsController.getMetrics();
        }
        Test.stopTest();

        Assert.isFalse(canQuery, 'PRECONDITION: the user cannot query Dispute in user mode.');
        Assert.isTrue(RLM_BillingCaseMetricsController.lastDisputeQueryError != null || !statusVisible,
            'The controller\'s dispute query was refused or skipped for lack of access, not run and '
            + 'filtered by sharing.');
        Assert.areEqual(0, (Integer) result.get('openDisputes'), 'The open dispute is not counted.');
    }

    // A user who cannot query Case does not see the admin's open billing case (through access or
    // sharing; the controller records no error for the case count), and gets a zero rather than
    // an error.
    @isTest
    static void getMetrics_userWhoCannotReadCases_doesNotCountABillingCase() {
        if (billingCaseTypeIsBlocked()) {
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
        User u = billingUser();
        // Each field gates part of the dispute logic: one missing from the user's describe skips
        // that part without an error, so all three are checked first. getMap() keys are lowercase.
        Set<String> hidden = new Set<String>{ 'status', 'disputedamount', 'invoiceid' };
        System.runAs(u) {
            hidden.removeAll(Schema.getGlobalDescribe().get('Dispute').getDescribe().fields.getMap().keySet());
            RLM_BillingCaseMetricsController.getMetrics();
        }
        Assert.isTrue(hidden.isEmpty(), 'Premise: the Billing Operations user\'s describe lists Dispute status, '
            + 'disputedamount and invoiceid; missing: ' + hidden);
        Assert.isNull(RLM_BillingCaseMetricsController.lastDisputeQueryError,
            'Dispute query failed: ' + RLM_BillingCaseMetricsController.lastDisputeQueryError);
    }

    // A Billing Operations user holding RLM_BillingUI and the Billing permission set license: the
    // dispute reads in these tests check that role's access, not the running admin's.
    private static User billingUser() {
        return RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
    }

    // True, with a visible skip, only where Case.Type is restricted and lacks 'Billing', so a
    // Billing case cannot be inserted. Case.Type is unrestricted by default.
    private static Boolean billingCaseTypeIsBlocked() {
        Schema.DescribeFieldResult typeField = Case.Type.getDescribe();
        if (!typeField.isRestrictedPicklist()) {
            return false;
        }
        for (Schema.PicklistEntry entry : typeField.getPicklistValues()) {
            if (entry.isActive() && entry.getValue() == 'Billing') {
                return false;
            }
        }
        System.debug(LoggingLevel.WARN, 'SKIPPED: Case.Type is restricted and has no Billing value, so a '
            + 'Billing case cannot be created.');
        return true;
    }

    // Fails on a null amount and names both values in the message; Decimal equality already
    // ignores scale.
    private static void assertAmount(Decimal expected, Decimal actual, String message) {
        Assert.isTrue(actual != null && actual == expected,
            message + ' Expected ' + expected + ', got ' + actual + '.');
    }
}
