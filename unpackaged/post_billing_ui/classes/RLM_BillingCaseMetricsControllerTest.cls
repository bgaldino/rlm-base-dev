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
        // The amount goes on the dispute when its field is createable; otherwise the dispute
        // totals its items, so it goes on one item.
        Boolean amountOnDispute = Schema.getGlobalDescribe().get('Dispute').getDescribe()
            .fields.getMap().get('DisputedAmount').getDescribe().isCreateable();
        List<SObject> disputes = new List<SObject>();
        for (Integer i = 0; i < amounts.size(); i++) {
            SObject d = Schema.getGlobalDescribe().get('Dispute').newSObject();
            d.put('AccountId', a.Id);
            d.put('CaseId', disputeCases[i].Id);
            d.put('ReceivedDate', Date.today());
            if (amountOnDispute) {
                d.put('DisputedAmount', amounts[i]);
            }
            disputes.add(d);
        }
        insert disputes;
        if (!amountOnDispute) {
            List<SObject> items = new List<SObject>();
            for (Integer i = 0; i < amounts.size(); i++) {
                SObject item = Schema.getGlobalDescribe().get('DisputeItem').newSObject();
                item.put('DisputeId', disputes[i].Id);
                item.put('TransactionDate', Date.today());
                item.put('DisputedAmount', amounts[i]);
                items.add(item);
            }
            insert items;
        }

        Test.startTest();
        Map<String, Object> result = RLM_BillingCaseMetricsController.getMetrics();
        Test.stopTest();

        Assert.isNull(RLM_BillingCaseMetricsController.lastDisputeQueryError,
            'Dispute query failed: ' + RLM_BillingCaseMetricsController.lastDisputeQueryError);
        Assert.areEqual(2, (Integer) result.get('openDisputes'), 'Both new disputes are open.');
        Decimal total = (Decimal) result.get('totalDisputedAmount');
        Assert.isTrue(total == 150, 'The open disputes total 100 + 50. Got ' + total);
        Assert.areEqual(0, (Integer) result.get('disputedInvoices'), 'No dispute names an invoice.');
    }

    // A user who cannot read Case sees zero open billing cases rather than an error, even when
    // one exists. Without Dispute access the dispute metrics stay at zero too.
    @isTest
    static void getMetrics_userWhoCannotReadCases_seesZero() {
        User noAccess = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        Case openCase = new Case(Subject = 'RLM Billing Case Metrics unreadable', Status = 'New');
        if (billingCaseTypeIsValid()) {
            openCase.Type = 'Billing';
        }
        insert openCase;

        Map<String, Object> result;
        Test.startTest();
        System.runAs(noAccess) {
            result = RLM_BillingCaseMetricsController.getMetrics();
        }
        Test.stopTest();

        Assert.areEqual(0, (Integer) result.get('openBillingCases'), 'An unreadable Case counts as none.');
        Assert.areEqual(0, (Integer) result.get('openDisputes'), 'No readable disputes.');
        Assert.areEqual(0, (Integer) result.get('disputedInvoices'), 'No readable disputed invoices.');
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
