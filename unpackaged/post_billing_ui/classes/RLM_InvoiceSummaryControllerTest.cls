@isTest
private class RLM_InvoiceSummaryControllerTest {

    // Checks that, as the admin, the summary for an account with no billing records returns
    // zeros. It does not show the dispute read runs (with no cases it is skipped). The
    // dispute and promise-to-pay tests below, run as billing users after USER_MODE probes, show
    // their reads run; the two role tests show the summary loads for each role.
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

    // A currency with no rate is never converted at 1 (pack 452): the conversion refuses with a
    // fixed sentence, which the dispute, debit memo and promise-to-pay steps turn into unavailable.
    @isTest
    static void convertCurrency_withAMissingRate_refusesWithAFixedSentence() {
        Map<String, Decimal> rates = new Map<String, Decimal>{ 'USD' => 1 };
        String message;
        try {
            RLM_InvoiceSummaryController.convertCurrency(100, 'EUR', 'USD', rates);
        } catch (AuraHandledException e) {
            message = e.getMessage();
        }
        Assert.areEqual(RLM_InvoiceSummaryController.RATE_MISSING, message, 'No EUR rate: refused, not converted at 1.');
    }

    // A dispute step whose amounts are in a currency with no rate leaves the disputes unavailable.
    @isTest
    static void addDisputes_withAMissingRate_leavesThemUnavailable() {
        Account acc = new Account(Name = 'RLM Invoice Summary Dispute No Rate');
        insert acc;
        Case openCase = new Case(AccountId = acc.Id, Subject = 'RLM dispute in a currency with no rate');
        insert openCase;
        newDispute(acc.Id, openCase.Id, 40, UserInfo.getUserId(), UserInfo.getDefaultCurrency());
        RLM_InvoiceSummaryController.InvoiceSummaryData ownCurrency = zeroedSummary();
        RLM_InvoiceSummaryController.InvoiceSummaryData data = zeroedSummary();
        Test.startTest();
        // The same dispute with its own currency as the target needs no rate: it sums.
        RLM_InvoiceSummaryController.addDisputes(ownCurrency, new Set<Id>{ openCase.Id }, true,
            UserInfo.getDefaultCurrency(), new Map<String, Decimal>());
        // Multi-currency, target ZZZ: no rate for either side in an empty map.
        RLM_InvoiceSummaryController.addDisputes(data, new Set<Id>{ openCase.Id }, true, 'ZZZ', new Map<String, Decimal>());
        Test.stopTest();
        Assert.areEqual(40, ownCurrency.disputeAmount, 'PRECONDITION: with its own currency as the target the dispute sums to 40.');
        Assert.isNull(data.disputeAmount, 'The dispute amount is unavailable, not converted at 1.');
        Assert.isNull(data.disputeCount, 'The dispute count is unavailable.');
        Assert.areEqual(0, data.promiseToPayAmount, 'Only the dispute part is unavailable: promises stay as they were.');
        Assert.areEqual(0, data.promiseToPayCount, 'Only the dispute part is unavailable.');
    }

    // A promise to pay in a currency with no rate leaves only the promise-to-pay part unavailable.
    // Runs as a collections user, who can read the plan chain; the admin creates the records.
    @isTest
    static void addPromisesToPay_withAMissingRate_leavesOnlyThemUnavailable() {
        if (!UserInfo.isMultiCurrencyOrganization()) {
            System.debug(LoggingLevel.WARN, 'SKIPPED: single-currency org, no conversion to miss.');
            return;
        }
        User u = collectionsUser();
        String userCurrency = [SELECT DefaultCurrencyIsoCode FROM User WHERE Id = :u.Id].DefaultCurrencyIsoCode;
        Account acc = new Account(Name = 'RLM Invoice Summary Promise No Rate', OwnerId = u.Id);
        insert acc;
        CollectionPlan plan = new CollectionPlan(AccountId = acc.Id, OwnerId = u.Id);
        insert plan;
        CollectionPlanItem planItem = new CollectionPlanItem(CollectionPlanId = plan.Id);
        insert planItem;
        PaymentSchedule promise = new PaymentSchedule(OwnerId = u.Id, Status = 'Draft', TotalRequestedAmount = 75);
        promise.put('CollectionPlanItemId', planItem.Id);
        promise.put('CurrencyIsoCode', userCurrency);
        insert promise;
        PaymentScheduleItem item = new PaymentScheduleItem(PaymentScheduleId = promise.Id, PaymentAccountId = acc.Id,
            RequestedAmount = 75, TargetPaymentProcessingDate = Date.today().addDays(7), Status = 'Draft');
        item.put('CurrencyIsoCode', userCurrency);
        insert item;

        RLM_InvoiceSummaryController.InvoiceSummaryData withRates = zeroedSummary();
        RLM_InvoiceSummaryController.InvoiceSummaryData noRate = zeroedSummary();
        Test.startTest();
        System.runAs(u) {
            RLM_InvoiceSummaryController.addPromisesToPay(withRates, acc.Id, true, userCurrency, new Map<String, Decimal>());
            RLM_InvoiceSummaryController.addPromisesToPay(noRate, acc.Id, true, 'ZZZ', new Map<String, Decimal>());
        }
        Test.stopTest();

        Assert.areEqual(75, withRates.promiseToPayAmount, 'PRECONDITION: in the user\'s own currency the promise sums (no conversion).');
        Assert.isNull(noRate.promiseToPayAmount, 'No rate for the promise\'s currency: unavailable, not 75 at rate 1.');
        Assert.isNull(noRate.promiseToPayCount, 'And its count.');
        Assert.areEqual(0, noRate.disputeAmount, 'Only the promise-to-pay part is unavailable: disputes stay as they were.');
    }

    // An org without the fields the dispute query reads has no disputes: a real zero, not
    // unavailable. Simulated by naming a field this org's Dispute lacks.
    @isTest
    static void addDisputes_withoutTheDisputeFields_countsZeroDisputes() {
        Account acc = new Account(Name = 'RLM Invoice Summary No Dispute Fields');
        insert acc;
        Case openCase = new Case(AccountId = acc.Id, Subject = 'RLM dispute without its fields');
        insert openCase;
        newDispute(acc.Id, openCase.Id, 40, UserInfo.getUserId(), UserInfo.getDefaultCurrency());
        RLM_InvoiceSummaryController.disputeReadFields = new Set<String>{ 'CaseId', 'DisputedAmount', 'RLM_NoSuchField__c' };
        RLM_InvoiceSummaryController.InvoiceSummaryData data = zeroedSummary();
        Test.startTest();
        RLM_InvoiceSummaryController.addDisputes(data, new Set<Id>{ openCase.Id }, UserInfo.isMultiCurrencyOrganization(),
            UserInfo.getDefaultCurrency(), new Map<String, Decimal>());
        Test.stopTest();
        Assert.areEqual(0, data.disputeCount, 'Without the fields there are no disputes: a real zero.');
        Assert.areEqual(0, data.disputeAmount, 'And a real zero amount.');
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
        return RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
    }

    private static User collectionsUser() {
        return RLM_BillingUITestUsers.create(
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

    // A billing role without collections (the managed role on its own, without the standalone
    // RLM_BillingCollectionsRead set) can't read the collection plan link that the promise-to-pay step
    // filters on. The summary must still load for that user, with the
    // promise to pay unavailable (null), not zero: the account may have promises the user cannot
    // see (pack 452), and not failing on that one query.
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
        Assert.isNull(data.promiseToPayCount, 'No collections access -> the promise-to-pay count is unavailable, not zero.');
        Assert.isNull(data.promiseToPayAmount, 'No collections access -> the promise-to-pay amount is unavailable, not zero.');
        Assert.areEqual(0, data.totalDue, 'The rest of the summary still loads.');
    }

    // Each billing persona with the standalone RLM_BillingCollectionsRead set (owner decision, todo
    // 452) reads collection plans, so its promise to pay is a real figure (zero here), not
    // unavailable. Skipped visibly where the personas bundle is not deployed.
    @isTest
    static void getInvoiceSummary_eachBillingPersonaWithTheCollectionsSet_runsPromiseToPay() {
        Map<String, User> personas = new Map<String, User>();
        for (String groupName : RLM_BillingUITestUsers.BILLING_PERSONA_GROUPS) {
            User u = RLM_BillingUITestUsers.billingPersonaWithCollectionsRead(groupName);
            if (u == null) {
                return;
            }
            personas.put(groupName, u);
        }
        Map<String, Id> accountByGroup = new Map<String, Id>();
        for (String groupName : personas.keySet()) {
            Account acc = new Account(Name = 'RLM Invoice Summary ' + groupName, OwnerId = personas.get(groupName).Id);
            insert acc;
            accountByGroup.put(groupName, acc.Id);
        }
        Map<String, Boolean> seesCollections = new Map<String, Boolean>();
        Map<String, String> promiseReadErrors = new Map<String, String>();
        Map<String, RLM_InvoiceSummaryController.InvoiceSummaryData> results = new Map<String, RLM_InvoiceSummaryController.InvoiceSummaryData>();
        Test.startTest();
        for (String groupName : personas.keySet()) {
            System.runAs(personas.get(groupName)) {
                seesCollections.put(groupName, RLM_InvoiceSummaryController.canReadCollectionPlans());
                promiseReadErrors.put(groupName, userModeError('SELECT Id, RequestedAmount, Status, CurrencyIsoCode FROM PaymentScheduleItem '
                    + 'WHERE PaymentSchedule.CollectionPlanItemId != null '
                    + 'AND PaymentSchedule.CollectionPlanItem.CollectionPlan.AccountId != null LIMIT 1'));
                results.put(groupName, RLM_InvoiceSummaryController.getInvoiceSummary(accountByGroup.get(groupName)));
            }
        }
        Test.stopTest();

        for (String groupName : personas.keySet()) {
            Assert.isTrue(seesCollections.get(groupName), groupName + ' persona can read collection plans.');
            Assert.isNull(promiseReadErrors.get(groupName), groupName + ' persona can run the promise-to-pay read: ' + promiseReadErrors.get(groupName));
            Assert.areEqual(0, results.get(groupName).promiseToPayCount, groupName + ': the promise-to-pay count is a real zero, not unavailable.');
            Assert.areEqual(0, results.get(groupName).promiseToPayAmount, groupName + ': the promise-to-pay amount is a real zero, not unavailable.');
        }
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

    // Pack 452: a user who cannot read Dispute gets the dispute amount and count as unavailable
    // (null), not zero, for an open case that has a dispute. Run on the dispute step directly: a
    // user built to read only some billing objects cannot read DebitMemo (measured), which the
    // full summary also needs.
    @isTest
    static void addDisputes_forAUserWhoCannotReadDisputes_leavesThemUnavailable() {
        Account acc = new Account(Name = 'RLM Invoice Summary Unreadable Disputes');
        insert acc;
        Case openCase = new Case(AccountId = acc.Id, Subject = 'RLM dispute the user cannot read');
        insert openCase;
        newDispute(acc.Id, openCase.Id, 40, UserInfo.getUserId(), UserInfo.getDefaultCurrency());
        User u = RLM_BillingUITestUsers.createWithBillingAccess(
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL }, new List<String>(), new List<String>{ 'Case' });

        RLM_InvoiceSummaryController.InvoiceSummaryData data = zeroedSummary();
        Test.startTest();
        System.runAs(u) {
            Assert.isNotNull(userModeError('SELECT Id, DisputedAmount, CurrencyIsoCode FROM Dispute WHERE CaseId != null LIMIT 1'),
                'PRECONDITION: the user cannot read Dispute.');
            RLM_InvoiceSummaryController.addDisputes(data, new Set<Id>{ openCase.Id }, UserInfo.isMultiCurrencyOrganization(),
                UserInfo.getDefaultCurrency(), new Map<String, Decimal>());
        }
        Test.stopTest();

        Assert.isNull(data.disputeAmount, 'The dispute amount is unavailable (null), not zero.');
        Assert.isNull(data.disputeCount, 'The dispute count is unavailable (null), not zero.');
    }

    // The readable path of the same step, as the admin: the dispute on the open case is summed.
    @isTest
    static void addDisputes_forAUserWhoCanReadDisputes_sumsThem() {
        Account acc = new Account(Name = 'RLM Invoice Summary Readable Disputes');
        insert acc;
        Case openCase = new Case(AccountId = acc.Id, Subject = 'RLM dispute the admin can read');
        insert openCase;
        String userCurrency = UserInfo.getDefaultCurrency();
        newDispute(acc.Id, openCase.Id, 40, UserInfo.getUserId(), userCurrency);

        RLM_InvoiceSummaryController.InvoiceSummaryData data = zeroedSummary();
        Test.startTest();
        RLM_InvoiceSummaryController.addDisputes(data, new Set<Id>{ openCase.Id }, UserInfo.isMultiCurrencyOrganization(),
            userCurrency, new Map<String, Decimal>());
        Test.stopTest();

        Assert.areEqual(1, data.disputeCount, 'The dispute is counted.');
        Assert.areEqual(40, data.disputeAmount, 'The disputed amount is summed.');
    }

    // A user who can read collection plans (so the gate opens) but not the payment schedule items
    // the query reads: the promise to pay is unavailable (null), not zero, and the summary step
    // does not throw.
    @isTest
    static void addPromisesToPay_whenTheScheduleItemReadIsRefused_leavesThemUnavailable() {
        Account acc = new Account(Name = 'RLM Invoice Summary Unreadable Promises');
        insert acc;
        User u = collectionPlanReaderWithoutScheduleItems();

        RLM_InvoiceSummaryController.InvoiceSummaryData data = zeroedSummary();
        Test.startTest();
        System.runAs(u) {
            Assert.isTrue(RLM_InvoiceSummaryController.canReadCollectionPlans(),
                'PRECONDITION: the user can read collection plans, so the promise-to-pay query runs.');
            Assert.isNotNull(userModeError('SELECT Id, RequestedAmount, Status FROM PaymentScheduleItem LIMIT 1'),
                'PRECONDITION: the user cannot read PaymentScheduleItem.');
            RLM_InvoiceSummaryController.addPromisesToPay(data, acc.Id, UserInfo.isMultiCurrencyOrganization(),
                UserInfo.getDefaultCurrency(), new Map<String, Decimal>());
        }
        Test.stopTest();

        Assert.isNull(data.promiseToPayAmount, 'The promise-to-pay amount is unavailable (null), not zero.');
        Assert.isNull(data.promiseToPayCount, 'The promise-to-pay count is unavailable (null), not zero.');
    }

    // A user who reads collection plans and their items but not payment schedule items. Measured
    // on a 264 org (2026-11-26): CollectionPlan is readable only with the Collections and Recovery
    // Specialist user permission, which the user license allows only with the Billing Advanced
    // permission set license; object read grants alone leave it "not supported".
    private static User collectionPlanReaderWithoutScheduleItems() {
        User u = RLM_BillingUITestUsers.create(new List<String>(),
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL, RLM_BillingUITestUsers.BILLING_ADVANCED_PSL });
        String stamp = String.valueOf(Crypto.getRandomInteger()).remove('-');
        System.runAs(new User(Id = UserInfo.getUserId())) {
            PermissionSet ps = new PermissionSet(Name = 'RLM_TestCollectionPlans_' + stamp, Label = 'RLM Test Collection Plans ' + stamp,
                PermissionsRlmBillingAccess = true);
            ps.put('PermissionsCollectionsAndRecoverySpecialist', true);
            insert ps;
            List<ObjectPermissions> grants = new List<ObjectPermissions>();
            for (String objectName : new List<String>{ 'CollectionPlan', 'CollectionPlanItem' }) {
                grants.add(new ObjectPermissions(ParentId = ps.Id, SobjectType = objectName,
                    PermissionsRead = true, PermissionsViewAllRecords = true));
            }
            insert grants;
            insert new PermissionSetAssignment(AssigneeId = u.Id, PermissionSetId = ps.Id);
        }
        return u;
    }

    // A billing user who reads the account's invoices and cases but not debit memos: the card loads,
    // with the debit memo amount, its count and the total due unavailable (null), not zero and not
    // a failed card (pack 452). Measured: a user built this way cannot read DebitMemo at all, which
    // is the refusal this test needs.
    @isTest
    static void getInvoiceSummary_forAUserWhoCannotReadDebitMemos_leavesThemAndTheTotalDueUnavailable() {
        User u = RLM_BillingUITestUsers.createWithBillingAccess(
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL }, new List<String>(),
            new List<String>{ 'Account', 'Invoice', 'Case' }, new List<String>{ 'Case.AccountId' });
        Account acc = new Account(Name = 'RLM Invoice Summary Unreadable Debit Memos', OwnerId = u.Id);
        insert acc;
        RLM_InvoiceSummaryController.InvoiceSummaryData data;
        Test.startTest();
        System.runAs(u) {
            Assert.isNull(userModeError('SELECT Id, Balance, DueDate, Status, SettlementStatus, CurrencyIsoCode FROM Invoice LIMIT 1'),
                'PRECONDITION: the user can read Invoice.');
            Assert.isNotNull(userModeError('SELECT Id, TotalAmount, CurrencyIsoCode FROM DebitMemo LIMIT 1'),
                'PRECONDITION: the user cannot read DebitMemo.');
            data = RLM_InvoiceSummaryController.getInvoiceSummary(acc.Id);
        }
        Test.stopTest();

        Assert.isNull(data.debitAmount, 'The debit memo amount is unavailable (null), not zero.');
        Assert.isNull(data.debitCount, 'The debit memo count is unavailable (null), not zero.');
        Assert.isNull(data.totalDue, 'The total due includes debit memos, so it is unavailable.');
        Assert.areEqual(0, data.totalInvoices, 'The invoice reads still run.');
    }

    // The live failure (pack 452): a billing user who reads only Account and Invoice saw the card
    // replaced by the raw text "Variable does not exist: tmpVar1", raised by the inline Case read
    // (measured as this user on a 264 org). The card now loads with the parts it cannot read
    // unavailable: disputes (no Case read), debit memos and promises to pay.
    @isTest
    static void getInvoiceSummary_forAUserWhoCannotReadCases_loadsWithDisputesUnavailable() {
        User u = RLM_BillingUITestUsers.createWithBillingAccess(
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL }, new List<String>(), new List<String>{ 'Account', 'Invoice' });
        Account acc = new Account(Name = 'RLM Invoice Summary No Case Read', OwnerId = u.Id);
        insert acc;
        insert new Case(AccountId = acc.Id, Subject = 'RLM open case the user cannot read');
        RLM_InvoiceSummaryController.InvoiceSummaryData data;
        String failure;
        Test.startTest();
        System.runAs(u) {
            Assert.isNotNull(userModeError('SELECT Id FROM Case LIMIT 1'), 'PRECONDITION: the user cannot read Case.');
            Assert.isNull(userModeError('SELECT Id, Balance FROM Invoice LIMIT 1'), 'PRECONDITION: the user can read Invoice.');
            Assert.isNull(RLM_InvoiceSummaryController.openCaseIds(acc.Id), 'Case refused: null, not a system-mode read.');
            try {
                data = RLM_InvoiceSummaryController.getInvoiceSummary(acc.Id);
            } catch (Exception e) {
                failure = e.getTypeName() + ': ' + e.getMessage();
            }
        }
        Test.stopTest();

        Assert.isNull(failure, 'The card loads instead of failing: ' + failure);
        Assert.isNull(data.disputeAmount, 'Without Case read the disputes are unavailable (null), not zero.');
        Assert.isNull(data.disputeCount, 'And their count.');
        Assert.isNull(data.debitAmount, 'Debit memos (not readable) are unavailable.');
        Assert.isNull(data.promiseToPayAmount, 'Promises to pay (no collection plan read) are unavailable.');
        Assert.areEqual(0, data.totalInvoices, 'The invoice reads ran.');
        Assert.areEqual(0, data.paidCount, 'The paid-invoice read ran: a real zero.');
    }

    // A user who cannot read Invoice gets the fixed sentence the on-account summary uses, not the
    // platform's query error.
    @isTest
    static void getInvoiceSummary_forAUserWhoCannotReadInvoices_throwsAFixedSentence() {
        User u = RLM_BillingUITestUsers.createWithBillingAccess(
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL }, new List<String>(), new List<String>{ 'Account' });
        Account acc = new Account(Name = 'RLM Invoice Summary No Invoice Read', OwnerId = u.Id);
        insert acc;
        String message;
        Test.startTest();
        System.runAs(u) {
            Assert.isNotNull(userModeError('SELECT Id, Balance FROM Invoice LIMIT 1'), 'PRECONDITION: the user cannot read Invoice.');
            try {
                RLM_InvoiceSummaryController.getInvoiceSummary(acc.Id);
            } catch (AuraHandledException e) {
                message = e.getMessage();
            }
        }
        Test.stopTest();
        Assert.areEqual(RLM_InvoiceSummaryController.INVOICES_UNREADABLE, message,
            'The user-facing sentence is fixed; no platform text is echoed.');
    }

    // openCaseIds reads in user mode: a user who can read Case and see the case (View All) but not
    // Case.AccountId, the field it filters on, is refused (null). A system-mode read would ignore
    // that field refusal and return the case, so this pins the access level.
    @isTest
    static void openCaseIds_forAUserWhoCannotReadCaseAccountId_isNull() {
        User u = RLM_BillingUITestUsers.createWithBillingAccess(
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL }, new List<String>(), new List<String>{ 'Case' });
        Account acc = new Account(Name = 'RLM Invoice Summary No Case Account Field');
        insert acc;
        Case openCase = new Case(AccountId = acc.Id, Subject = 'RLM open case, account field unreadable');
        insert openCase;
        Id caseId = openCase.Id;
        Set<Id> caseIds;
        Test.startTest();
        System.runAs(u) {
            Assert.isNull(userModeError('SELECT Id FROM Case LIMIT 1'), 'PRECONDITION: the user can read Case.');
            Assert.areEqual(1, Database.countQuery('SELECT COUNT() FROM Case WHERE Id = :caseId', AccessLevel.USER_MODE),
                'PRECONDITION: the user can see the case (View All).');
            Assert.isNotNull(userModeError('SELECT Id FROM Case WHERE AccountId != null LIMIT 1'),
                'PRECONDITION: the user cannot read Case.AccountId.');
            caseIds = RLM_InvoiceSummaryController.openCaseIds(acc.Id);
        }
        Test.stopTest();
        Assert.isNull(caseIds, 'Case.AccountId refused: null (unavailable), not the case found by a system-mode read.');
    }

    // A failed paid-invoice read leaves the paid amount and count unavailable (null), not zero, and
    // the rest of the card still loads. Simulated by naming a field Invoice lacks.
    @isTest
    static void getInvoiceSummary_whenThePaidInvoiceReadFails_leavesPaidUnavailable() {
        Account acc = new Account(Name = 'RLM Invoice Summary Paid Read Fails');
        insert acc;
        RLM_InvoiceSummaryController.paidReadFields = 'Id, NetPaymentsApplied, RLM_NoSuchField__c';
        Test.startTest();
        RLM_InvoiceSummaryController.InvoiceSummaryData data = RLM_InvoiceSummaryController.getInvoiceSummary(acc.Id);
        Test.stopTest();
        Assert.isNull(data.paidAmount, 'The paid amount is unavailable (null), not zero.');
        Assert.isNull(data.paidCount, 'The paid count is unavailable (null), not zero.');
        Assert.areEqual(0, data.totalInvoices, 'The open invoices are still read.');
    }

    private static RLM_InvoiceSummaryController.InvoiceSummaryData zeroedSummary() {
        RLM_InvoiceSummaryController.InvoiceSummaryData data = new RLM_InvoiceSummaryController.InvoiceSummaryData();
        data.disputeAmount = 0;
        data.disputeCount = 0;
        data.promiseToPayAmount = 0;
        data.promiseToPayCount = 0;
        return data;
    }
}
