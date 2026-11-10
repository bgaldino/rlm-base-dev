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
    // 'Billing' is a valid Case.Type picklist value (added by the billing feature set).
    @isTest
    static void getMetrics_openBillingCase_isCounted() {
        if (!billingCaseTypeIsValid()) {
            return; // 'Billing' Type not available in this org; covered by the zero-path test.
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
    // amounts. No dispute can name an invoice (Invoice is not createable), so none is counted.
    @isTest
    static void getMetrics_countsOpenDisputesAndSumsTheirAmounts() {
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
        Decimal total = (Decimal) result.get('totalDisputedAmount');
        Assert.isTrue(total == 150, 'The open disputes total 100 + 50. Got ' + total);
    }

    // A user who cannot query Case or Dispute gets metrics instead of an error. The open
    // dispute seeded here is counted for the admin, so the zero this user gets comes from
    // access. The case count is checked only as returned without an error: the repo's Case
    // Type values do not include 'Billing', so no case this test could seed would be counted.
    @isTest
    static void getMetrics_userWhoCannotReadCasesOrDisputes_doesNotCountTheDispute() {
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

        List<String> readable = new List<String>();
        Map<String, Object> result;
        Test.startTest();
        System.runAs(noAccess) {
            for (String objectName : new List<String>{ 'Case', 'Dispute' }) {
                try {
                    Database.query('SELECT Id FROM ' + objectName + ' LIMIT 1', AccessLevel.USER_MODE);
                    readable.add(objectName);
                } catch (Exception e) {
                    // Expected: the user may not query it.
                }
            }
            result = RLM_BillingCaseMetricsController.getMetrics();
        }
        Test.stopTest();

        Assert.isTrue(readable.isEmpty(), 'PRECONDITION: the user cannot query ' + readable + ' in user mode.');
        Assert.isNotNull(result.get('openBillingCases'), 'An unreadable Case still returns a count, not an error.');
        Assert.areEqual(0, (Integer) result.get('openDisputes'), 'The admin\'s open dispute is not counted.');
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
