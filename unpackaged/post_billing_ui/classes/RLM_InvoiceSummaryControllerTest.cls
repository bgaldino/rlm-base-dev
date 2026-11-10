@isTest
private class RLM_InvoiceSummaryControllerTest {

    // Checks that, as the admin, the summary for an account with no billing records returns
    // zeros. It does not prove the reads run (with no cases the dispute query is skipped);
    // the role tests below, run as billing users, do.
    @isTest
    static void getInvoiceSummary_accountWithNoBilling_returnsZeroedSummary() {
        Account acc = new Account(Name = 'RLM Invoice Summary Test');
        insert acc;

        Test.startTest();
        RLM_InvoiceSummaryController.InvoiceSummaryData data =
            RLM_InvoiceSummaryController.getInvoiceSummary(acc.Id);
        Test.stopTest();

        System.assertNotEquals(null, data, 'A summary should always be returned.');
        System.assertEquals(0, data.totalDue, 'No invoices -> zero total due.');
        System.assertEquals(0, data.totalInvoices, 'No invoices -> zero invoice count.');
        System.assertEquals(0, data.openInvoices, 'No invoices -> zero open invoices.');
        System.assertEquals(0, data.overdueAmount, 'No invoices -> zero overdue amount.');
        System.assertEquals(0, data.overdueCount, 'No invoices -> zero overdue count.');
        System.assertEquals(0, data.disputeAmount, 'No disputes -> zero dispute amount.');
        System.assertEquals(0, data.disputeCount, 'No disputes -> zero dispute count.');
        System.assertEquals(0, data.debitAmount, 'No debit memos -> zero debit amount.');
        System.assertEquals(0, data.promiseToPayCount, 'No PSIs -> zero promise-to-pay count.');
        System.assertEquals(0, data.paidCount, 'No settled invoices -> zero paid count.');
        System.assertEquals(Date.today(), data.periodEnd,
            'With no invoices the period end defaults to today.');
    }

    // Exercises the classification seam with synthetic invoices: current vs overdue bucketing,
    // null-due-date handling (treated as current), totals, and period-window derivation.
    @isTest
    static void classifyInvoices_bucketsCurrentOverdueAndPeriod() {
        Date today = Date.today();
        List<SObject> invoices = new List<SObject>{
            synthInvoice(100, today.addDays(-10)), // overdue
            synthInvoice(50, today.addDays(10)),   // current
            synthInvoice(25, null)                 // no due date -> current bucket
        };

        RLM_InvoiceSummaryController.InvoiceSummaryData data =
            new RLM_InvoiceSummaryController.InvoiceSummaryData();
        data.totalDue = 0; data.openInvoices = 0;
        data.overdueAmount = 0; data.overdueCount = 0;
        data.currentAmount = 0; data.currentCount = 0;

        Test.startTest();
        RLM_InvoiceSummaryController.classifyInvoices(
            invoices, data, today, false, 'USD', new Map<String, Decimal>());
        Test.stopTest();

        System.assertEquals(175, data.totalDue, 'Sum of all balances.');
        System.assertEquals(3, data.openInvoices, 'All three are open.');
        System.assertEquals(3, data.totalInvoices, 'Total invoice count.');
        System.assertEquals(100, data.overdueAmount, 'Only the past-due invoice is overdue.');
        System.assertEquals(1, data.overdueCount, 'One overdue invoice.');
        System.assertEquals(75, data.currentAmount, 'Future-due + no-due-date are current.');
        System.assertEquals(2, data.currentCount, 'Two current invoices.');
        System.assertEquals(today.addDays(-10), data.periodStart, 'Earliest due date.');
        System.assertEquals(today.addDays(10), data.periodEnd, 'Latest due date.');
    }

    // In a multi-currency org each balance is converted into the target currency before it is
    // bucketed and totalled.
    @isTest
    static void classifyInvoices_multiCurrency_convertsEachBalanceBeforeBucketing() {
        Date today = Date.today();
        List<SObject> invoices = new List<SObject>{
            synthInvoice(100, today.addDays(-5), 'EUR'), // overdue: 100 EUR @0.5 -> 200 USD
            synthInvoice(30, today.addDays(5), 'USD')    // current: already USD
        };

        RLM_InvoiceSummaryController.InvoiceSummaryData data =
            new RLM_InvoiceSummaryController.InvoiceSummaryData();
        data.totalDue = 0; data.openInvoices = 0;
        data.overdueAmount = 0; data.overdueCount = 0;
        data.currentAmount = 0; data.currentCount = 0;

        Test.startTest();
        RLM_InvoiceSummaryController.classifyInvoices(
            invoices, data, today, true, 'USD', new Map<String, Decimal>{ 'USD' => 1, 'EUR' => 0.5 });
        Test.stopTest();

        Assert.areEqual(230, data.totalDue, '200 USD converted from EUR plus 30 USD.');
        Assert.areEqual(200, data.overdueAmount, 'The overdue EUR invoice is converted before bucketing.');
        Assert.areEqual(1, data.overdueCount, 'One overdue invoice.');
        Assert.areEqual(30, data.currentAmount, 'The USD invoice is current and unconverted.');
        Assert.areEqual(1, data.currentCount, 'One current invoice.');
        Assert.areEqual(2, data.totalInvoices, 'Both invoices are counted.');
    }

    @isTest
    static void convertCurrency_coversIdentityAndCrossRate() {
        Map<String, Decimal> rates = new Map<String, Decimal>{ 'USD' => 1, 'EUR' => 0.5 };
        System.assertEquals(100,
            RLM_InvoiceSummaryController.convertCurrency(100, 'USD', 'USD', rates),
            'Same currency is a no-op.');
        System.assertEquals(0,
            RLM_InvoiceSummaryController.convertCurrency(0, 'EUR', 'USD', rates),
            'Zero amount short-circuits.');
        System.assertEquals(200,
            RLM_InvoiceSummaryController.convertCurrency(100, 'EUR', 'USD', rates),
            '100 EUR @0.5 -> 200 USD @1.0.');
    }

    // Disputes are counted through the account's open cases. Dispute is Apex-createable with
    // an account, a case and a received date. A dispute with an amount on an open case counts
    // toward the disputed total; one without an amount is skipped, not counted as zero; and
    // one on a closed case is not counted at all.
    // It runs as a billing operations user, not the deploying admin: RLM_BillingUI, which grants
    // the dispute fields, is assigned only after this bundle deploys. The read-only user cannot
    // create records, so the admin creates them owned by that user (account, cases and
    // disputes), so they are visible to it whatever the org's sharing defaults, in the user's
    // currency.
    @isTest
    static void getInvoiceSummary_disputesOnOpenCases_areSummed() {
        User u = billingOperationsUser();
        if (u == null) {
            return; // no free Billing seat (logged)
        }
        String userCurrency = [SELECT DefaultCurrencyIsoCode FROM User WHERE Id = :u.Id].DefaultCurrencyIsoCode;
        Account acc = new Account(Name = 'RLM Invoice Summary Dispute Test', OwnerId = u.Id);
        insert acc;
        Case amountCase = new Case(AccountId = acc.Id, OwnerId = u.Id, Subject = 'RLM disputed amount case');
        Case emptyCase = new Case(AccountId = acc.Id, OwnerId = u.Id, Subject = 'RLM dispute without an amount');
        Case closedCase = new Case(AccountId = acc.Id, OwnerId = u.Id, Subject = 'RLM closed dispute case', Status = 'Closed');
        insert new List<Case>{ amountCase, emptyCase, closedCase };
        Assert.isTrue([SELECT IsClosed FROM Case WHERE Id = :closedCase.Id].IsClosed,
            'PRECONDITION: the closed case is closed.');

        Id withAmountId = newDispute(acc.Id, amountCase.Id, 40, u.Id, userCurrency).Id;
        newDispute(acc.Id, emptyCase.Id, null, u.Id, userCurrency);
        newDispute(acc.Id, closedCase.Id, 25, u.Id, userCurrency);
        Decimal disputed = [SELECT DisputedAmount FROM Dispute WHERE Id = :withAmountId].DisputedAmount;
        Assert.areEqual(40, disputed, 'PRECONDITION: the dispute must carry its disputed amount.');

        RLM_InvoiceSummaryController.InvoiceSummaryData data;
        Test.startTest();
        System.runAs(u) {
            for (String soql : new List<String>{
                'SELECT Id FROM Case WHERE AccountId != null AND IsClosed = false LIMIT 1',
                'SELECT Id, DisputedAmount, InvoiceId, CurrencyIsoCode FROM Dispute WHERE CaseId != null LIMIT 1'
            }) {
                String readError = userModeError(soql);
                Assert.isNull(readError, 'PRECONDITION: a billing operations user can run "' + soql + '": ' + readError);
            }
            data = RLM_InvoiceSummaryController.getInvoiceSummary(acc.Id);
        }
        Test.stopTest();

        Assert.areEqual(1, data.disputeCount,
            'Only the dispute with an amount on an open case is counted.');
        Assert.areEqual(40, data.disputeAmount,
            'The disputed amount on the open case is summed; the closed case\'s 25 is not.');
        Assert.areEqual(0, data.totalDue, 'Disputes do not add to the amount due.');
    }

    // Promise to pay: a draft payment schedule item under a collection plan item of the
    // account's collection plan counts, at its requested amount.
    // PaymentSchedule.CollectionPlanItemId is not named in this bundle's metadata, and the
    // controller only reads it by name behind a field check, so it is set by name here, after
    // a precondition that the field exists. Besides it, the payment schedule sets its required
    // Status and TotalRequestedAmount, plus OwnerId and CurrencyIsoCode. The schedule and its
    // item use the user's default currency, so the controller's conversion is an identity.
    // It runs as a collections user, not the deploying admin (RLM_BillingUI is assigned after
    // this bundle deploys). The admin creates the account, collection plan and payment schedule
    // owned by that user; the payment schedule item has no owner to set, so its visibility to
    // that user is checked.
    @isTest
    static void getInvoiceSummary_promiseToPayItem_isSummed() {
        User u = collectionsUser();
        if (u == null) {
            return; // no free Billing seat (logged)
        }
        String userCurrency = [SELECT DefaultCurrencyIsoCode FROM User WHERE Id = :u.Id].DefaultCurrencyIsoCode;
        Account acc = new Account(Name = 'RLM Invoice Summary Promise Test', OwnerId = u.Id);
        insert acc;
        // No CollectionPlanReason: with one, RLM_Create_Case_for_Collection raises a case
        // from org data a unit test cannot see. No UsageType either: a Billing plan's items
        // must each link an invoice, and invoices cannot be created in a test. The
        // promise-to-pay query follows the plan chain whatever the plan's usage type.
        CollectionPlan plan = new CollectionPlan(AccountId = acc.Id, OwnerId = u.Id);
        insert plan;
        CollectionPlanItem planItem = new CollectionPlanItem(CollectionPlanId = plan.Id);
        insert planItem;
        PaymentSchedule promise = new PaymentSchedule(
            OwnerId = u.Id,
            Status = 'Draft',
            TotalRequestedAmount = 75
        );
        // A hard failure is intended: the bundle requires CollectionPlanItem, and this field
        // comes with it.
        Assert.isTrue(Schema.SObjectType.PaymentSchedule.fields.getMap().containsKey('CollectionPlanItemId'),
            'PRECONDITION: PaymentSchedule.CollectionPlanItemId exists (collections provides it).');
        promise.put('CollectionPlanItemId', planItem.Id);
        promise.put('CurrencyIsoCode', userCurrency);
        insert promise;
        PaymentScheduleItem item = new PaymentScheduleItem(
            PaymentScheduleId = promise.Id,
            PaymentAccountId = acc.Id,
            RequestedAmount = 75,
            TargetPaymentProcessingDate = Date.today().addDays(7),
            Status = 'Draft'
        );
        item.put('CurrencyIsoCode', userCurrency);
        insert item;

        RLM_InvoiceSummaryController.InvoiceSummaryData data;
        Test.startTest();
        System.runAs(u) {
            Assert.isTrue(RLM_InvoiceSummaryController.canReadCollectionPlans(),
                'PRECONDITION: a collections user can read collection plans and PaymentSchedule.CollectionPlanItemId '
                + 'exists, so the promise-to-pay query runs.');
            String soql = 'SELECT Id, RequestedAmount, Status, CurrencyIsoCode FROM PaymentScheduleItem '
                + 'WHERE PaymentSchedule.CollectionPlanItemId != null '
                + 'AND PaymentSchedule.CollectionPlanItem.CollectionPlan.AccountId != null LIMIT 1';
            String readError = userModeError(soql);
            Assert.isNull(readError, 'PRECONDITION: a collections user can run the promise-to-pay query: ' + readError);
            Assert.areEqual(1, [SELECT COUNT() FROM PaymentScheduleItem WHERE Id = :item.Id WITH USER_MODE],
                'PRECONDITION: the collections user can see the payment schedule item.');
            data = RLM_InvoiceSummaryController.getInvoiceSummary(acc.Id);
        }
        Test.stopTest();

        Assert.areEqual(1, data.promiseToPayCount, 'The draft promise-to-pay item is counted.');
        Assert.areEqual(75, data.promiseToPayAmount, 'The promise to pay is the item\'s requested amount.');
    }

    private static Integer seq = 0;

    private static Id mintInvoiceId() {
        seq++;
        String suffix = String.valueOf(seq);
        while (suffix.length() < 12) {
            suffix = '0' + suffix;
        }
        return Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + suffix);
    }

    // Invoice fields aren't writeable on a constructed sObject; build via JSON to set
    // Balance and DueDate for the classification logic.
    private static SObject synthInvoice(Decimal balance, Date dueDate) {
        return synthInvoice(balance, dueDate, null);
    }

    private static SObject synthInvoice(Decimal balance, Date dueDate, String currencyCode) {
        Map<String, Object> m = new Map<String, Object>{
            'attributes' => new Map<String, Object>{ 'type' => 'Invoice' },
            'Id'         => mintInvoiceId(),
            'Balance'    => balance
        };
        if (dueDate != null) {
            m.put('DueDate', dueDate);
        }
        if (currencyCode != null) {
            m.put('CurrencyIsoCode', currencyCode);
        }
        return (SObject) JSON.deserialize(JSON.serialize(m), Invoice.class);
    }

    // A dispute on a case; amount may be null, for a dispute with no disputed amount.
    // Dispute.CaseId and DisputedAmount are named in RLM_BillingUI, so this bundle cannot deploy without them.
    private static Dispute newDispute(Id accountId, Id caseId, Decimal amount, Id ownerId, String currencyCode) {
        Dispute d = new Dispute(
            AccountId = accountId,
            CaseId = caseId,
            OwnerId = ownerId,
            ReceivedDate = Date.today(),
            DisputedAmount = amount
        );
        d.put('CurrencyIsoCode', currencyCode);
        insert d;
        return d;
    }

    private static User billingOperationsUser() {
        return billingUserOrNull(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
    }

    // Creates a billing test user, or returns null after a visible skip message when no
    // Billing licence seat is free; callers return early on null. Defensive: a test-context
    // probe assigned more Billing seats than the org had free without any error.
    private static User billingUserOrNull(List<String> permissionSets, List<String> licenses) {
        try {
            return RLM_BillingUITestUsers.create(permissionSets, licenses);
        } catch (DmlException e) {
            if (e.getDmlType(0) == StatusCode.LICENSE_LIMIT_EXCEEDED) {
                System.debug(LoggingLevel.WARN, 'SKIPPED: no free Billing licence seat');
                return null;
            }
            throw e;
        }
    }

    private static User collectionsUser() {
        return billingUserOrNull(
            new List<String>{
                'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations', 'BillingCollectionsAndRecoverySpecialist'
            },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL, RLM_BillingUITestUsers.BILLING_ADVANCED_PSL });
    }

    // Returns the error a USER_MODE query raises for the running user, or null if it runs.
    private static String userModeError(String soql) {
        try {
            Database.query(soql, AccessLevel.USER_MODE);
            return null;
        } catch (QueryException e) {
            return e.getMessage();
        }
    }

    // A billing role without collections can't read the collection plan link that the
    // promise-to-pay step filters on. The summary must still load for that user, showing
    // no promise to pay, rather than failing on that one query.
    @isTest
    static void getInvoiceSummary_billingRoleWithoutCollections_loads() {
        Account acc = new Account(Name = 'RLM Invoice Summary Role Test');
        insert acc;
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });

        RLM_InvoiceSummaryController.InvoiceSummaryData data;
        Boolean seesCollections;
        System.runAs(u) {
            seesCollections = RLM_InvoiceSummaryController.canReadCollectionPlans();
            data = RLM_InvoiceSummaryController.getInvoiceSummary(acc.Id);
        }
        Assert.isFalse(seesCollections, 'Premise: Billing Operations alone cannot read collection plans.');
        Assert.areEqual(0, data.promiseToPayCount, 'No collections access -> no promise to pay.');
    }

    // The other side of the gate: a collections user still gets the promise-to-pay query.
    @isTest
    static void getInvoiceSummary_collectionsUser_runsPromiseToPay() {
        Account acc = new Account(Name = 'RLM Invoice Summary Collections Test');
        insert acc;
        User u = RLM_BillingUITestUsers.create(
            new List<String>{
                'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations', 'BillingCollectionsAndRecoverySpecialist'
            },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL, RLM_BillingUITestUsers.BILLING_ADVANCED_PSL });

        Boolean seesCollections;
        RLM_InvoiceSummaryController.InvoiceSummaryData data;
        System.runAs(u) {
            seesCollections = RLM_InvoiceSummaryController.canReadCollectionPlans();
            // With the gate open the promise-to-pay query runs; it must be valid for this user.
            data = RLM_InvoiceSummaryController.getInvoiceSummary(acc.Id);
        }
        Assert.isTrue(seesCollections, 'A collections user can read collection plans.');
        Assert.areEqual(0, data.promiseToPayCount, 'No payment schedules -> no promise to pay.');
    }
}
