/**
 * Tests for RLM_CollectionsDashboardController.
 *
 * Invoice is createable=false, so no unit test can insert an invoice. The code that works on
 * queried invoices (the card tally, critical follow-ups and high-value delinquents) takes rows, and the tests pass invoices built with JSON.deserialize.
 * The invoice queries themselves, the critical follow-ups' collection-plan lookup and the
 * disputed-accounts invoice rollup can only be verified live. What a test can build -- payments, payment schedule items,
 * collection plans, tasks, cases and debit memos -- is built here, and the cards, worklist,
 * plans, progress and tasks are asserted against it where a test can tell the result apart.
 * Records are created in admin context. Other tests run as other users: a collections specialist,
 * who reads their own plan; a user with no access, for whom every section is unavailable as refused;
 * and the same kind of no-access user, for whom getAccountOptions returns only the sentinel and the
 * worklist builders keep their rows without account names. The specialist holds the Billing and
 * Billing Advanced permission set licenses; the no-access users hold none. getMyCollectionPlans
 * keeping plans with a dash for the name when Account is refused needs a user who owns a plan but
 * cannot read Account, so it is verified live only.
 *
 * Documented, not pinned: the unapplied-credits card filters Payment.Type on 'Credit' and
 * 'Credit Memo', which are not Payment.Type values (Sale and Capture), so it is
 * always zero. No record a test can create exercises that filter, so no test here would notice
 * a fix.
 */
@isTest
private class RLM_CollectionsDashboardControllerTest {

    // The controller's own separators: an em dash for a missing value and an en dash
    // between a case's subject and description.
    private static final String NO_VALUE = '—';
    private static final String SUBJECT_SEPARATOR = ' – ';

    // ---- bounded reads (todo 435) ----

    @isTest
    static void requireWithin_allowsExactlyTheAllowanceAndNoMore() {
        RLM_CollectionsDashboardController.requireWithin(10, 10, 'rows');
        RLM_CollectionsDashboardController.requireWithin(0, 0, 'rows');
        for (List<Integer> over : new List<List<Integer>>{ new List<Integer>{ 11, 10 }, new List<Integer>{ 1, 0 } }) {
            try {
                RLM_CollectionsDashboardController.requireWithin(over[0], over[1], 'rows');
                Assert.fail(over[0] + ' rows against an allowance of ' + over[1] + ' must be too many');
            } catch (RLM_CollectionsDashboardController.TooManyRowsException e) {
                Assert.areEqual(RLM_CollectionsDashboardController.REASON_TOO_MANY,
                    RLM_CollectionsDashboardController.reasonFor(e), 'Its reason is tooMany');
            }
        }
    }

    @isTest
    static void rowAllowance_isTheCapOrWhatTheTransactionHasLeftLessTheHeadroom() {
        Integer headroom = RLM_CollectionsDashboardController.ROW_HEADROOM;
        Assert.areEqual(10000, RLM_CollectionsDashboardController.rowAllowance(10000, 50000, 0), 'The cap, with rows to spare');
        Assert.areEqual(5, RLM_CollectionsDashboardController.rowAllowance(5, 50000, 0), 'A smaller cap');
        Assert.areEqual(50000 - 45000 - headroom, RLM_CollectionsDashboardController.rowAllowance(10000, 50000, 45000),
            'What the transaction has left, less the headroom');
        Assert.areEqual(0, RLM_CollectionsDashboardController.rowAllowance(10000, 50000, 50000 - headroom),
            'Nothing once only the headroom is left');
        Assert.areEqual(0, RLM_CollectionsDashboardController.rowAllowance(10000, 50000, 49999), 'Never below zero');
    }

    // Every read a figure or a list is built from goes through the bound. Invoices cannot be inserted, so a
    // row cap cannot be shown to cut an invoice read: the reads each call made are checked by label instead.
    @isTest
    static void everySummedOrListedRead_isBounded() {
        Account a = newAccount('RLM CD Bounded');
        insert new Case(AccountId = a.Id, Subject = 'RLM CD bounded dispute');
        Date today = Date.newInstance(2026, 6, 30);
        List<Invoice> invoices = new List<Invoice>{
            invoice(new Map<String, Object>{ 'Id' => Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + '000000000008'),
                'Balance' => 2500, 'DueDate' => today.addDays(-40), 'BillingAccountId' => a.Id })
        };
        Set<String> cardReads = new Set<String>{ 'unpaid invoices', 'unapplied credits', 'unapplied payments' };
        if (Schema.getGlobalDescribe().containsKey('DebitMemo')) {
            cardReads.add('debit memos');
        }

        Test.startTest();
        Map<String, Set<String>> readsByCall = new Map<String, Set<String>>();
        RLM_CollectionsDashboardController.boundedReads.clear();
        RLM_CollectionsDashboardController.getDashboardCards(null, null);
        readsByCall.put('cards', new Set<String>(RLM_CollectionsDashboardController.boundedReads));
        RLM_CollectionsDashboardController.boundedReads.clear();
        RLM_CollectionsDashboardController.getWorklist(null, null);
        readsByCall.put('worklist', new Set<String>(RLM_CollectionsDashboardController.boundedReads));
        RLM_CollectionsDashboardController.boundedReads.clear();
        RLM_CollectionsDashboardController.addCriticalFollowUps(new RLM_CollectionsDashboardController.WorklistData(),
            invoices, false, false, today);
        readsByCall.put('critical', new Set<String>(RLM_CollectionsDashboardController.boundedReads));
        RLM_CollectionsDashboardController.boundedReads.clear();
        RLM_CollectionsDashboardController.addHighValueDelinquents(new RLM_CollectionsDashboardController.WorklistData(),
            invoices, 'BillingAccountId', today);
        readsByCall.put('highValue', new Set<String>(RLM_CollectionsDashboardController.boundedReads));
        RLM_CollectionsDashboardController.boundedReads.clear();
        RLM_CollectionsDashboardController.getPaymentPromiseSummary(null, null);
        readsByCall.put('promises', new Set<String>(RLM_CollectionsDashboardController.boundedReads));
        RLM_CollectionsDashboardController.boundedReads.clear();
        RLM_CollectionsDashboardController.getCollectionsProgress();
        readsByCall.put('progress', new Set<String>(RLM_CollectionsDashboardController.boundedReads));
        RLM_CollectionsDashboardController.boundedReads.clear();
        RLM_CollectionsDashboardController.getCollectionPlanTasks(null);
        readsByCall.put('tasks', new Set<String>(RLM_CollectionsDashboardController.boundedReads));
        Test.stopTest();

        Assert.areEqual(cardReads, readsByCall.get('cards'), 'Every card read is bounded');
        Assert.areEqual(new Set<String>{ 'high-value invoices', 'open cases', 'disputed invoices' }, readsByCall.get('worklist'),
            'The worklist\'s invoice and case reads are bounded');
        Assert.areEqual(new Set<String>{ 'collection plan items' }, readsByCall.get('critical'), 'The plan item lookup is bounded');
        Assert.areEqual(new Set<String>{ 'collection plans' }, readsByCall.get('highValue'), 'The plan lookup is bounded');
        Assert.areEqual(new Set<String>{ 'payment schedule items' }, readsByCall.get('promises'), 'The promise sums are bounded');
        Assert.areEqual(new Set<String>{ 'collection plans' }, readsByCall.get('progress'), 'The progress read is bounded');
        Assert.areEqual(new Set<String>{ 'collection plans' }, readsByCall.get('tasks'), 'The task plans read is bounded');
    }

    // Two records of each kind against a cap of one: each section built from them is unavailable as tooMany,
    // not a figure or list from the first row alone. The next test reads exactly the cap normally.
    @isTest
    static void sectionsWithMoreRowsThanTheCap_sayTooMany() {
        seedTwoOfEach();
        RLM_CollectionsDashboardController.ROW_CAP = 1;

        Test.startTest();
        RLM_CollectionsDashboardController.CollectionsDashboardData cards = RLM_CollectionsDashboardController.getDashboardCards(null, null);
        RLM_CollectionsDashboardController.WorklistData wl = RLM_CollectionsDashboardController.getWorklist(null, null);
        RLM_CollectionsDashboardController.PaymentPromiseSummary promises = RLM_CollectionsDashboardController.getPaymentPromiseSummary(null, null);
        RLM_CollectionsDashboardController.CollectionsProgressData progress = RLM_CollectionsDashboardController.getCollectionsProgress();
        RLM_CollectionsDashboardController.CpTaskList tasks = RLM_CollectionsDashboardController.getCollectionPlanTasks(null);
        Test.stopTest();

        String tooMany = RLM_CollectionsDashboardController.REASON_TOO_MANY;
        Assert.areEqual(tooMany, cards.unavailableReason.get(RLM_CollectionsDashboardController.UNAVAILABLE_PAYMENTS),
            'Two unapplied payments against a cap of one: too many to total');
        Assert.isNull(cards.unappliedPaymentBalance, 'No payment balance from one of the two');
        Assert.isFalse(cards.unavailable.contains(RLM_CollectionsDashboardController.UNAVAILABLE_INVOICES),
            'No invoice rows: within the cap');
        Assert.areEqual(tooMany, wl.unavailableReason.get(RLM_CollectionsDashboardController.WORKLIST_DISPUTED),
            'Two open cases against a cap of one: the disputed tab is too many');
        Assert.isTrue(wl.disputedInvoices.isEmpty(), 'No rows from the first case alone');
        Assert.isTrue(promises.unavailable, 'Two schedule items against a cap of one');
        Assert.areEqual(tooMany, promises.unavailableReason, 'The promise sums are too many');
        Assert.isTrue(progress.unavailable, 'Two plans against a cap of one');
        Assert.areEqual(tooMany, progress.unavailableReason, 'Progress is too many');
        Assert.isTrue(tasks.unavailable, 'Two plans against a cap of one');
        Assert.areEqual(tooMany, tasks.unavailableReason, 'The task plans are too many');
    }

    @isTest
    static void sectionsWithExactlyTheCap_readNormally() {
        seedTwoOfEach();
        RLM_CollectionsDashboardController.ROW_CAP = 2;

        Test.startTest();
        RLM_CollectionsDashboardController.CollectionsDashboardData cards = RLM_CollectionsDashboardController.getDashboardCards(null, null);
        RLM_CollectionsDashboardController.WorklistData wl = RLM_CollectionsDashboardController.getWorklist(null, null);
        RLM_CollectionsDashboardController.PaymentPromiseSummary promises = RLM_CollectionsDashboardController.getPaymentPromiseSummary(null, null);
        RLM_CollectionsDashboardController.CollectionsProgressData progress = RLM_CollectionsDashboardController.getCollectionsProgress();
        RLM_CollectionsDashboardController.CpTaskList tasks = RLM_CollectionsDashboardController.getCollectionPlanTasks(null);
        Test.stopTest();

        Assert.isFalse(cards.unavailable.contains(RLM_CollectionsDashboardController.UNAVAILABLE_PAYMENTS),
            'Two payments against a cap of two are read: ' + cards.unavailableReason);
        Assert.areEqual(2, cards.unappliedPaymentCount, 'Both payments are counted');
        Assert.isFalse(wl.unavailable.contains(RLM_CollectionsDashboardController.WORKLIST_DISPUTED),
            'Two cases against a cap of two are read: ' + wl.unavailableReason);
        Assert.areEqual(2, wl.disputedInvoices.size(), 'Both disputed accounts are listed');
        Assert.isFalse(promises.unavailable, 'Two schedule items against a cap of two are read');
        Assert.isFalse(progress.unavailable, 'Two plans against a cap of two are read');
        Assert.areEqual(2, progress.totalPlans, 'Both plans are counted');
        Assert.isFalse(tasks.unavailable, 'Two plans against a cap of two are read');
    }

    // Two accounts, each with an open case, a Processed (unapplied) payment, a collection plan and a Draft
    // payment schedule item.
    private static void seedTwoOfEach() {
        Account a = newAccount('RLM CD Bound A');
        Account b = newAccount('RLM CD Bound B');
        insert new List<Case>{ new Case(AccountId = a.Id, Subject = 'RLM CD bound dispute A'),
            new Case(AccountId = b.Id, Subject = 'RLM CD bound dispute B') };
        String corporate = corporateCurrency();
        insert new List<Payment>{ payment(a.Id, 10, 'Processed', corporate), payment(b.Id, 20, 'Processed', corporate) };
        insert new List<CollectionPlan>{ newPlan(a.Id, Date.today().addDays(10)), newPlan(b.Id, Date.today().addDays(20)) };
        PaymentSchedule ps = new PaymentSchedule(Status = 'Draft', TotalRequestedAmount = 30, CurrencyIsoCode = corporate);
        insert ps;
        insert new List<PaymentScheduleItem>{
            new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = a.Id, CurrencyIsoCode = corporate,
                RequestedAmount = 10, TargetPaymentProcessingDate = Date.today(), Status = 'Draft'),
            new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = b.Id, CurrencyIsoCode = corporate,
                RequestedAmount = 20, TargetPaymentProcessingDate = Date.today(), Status = 'Draft')
        };
    }

    // A spent allowance runs no query: the section is too many at once, so later reads cannot each cost a row.
    @isTest
    static void aReadWithNoAllowanceLeft_runsNoQueryAndSaysTooMany() {
        RLM_CollectionsDashboardController.ROW_CAP = 0;

        Test.startTest();
        Integer queriesBefore = Limits.getQueries();
        Integer rowsBefore = Limits.getQueryRows();
        RLM_CollectionsDashboardController.CollectionsProgressData progress = RLM_CollectionsDashboardController.getCollectionsProgress();
        Integer queriesRun = Limits.getQueries() - queriesBefore;
        Integer rowsRead = Limits.getQueryRows() - rowsBefore;
        Test.stopTest();

        Assert.areEqual(0, queriesRun, 'No query with no allowance');
        Assert.areEqual(0, rowsRead, 'No query rows with no allowance');
        Assert.isTrue(progress.unavailable, 'Unavailable, not "no plans"');
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_TOO_MANY, progress.unavailableReason, 'Too many');
    }

    // The Disputed tab lists the DISPUTED_ROWS accounts with the newest open cases and says when there are more.
    @isTest
    static void disputedTab_withMoreAccountsThanItLists_saysItHasMore() {
        Account a = newAccount('RLM CD Disputed Bound A');
        Account b = newAccount('RLM CD Disputed Bound B');
        insert new Case(AccountId = a.Id, Subject = 'RLM CD bound A');
        Case newer = new Case(AccountId = b.Id, Subject = 'RLM CD bound B');
        insert newer;
        Test.setCreatedDate(newer.Id, Datetime.now().addMinutes(5));

        Test.startTest();
        RLM_CollectionsDashboardController.DISPUTED_ROWS = 1;
        RLM_CollectionsDashboardController.WorklistData over = RLM_CollectionsDashboardController.getWorklist(null, null);
        RLM_CollectionsDashboardController.DISPUTED_ROWS = 2;
        RLM_CollectionsDashboardController.WorklistData exact = RLM_CollectionsDashboardController.getWorklist(null, null);
        Test.stopTest();

        Assert.isFalse(over.unavailable.contains(RLM_CollectionsDashboardController.WORKLIST_DISPUTED), 'Listed, not unavailable');
        Assert.areEqual(1, over.disputedInvoices.size(), 'One account listed');
        Assert.areEqual(b.Id, over.disputedInvoices[0].accountId, 'The newest open case first');
        Assert.areEqual(new List<String>{ RLM_CollectionsDashboardController.FILTER_ACCOUNT },
            over.hasMore.get(RLM_CollectionsDashboardController.WORKLIST_DISPUTED),
            'Two disputed accounts, one listed: more, and only the account narrows which accounts have open cases');
        Assert.isFalse(exact.unavailable.contains(RLM_CollectionsDashboardController.WORKLIST_DISPUTED), 'Two of two are listed');
        Assert.isFalse(exact.hasMore.containsKey(RLM_CollectionsDashboardController.WORKLIST_DISPUTED), 'No more');
        Assert.areEqual(2, exact.disputedInvoices.size(), 'Both accounts are listed');
    }

    // Case text is read DESCRIPTION_BATCH cases per query, each account's reason from its own case.
    @isTest
    static void readDisputeReasons_readsTheShownCasesInBatches() {
        List<Account> accounts = new List<Account>{ new Account(Name = 'RLM CD Batch 1'), new Account(Name = 'RLM CD Batch 2'),
            new Account(Name = 'RLM CD Batch 3') };
        insert accounts;
        List<Case> shown = new List<Case>();
        for (Integer i = 0; i < accounts.size(); i++) {
            shown.add(new Case(AccountId = accounts[i].Id, Subject = 'RLM CD batch subject ' + i, Description = 'Note ' + i));
        }
        insert shown;
        RLM_CollectionsDashboardController.DESCRIPTION_BATCH = 2;

        Test.startTest();
        Integer queriesBefore = Limits.getQueries();
        Map<Id, String> reasons = RLM_CollectionsDashboardController.readDisputeReasons(shown);
        Integer queriesRun = Limits.getQueries() - queriesBefore;
        Test.stopTest();

        Assert.areEqual(2, queriesRun, 'Three cases, two per query: two queries');
        for (Integer i = 0; i < accounts.size(); i++) {
            Assert.isTrue(reasons.get(accounts[i].Id).startsWith('RLM CD batch subject ' + i + SUBJECT_SEPARATOR + 'Note ' + i),
                'Each account\'s reason comes from its own case: ' + reasons.get(accounts[i].Id));
        }
    }

    // A failure after the High-Value read (its roll-up, names or plan lookup) marks the tab, not an empty list.
    @isTest
    static void worklist_aFailureInTheHighValueRows_marksTheTabUnavailable() {
        RLM_CollectionsDashboardController.forcedFailures.add('highValueRows');

        Test.startTest();
        RLM_CollectionsDashboardController.WorklistData wl = RLM_CollectionsDashboardController.getWorklist(null, null);
        Test.stopTest();

        Assert.areEqual(RLM_CollectionsDashboardController.REASON_FAILED,
            wl.unavailableReason.get(RLM_CollectionsDashboardController.WORKLIST_HIGH_VALUE), 'The High-Value tab failed, not empty');
        Assert.isFalse(wl.unavailable.contains(RLM_CollectionsDashboardController.WORKLIST_CRITICAL), 'Critical is unaffected');
        Assert.isFalse(wl.unavailable.contains(RLM_CollectionsDashboardController.WORKLIST_DISPUTED), 'Disputed is unaffected');
    }

    // Anything escaping a tab's builder marks that tab in getWorklist's own catch; the other tabs still build.
    @isTest
    static void worklist_aFailureEscapingABuilder_marksItsTabAndBuildsTheOthers() {
        Account a = newAccount('RLM CD Escaping Failure');
        insert new Case(AccountId = a.Id, Subject = 'RLM CD escaping failure');
        RLM_CollectionsDashboardController.forcedFailures.addAll(new Set<String>{
            RLM_CollectionsDashboardController.WORKLIST_CRITICAL, RLM_CollectionsDashboardController.WORKLIST_DISPUTED });

        Test.startTest();
        RLM_CollectionsDashboardController.WorklistData wl = RLM_CollectionsDashboardController.getWorklist(null, null);
        Test.stopTest();

        for (String tab : new List<String>{ RLM_CollectionsDashboardController.WORKLIST_CRITICAL, RLM_CollectionsDashboardController.WORKLIST_DISPUTED }) {
            Assert.areEqual(RLM_CollectionsDashboardController.REASON_FAILED, wl.unavailableReason.get(tab), tab + ' failed, not empty');
        }
        Assert.isTrue(wl.disputedInvoices.isEmpty(), 'An unavailable tab carries no rows');
        Assert.isFalse(wl.unavailable.contains(RLM_CollectionsDashboardController.WORKLIST_HIGH_VALUE), 'High-Value is still built');
    }

    // The Disputed tab's promise-to-pay reads, run without invoices (Apex cannot insert them): each is bounded.
    @isTest
    static void schedulesForInvoices_isABoundedRead() {
        Id someInvoice = Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + '000000000007');

        Test.startTest();
        RLM_CollectionsDashboardController.boundedReads.clear();
        Map<Id, Id> schedules = RLM_CollectionsDashboardController.schedulesForInvoices(new Set<Id>{ someInvoice });
        Set<String> reads = new Set<String>(RLM_CollectionsDashboardController.boundedReads);
        Test.stopTest();

        Assert.isTrue(schedules.isEmpty(), 'No schedule refers to that invoice');
        Assert.areEqual(new Set<String>{ 'payment schedules' }, reads, 'The schedule read is bounded');
    }

    @isTest
    static void latestPromiseDates_takesEachAccountsLatestItemDate_andIsBounded() {
        Account acc = newAccount('RLM CD Promise Dates');
        String corporate = corporateCurrency();
        PaymentSchedule ps = new PaymentSchedule(Status = 'Draft', TotalRequestedAmount = 30, CurrencyIsoCode = corporate);
        insert ps;
        Date sooner = Date.today().addDays(3);
        Date later = Date.today().addDays(9);
        insert new List<PaymentScheduleItem>{
            new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id, CurrencyIsoCode = corporate,
                RequestedAmount = 10, TargetPaymentProcessingDate = later, Status = 'Draft'),
            new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id, CurrencyIsoCode = corporate,
                RequestedAmount = 20, TargetPaymentProcessingDate = sooner, Status = 'Draft')
        };
        Id someInvoice = Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + '000000000006');
        Map<Id, Id> scheduleToInvoice = new Map<Id, Id>{ ps.Id => someInvoice };
        Map<Id, Id> invoiceToAccount = new Map<Id, Id>{ someInvoice => acc.Id };

        Test.startTest();
        RLM_CollectionsDashboardController.boundedReads.clear();
        Map<Id, Date> dates = RLM_CollectionsDashboardController.latestPromiseDates(scheduleToInvoice, invoiceToAccount);
        Set<String> reads = new Set<String>(RLM_CollectionsDashboardController.boundedReads);
        RLM_CollectionsDashboardController.ROW_CAP = 1;
        Boolean tooMany = false;
        try {
            RLM_CollectionsDashboardController.latestPromiseDates(scheduleToInvoice, invoiceToAccount);
        } catch (RLM_CollectionsDashboardController.TooManyRowsException e) {
            tooMany = true;
        }
        Test.stopTest();

        Assert.areEqual(later, dates.get(acc.Id), 'The latest of the account\'s item dates');
        Assert.areEqual(new Set<String>{ 'payment schedule items' }, reads, 'The schedule item read is bounded');
        Assert.isTrue(tooMany, 'Two items against a cap of one: too many, not the first date alone');
    }

    // ---- short lists say when there are more (todo 435) ----

    @isTest
    static void keepFirst_keepsTheListedRowsAndSaysWhenThereWereMore() {
        List<Integer> over = new List<Integer>{ 1, 2, 3 };
        List<Integer> exact = new List<Integer>{ 1, 2 };
        Assert.isTrue(RLM_CollectionsDashboardController.keepFirst(over, 2), 'Three rows, two listed: more');
        Assert.areEqual(new List<Integer>{ 1, 2 }, over, 'The first two are kept, in order');
        Assert.isFalse(RLM_CollectionsDashboardController.keepFirst(exact, 2), 'Two rows, two listed: no more');
        Assert.areEqual(2, exact.size(), 'Nothing removed');
    }

    @isTest
    static void planTasks_withMoreThanTheListShows_sayTheyHaveMore() {
        Account a = newAccount('RLM CD Task Rows');
        CollectionPlan plan = newPlan(a.Id, Date.today());
        insert plan;
        insert new List<Task>{
            new Task(WhatId = plan.Id, Subject = 'RLM CD later', ActivityDate = Date.today().addDays(5)),
            new Task(WhatId = plan.Id, Subject = 'RLM CD sooner', ActivityDate = Date.today())
        };

        Test.startTest();
        RLM_CollectionsDashboardController.TASK_ROWS = 1;
        RLM_CollectionsDashboardController.CpTaskList over = RLM_CollectionsDashboardController.getCollectionPlanTasks(null);
        RLM_CollectionsDashboardController.TASK_ROWS = 2;
        RLM_CollectionsDashboardController.CpTaskList exact = RLM_CollectionsDashboardController.getCollectionPlanTasks(null);
        Test.stopTest();

        Assert.areEqual(1, over.items.size(), 'One task listed');
        Assert.areEqual('RLM CD later', over.items[0].subject, 'The latest due first');
        Assert.isTrue(over.hasMore, 'Two tasks, one listed: the list says there are more');
        Assert.areEqual(2, exact.items.size(), 'Both tasks listed');
        Assert.isFalse(exact.hasMore, 'Two tasks, two listed: no more');
    }

    @isTest
    static void myPlans_withMoreThanTheListShows_sayTheyHaveMore() {
        Account a = newAccount('RLM CD Plan Rows');
        insert new List<CollectionPlan>{ newPlan(a.Id, Date.today().addDays(20)), newPlan(a.Id, Date.today().addDays(2)) };

        Test.startTest();
        RLM_CollectionsDashboardController.MY_PLAN_ROWS = 1;
        RLM_CollectionsDashboardController.MyCollectionPlanList over = RLM_CollectionsDashboardController.getMyCollectionPlans();
        RLM_CollectionsDashboardController.MY_PLAN_ROWS = 2;
        RLM_CollectionsDashboardController.MyCollectionPlanList exact = RLM_CollectionsDashboardController.getMyCollectionPlans();
        Test.stopTest();

        Assert.areEqual(1, over.items.size(), 'One plan listed');
        Assert.areEqual(Date.today().addDays(2), over.items[0].dueDate, 'The soonest due first');
        Assert.isTrue(over.hasMore, 'Two plans, one listed: the list says there are more');
        Assert.areEqual(2, exact.items.size(), 'Both plans listed');
        Assert.isFalse(exact.hasMore, 'Two plans, two listed: no more');
    }

    @isTest
    static void highValueTab_withMoreQualifyingAccountsThanItLists_saysItHasMore() {
        Account big = newAccount('RLM CD HV Big');
        Account small = newAccount('RLM CD HV Small');
        Date today = Date.newInstance(2026, 6, 30);
        List<Invoice> invoices = new List<Invoice>{
            invoice(new Map<String, Object>{ 'Balance' => 9000, 'DueDate' => today.addDays(-40), 'BillingAccountId' => big.Id }),
            invoice(new Map<String, Object>{ 'Balance' => 3000, 'DueDate' => today.addDays(-40), 'BillingAccountId' => small.Id })
        };
        RLM_CollectionsDashboardController.WorklistData over = new RLM_CollectionsDashboardController.WorklistData();
        RLM_CollectionsDashboardController.WorklistData exact = new RLM_CollectionsDashboardController.WorklistData();

        Test.startTest();
        RLM_CollectionsDashboardController.HIGH_VALUE_ROWS = 1;
        RLM_CollectionsDashboardController.addHighValueDelinquents(over, invoices, 'BillingAccountId', today);
        RLM_CollectionsDashboardController.HIGH_VALUE_ROWS = 2;
        RLM_CollectionsDashboardController.addHighValueDelinquents(exact, invoices, 'BillingAccountId', today);
        Test.stopTest();

        Assert.areEqual(1, over.highValueDelinquents.size(), 'One account listed');
        Assert.areEqual(big.Id, over.highValueDelinquents[0].accountId, 'The largest balance first');
        Assert.isTrue(over.hasMore.containsKey(RLM_CollectionsDashboardController.WORKLIST_HIGH_VALUE),
            'Two qualifying accounts, one listed: the tab says there are more');
        Assert.isTrue(over.hasMore.get(RLM_CollectionsDashboardController.WORKLIST_HIGH_VALUE)
            .contains(RLM_CollectionsDashboardController.FILTER_ACCOUNT), 'The account narrows it');
        Assert.areEqual(2, exact.highValueDelinquents.size(), 'Both accounts listed');
        Assert.isTrue(exact.hasMore.isEmpty(), 'Two of two listed: no more');
    }

    // ---- account options and search (todo 435) ----

    @isTest
    static void accountOptions_withMoreAccountsThanListed_sayTheyHaveMore() {
        newAccount('RLM CD Options A');
        newAccount('RLM CD Options B');
        Integer accounts = [SELECT COUNT() FROM Account];

        Test.startTest();
        RLM_CollectionsDashboardController.ACCOUNT_OPTION_ROWS = accounts - 1;
        RLM_CollectionsDashboardController.AccountOptions over = RLM_CollectionsDashboardController.getAccountOptions();
        RLM_CollectionsDashboardController.ACCOUNT_OPTION_ROWS = accounts;
        RLM_CollectionsDashboardController.AccountOptions exact = RLM_CollectionsDashboardController.getAccountOptions();
        Test.stopTest();

        Assert.areEqual(accounts, over.options.size(), '"All Accounts" and all but one account');
        Assert.isTrue(over.hasMore, 'One more account than listed: the filter says so');
        Assert.areEqual(accounts + 1, exact.options.size(), '"All Accounts" and every account');
        Assert.isFalse(exact.hasMore, 'Every account listed: no more');
    }

    @isTest
    static void searchAccounts_matchesTheTypedTextLiterally_andIsBounded() {
        newAccount('RLM CD Srch 100% Alpha');
        newAccount('RLM CD Srch 1000 Beta');
        newAccount('RLM CD Srch Gamma');

        Test.startTest();
        RLM_CollectionsDashboardController.AccountOptions all = RLM_CollectionsDashboardController.searchAccounts(' RLM CD Srch ');
        RLM_CollectionsDashboardController.AccountOptions percent = RLM_CollectionsDashboardController.searchAccounts('100%');
        RLM_CollectionsDashboardController.AccountOptions tooShort = RLM_CollectionsDashboardController.searchAccounts('R');
        RLM_CollectionsDashboardController.ACCOUNT_SEARCH_ROWS = 2;
        RLM_CollectionsDashboardController.AccountOptions capped = RLM_CollectionsDashboardController.searchAccounts('RLM CD Srch');
        Test.stopTest();

        Assert.areEqual(4, all.options.size(), '"All Accounts" and the three matches (the text is trimmed)');
        Assert.areEqual('', all.options[0].get('value'), '"All Accounts" first');
        Assert.areEqual('RLM CD Srch 100% Alpha', all.options[1].get('label'), 'By name (% sorts before 0)');
        Assert.isFalse(all.hasMore, 'Three of three');
        Assert.areEqual(2, percent.options.size(), 'A typed % is matched literally, not as a wildcard: ' + percent.options);
        Assert.areEqual('RLM CD Srch 100% Alpha', percent.options[1].get('label'), 'Only the account with "100%"');
        Assert.areEqual(1, tooShort.options.size(), 'Too short a text searches nothing');
        Assert.areEqual(3, capped.options.size(), '"All Accounts" and the first two');
        Assert.isTrue(capped.hasMore, 'Three matches, two listed: more');
    }

    @isTest
    static void searchAccounts_forAUserWhoCannotReadAccounts_saysItCouldNotSearch() {
        User noAccess = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        newAccount('RLM CD Srch Unreadable');
        RLM_CollectionsDashboardController.AccountOptions found;

        Test.startTest();
        System.runAs(noAccess) {
            found = RLM_CollectionsDashboardController.searchAccounts('RLM CD Srch');
        }
        Test.stopTest();

        Assert.isTrue(found.unavailable, 'Unavailable, not "no match"');
        Assert.areEqual(1, found.options.size(), 'Only "All Accounts"');
    }

    // ---- filters each section applies (todo 435) ----

    @isTest
    static void everySection_reportsTheFiltersItsReadsApply() {
        Boolean invoiceCurrency = Schema.SObjectType.Invoice.fields.getMap().containsKey('CurrencyIsoCode');
        Boolean paymentCurrency = Schema.SObjectType.Payment.fields.getMap().containsKey('CurrencyIsoCode');
        List<String> invoiceFilters = new List<String>{ RLM_CollectionsDashboardController.FILTER_ACCOUNT };
        if (invoiceCurrency) invoiceFilters.add(RLM_CollectionsDashboardController.FILTER_CURRENCY);
        List<String> paymentFilters = new List<String>{ RLM_CollectionsDashboardController.FILTER_ACCOUNT };
        if (paymentCurrency) paymentFilters.add(RLM_CollectionsDashboardController.FILTER_CURRENCY);

        Test.startTest();
        RLM_CollectionsDashboardController.CollectionsDashboardData cards = RLM_CollectionsDashboardController.getDashboardCards(null, null);
        RLM_CollectionsDashboardController.WorklistData wl = RLM_CollectionsDashboardController.getWorklist(null, null);
        RLM_CollectionsDashboardController.CpTaskList tasks = RLM_CollectionsDashboardController.getCollectionPlanTasks(null);
        RLM_CollectionsDashboardController.MyCollectionPlanList plans = RLM_CollectionsDashboardController.getMyCollectionPlans();
        RLM_CollectionsDashboardController.CollectionsProgressData progress = RLM_CollectionsDashboardController.getCollectionsProgress();
        RLM_CollectionsDashboardController.PaymentPromiseSummary promises = RLM_CollectionsDashboardController.getPaymentPromiseSummary(null, null);
        Test.stopTest();

        Assert.areEqual(invoiceFilters, cards.filtersByKey.get(RLM_CollectionsDashboardController.UNAVAILABLE_INVOICES), 'Invoices');
        Assert.areEqual(paymentFilters, cards.filtersByKey.get(RLM_CollectionsDashboardController.UNAVAILABLE_PAYMENTS), 'Payments');
        Assert.areEqual(paymentFilters, cards.filtersByKey.get(RLM_CollectionsDashboardController.UNAVAILABLE_CREDITS), 'Credits');
        for (String tab : new List<String>{ RLM_CollectionsDashboardController.WORKLIST_CRITICAL,
                RLM_CollectionsDashboardController.WORKLIST_HIGH_VALUE, RLM_CollectionsDashboardController.WORKLIST_DISPUTED }) {
            Assert.areEqual(invoiceFilters, wl.filtersByTab.get(tab), 'Every tab reads invoices: ' + tab);
        }
        Assert.areEqual(new List<String>{ RLM_CollectionsDashboardController.FILTER_ACCOUNT }, tasks.filters, 'Tasks: the account');
        Assert.isTrue(plans.filters.isEmpty(), 'The user\'s plans: none');
        Assert.isTrue(progress.filters.isEmpty(), 'Progress: none');
        Assert.isTrue(promises.filters.contains(RLM_CollectionsDashboardController.FILTER_ACCOUNT), 'Promises: the account');
    }

    // ---- High-Value ranking (todo 435) ----

    @isTest
    static void largestBalances_picksTheLargestAtOrOverTheMinimum_inOrder() {
        String prefix = Account.SObjectType.getDescribe().getKeyPrefix();
        Map<Id, Decimal> balances = new Map<Id, Decimal>();
        List<Decimal> amounts = new List<Decimal>{ 2500, 1999, 9000, 2000, 7000, 9000 };
        List<Id> ids = new List<Id>();
        for (Integer i = 0; i < amounts.size(); i++) {
            Id accId = Id.valueOf(prefix + String.valueOf(i).leftPad(12, '0'));
            ids.add(accId);
            balances.put(accId, amounts[i]);
        }

        Assert.areEqual(new List<Id>{ ids[2], ids[5], ids[4] }, RLM_CollectionsDashboardController.largestBalances(balances, 2000, 3),
            'The three largest, ties in the map\'s order');
        Assert.areEqual(new List<Id>{ ids[2], ids[5], ids[4], ids[0], ids[3] }, RLM_CollectionsDashboardController.largestBalances(balances, 2000, 10),
            'Every balance of 2000 or more, largest first; 1999 is left out');
        Assert.isTrue(RLM_CollectionsDashboardController.largestBalances(new Map<Id, Decimal>(), 2000, 10).isEmpty(), 'None');
    }

    // The roll-up at the read cap: 10,000 invoices on 10,000 accounts, all qualifying. Ranking builds no row per
    // account, so the call stays within the heap and CPU limits and lists the ten largest.
    @isTest
    static void addHighValueDelinquents_atTheReadCap_listsTheTenLargest() {
        String accountPrefix = Account.SObjectType.getDescribe().getKeyPrefix();
        String invoicePrefix = Invoice.SObjectType.getDescribe().getKeyPrefix();
        // The JSON is built as text (Invoice's amounts cannot be set on a record), one row at a time, so the
        // test itself holds no more than the text and the rows.
        List<String> rows = new List<String>();
        for (Integer i = 0; i < 10000; i++) {
            rows.add('{"attributes":{"type":"Invoice"},"Id":"' + invoicePrefix + String.valueOf(i).leftPad(12, '0')
                + '","Balance":' + (2000 + i) + ',"DueDate":"2026-05-01","BillingAccountId":"'
                + accountPrefix + String.valueOf(i).leftPad(12, '0') + '"}');
        }
        String body = '[' + String.join(rows, ',') + ']';
        rows = null;
        List<Invoice> invoices = (List<Invoice>) JSON.deserialize(body, List<Invoice>.class);
        body = null;
        RLM_CollectionsDashboardController.WorklistData wl = new RLM_CollectionsDashboardController.WorklistData();

        Test.startTest();
        RLM_CollectionsDashboardController.addHighValueDelinquents(wl, invoices, 'BillingAccountId', Date.newInstance(2026, 6, 30));
        Test.stopTest();

        Assert.areEqual(10, wl.highValueDelinquents.size(), 'The ten largest');
        Assert.areEqual(11999, wl.highValueDelinquents[0].balance, 'Largest first');
        Assert.isTrue(wl.hasMore.containsKey(RLM_CollectionsDashboardController.WORKLIST_HIGH_VALUE), 'More qualify');
    }

    // The name read says when it could not read, so a row can show its name as not available, not "none".
    @isTest
    static void accountNamesRead_saysWhenTheNamesCouldNotBeRead() {
        User noAccess = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        Account a = newAccount('RLM CD Name Read');
        insert newPlan(a.Id, Date.today());
        RLM_AccountNames.Result refused;

        Test.startTest();
        RLM_AccountNames.Result readable = RLM_AccountNames.read(new Set<Id>{ a.Id });
        Boolean planNameUnavailable = RLM_CollectionsDashboardController.getMyCollectionPlans().items[0].accountNameUnavailable;
        System.runAs(noAccess) {
            refused = RLM_AccountNames.read(new Set<Id>{ a.Id });
        }
        Test.stopTest();

        Assert.isFalse(readable.unreadable, 'The admin reads the name');
        Assert.areEqual('RLM CD Name Read', readable.names.get(a.Id), 'And gets it');
        Assert.isFalse(planNameUnavailable, 'A read name is available on the plan row');
        Assert.isTrue(refused.unreadable, 'A refused read says so');
        Assert.isTrue(refused.names.isEmpty(), 'With no names');
    }

    // ---- the collections user (todo 435) ----

    private static final List<String> COLLECTIONS_LICENSES = new List<String>{
        RLM_BillingUITestUsers.BILLING_PSL, RLM_BillingUITestUsers.BILLING_ADVANCED_PSL
    };

    // RLM_CollectionsDashboard opens the dashboard for a collections user who does not hold RLM_BillingUI:
    // the tab (hidden on every profile when deployed through the Metadata API), this controller, and only
    // the reads the managed Billing Collections and Recovery Specialist set lacks. Read back from the org,
    // so a grant the platform drops or adds shows here (Event.WhatId is added with Task.WhatId).
    @isTest
    static void collectionsDashboardSet_grantsTheTabTheControllerAndTheSpecialistsMissingReads() {
        PermissionSet ps = [SELECT Id FROM PermissionSet WHERE Name = 'RLM_CollectionsDashboard'];
        List<SetupEntityAccess> access = [
            SELECT SetupEntityId FROM SetupEntityAccess WHERE ParentId = :ps.Id
        ];
        Id controllerId = [SELECT Id FROM ApexClass WHERE Name = 'RLM_CollectionsDashboardController' LIMIT 1].Id;
        Assert.areEqual(1, access.size(), 'One entity access: the controller. ' + access);
        Assert.areEqual(controllerId, access[0].SetupEntityId, 'The dashboard controller is granted.');

        List<PermissionSetTabSetting> tabs = [
            SELECT Name, Visibility FROM PermissionSetTabSetting WHERE ParentId = :ps.Id
        ];
        Assert.areEqual(1, tabs.size(), 'One tab setting: the dashboard tab. ' + tabs);
        Assert.areEqual('RLM_Collections_Dashboard', tabs[0].Name);
        Assert.areEqual('DefaultOn', tabs[0].Visibility, 'Visible in metadata reads back as DefaultOn.');

        Set<String> objects = new Set<String>();
        for (ObjectPermissions op : [
            SELECT SobjectType, PermissionsRead, PermissionsCreate, PermissionsEdit, PermissionsDelete,
                PermissionsViewAllRecords, PermissionsModifyAllRecords
            FROM ObjectPermissions WHERE ParentId = :ps.Id
        ]) {
            objects.add(op.SobjectType);
            Assert.isTrue(op.PermissionsRead && !op.PermissionsCreate && !op.PermissionsEdit && !op.PermissionsDelete
                && !op.PermissionsViewAllRecords && !op.PermissionsModifyAllRecords, 'Read only: ' + op);
        }
        Assert.areEqual(new Set<String>{ 'Case', 'Payment' }, objects, 'Object reads the specialist set lacks.');

        Set<String> fields = new Set<String>();
        for (FieldPermissions fp : [SELECT Field, PermissionsEdit FROM FieldPermissions WHERE ParentId = :ps.Id]) {
            fields.add(fp.Field);
            Assert.isFalse(fp.PermissionsEdit, 'Read only: ' + fp.Field);
        }
        Assert.areEqual(new Set<String>{
            'Case.AccountId', 'Case.Description', 'Case.Reason', 'Case.Subject', 'CollectionPlan.AccountId',
            'CollectionPlan.ClosedDate', 'CollectionPlan.DaysPastDue', 'CollectionPlan.Duedate', 'CollectionPlanItem.InvoiceId',
            'Event.WhatId', 'Task.ActivityDate', 'Task.WhatId'
        }, fields, 'Field reads the specialist set lacks.');
    }

    // The dashboard as the collections user it is for, with no RLM_BillingUI: the Billing and Billing
    // Advanced licenses, the managed Billing Collections and Recovery Specialist set and
    // RLM_CollectionsDashboard (no RLM_CollectionsUI: it ships with the collections flag, which can be off
    // while billing_ui is on). Every section that reads a record the test can create returns it
    // (invoices cannot be inserted; RLM_BillingUIAccessTest.collectionsUserWithoutBillingUiCanRunTheDashboardReads
    // runs every read the controller makes as this user). Debit memos are the one component this user
    // cannot read (no Manage Debit Memos): the cards say so instead of counting them as zero.
    // The records are owned by this user, so what it sees does not depend on the org's sharing defaults
    // (Payment has no owner; it follows the org-wide default, Read/Write on a fresh 264 org).
    //
    // The control is the same user without RLM_CollectionsDashboard. Its refusals are checked at the
    // reads themselves, not through empty sections, which sharing alone could also empty: the case
    // subject and task date selects are refused, and the cards mark payments unavailable (a refusal,
    // distinct from "none").
    @isTest
    static void collectionsUser_withoutBillingUi_getsEverySectionsData() {
        User withSet = RLM_BillingUITestUsers.create(new List<String>{
            'BillingCollectionsAndRecoverySpecialist', 'RLM_CollectionsDashboard'
        }, COLLECTIONS_LICENSES);
        User withoutSet = RLM_BillingUITestUsers.create(new List<String>{
            'BillingCollectionsAndRecoverySpecialist'
        }, COLLECTIONS_LICENSES);
        Account a = new Account(Name = 'RLM CD Collections User', OwnerId = withSet.Id);
        insert a;
        CollectionPlan plan = newPlan(a.Id, Date.today().addDays(3));
        plan.OwnerId = withSet.Id;
        insert plan;
        insert new Task(WhatId = plan.Id, Subject = 'RLM CD collections call', ActivityDate = Date.today(),
            OwnerId = withSet.Id);
        insert new Case(AccountId = a.Id, Subject = 'RLM CD collections dispute', OwnerId = withSet.Id);
        insert payment(a.Id, 250, 'Processed', corporateCurrency());
        List<String> dashboardReads = new List<String>{
            'SELECT Subject, Reason FROM Case LIMIT 1',
            'SELECT ActivityDate, WhatId FROM Task LIMIT 1',
            'SELECT Balance FROM Payment LIMIT 1',
            'SELECT Duedate, AccountId, ClosedDate, DaysPastDue FROM CollectionPlan LIMIT 1'
        };

        Map<String, Object> granted;
        Map<String, Object> control;
        List<String> refusedWithSet = new List<String>();
        List<String> refusedWithoutSet = new List<String>();
        Test.startTest();
        System.runAs(withSet) {
            for (String soql : dashboardReads) {
                if (userModeQueryFails(soql)) refusedWithSet.add(soql);
            }
            granted = dashboardFor(a.Id);
        }
        System.runAs(withoutSet) {
            for (String soql : dashboardReads) {
                if (userModeQueryFails(soql)) refusedWithoutSet.add(soql);
            }
            control = dashboardFor(a.Id);
        }
        Test.stopTest();

        Assert.areEqual(new List<String>(), refusedWithSet, 'With the set every one of these reads runs.');
        Assert.isTrue(((List<Map<String, String>>) granted.get('accounts')).size() > 1, 'Accounts are listed.');
        Assert.isTrue(((List<Map<String, String>>) granted.get('currencies')).size() > 1, 'Currencies are listed.');
        Assert.areEqual(1, granted.get('payments'), 'The unapplied payment is counted.');
        Assert.areEqual(1, granted.get('disputed'), 'The open case lists the account as disputed.');
        Assert.areEqual(Date.today(), granted.get('taskDate'), 'The plan task is listed with its due date.');
        Assert.areEqual(1, granted.get('myPlans'), 'The user\'s plan is listed.');
        Assert.areEqual(1, granted.get('plans'), 'Progress counts the plan.');
        Assert.isFalse((Boolean) granted.get('progressUnavailable'), 'Progress is a measurement.');
        Assert.isFalse((Boolean) granted.get('promisesUnavailable'), 'Payment promises were read (empty, not unavailable).');
        Assert.areEqual(new Map<String, String>{
            RLM_CollectionsDashboardController.UNAVAILABLE_DEBIT_MEMOS => RLM_CollectionsDashboardController.REASON_REFUSED
        }, granted.get('unavailableReason'), 'The debit memos are refused (no access), not a failure.');
        Assert.areEqual(new List<String>{ RLM_CollectionsDashboardController.UNAVAILABLE_DEBIT_MEMOS },
            granted.get('unavailable'), 'Only debit memos are unavailable to this user.');
        Map<String, Object> debitRow = (Map<String, Object>) granted.get('debitRow');
        Assert.areEqual('Debit Memos', debitRow.get('label'));
        Assert.isNull(debitRow.get('amount'), 'Not a zero: the debit memo read was refused.');
        Assert.areEqual(RLM_CollectionsDashboardController.UNAVAILABLE_DEBIT_MEMOS, debitRow.get('unavailable'));

        Assert.areEqual(dashboardReads, refusedWithoutSet, 'Without the set each of these reads is refused.');
        Assert.isNull(control.get('payments'), 'The refused payment read is unavailable, not zero.');
        Assert.isTrue((Boolean) control.get('tasksUnavailable'), 'The refused task read is unavailable, not "no tasks".');
        Assert.isNull(control.get('myPlans'), 'The refused plan field read is unavailable, not "no plans".');
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_REFUSED, control.get('tasksReason'), 'A refusal.');
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_REFUSED, control.get('myPlansReason'), 'A refusal.');
        Assert.isFalse((Boolean) granted.get('tasksUnavailable'), 'With the set the tasks are read.');
        Assert.isTrue(((List<String>) granted.get('worklistUnavailable')).isEmpty(),
            'With the set every worklist tab is read: ' + granted.get('worklistUnavailable'));
        Assert.isTrue(((List<String>) control.get('unavailable')).contains(
            RLM_CollectionsDashboardController.UNAVAILABLE_PAYMENTS), 'And listed as unavailable.');
    }

    // Calls every section the dashboard loads, as the running user, and keeps what the test checks.
    private static Map<String, Object> dashboardFor(Id accountId) {
        RLM_CollectionsDashboardController.CollectionsDashboardData cards =
            RLM_CollectionsDashboardController.getDashboardCards(null, null);
        RLM_CollectionsDashboardController.WorklistData worklist =
            RLM_CollectionsDashboardController.getWorklist(null, null);
        RLM_CollectionsDashboardController.CpTaskList tasks = RLM_CollectionsDashboardController.getCollectionPlanTasks(accountId);
        RLM_CollectionsDashboardController.MyCollectionPlanList myPlans = RLM_CollectionsDashboardController.getMyCollectionPlans();
        RLM_CollectionsDashboardController.PaymentPromiseSummary promises = RLM_CollectionsDashboardController.getPaymentPromiseSummary(null, null);
        RLM_CollectionsDashboardController.WorklistItem disputedRow = byAccount(worklist.disputedInvoices).get(accountId);
        RLM_CollectionsDashboardController.CollectionsProgressData progress =
            RLM_CollectionsDashboardController.getCollectionsProgress();
        return new Map<String, Object>{
            'accounts' => RLM_CollectionsDashboardController.getAccountOptions().options,
            'currencies' => RLM_CollectionsDashboardController.getCurrencyOptions(),
            'payments' => cards.unappliedPaymentCount,
            'unavailable' => cards.unavailable,
            'debitRow' => cards.totalBalanceBreakdown[1],
            'disputed' => disputedRow == null ? 0 : 1,
            // An unavailable list is a refused read, not an empty one.
            'taskDate' => tasks.unavailable || tasks.items.isEmpty() ? null : tasks.items[0].activityDate,
            'tasksUnavailable' => tasks.unavailable,
            'tasksReason' => tasks.unavailableReason,
            'myPlans' => myPlans.unavailable ? null : myPlans.items.size(),
            'myPlansReason' => myPlans.unavailableReason,
            'unavailableReason' => cards.unavailableReason,
            'worklistUnavailable' => worklist.unavailable,
            'plans' => progress.totalPlans,
            'progressUnavailable' => progress.unavailable,
            'promisesUnavailable' => promises.unavailable
        };
    }

    // A payment count that could not be read leaves the payment balance in the total and the breakdown:
    // only the count is unavailable, so the page shows the count as "—" and nothing else changes.
    @isTest
    static void totalUp_aCountOnlyFailureKeepsThePaymentBalanceInTheTotal() {
        RLM_CollectionsDashboardController.CollectionsDashboardData data =
            new RLM_CollectionsDashboardController.CollectionsDashboardData();
        data.unavailable.add(RLM_CollectionsDashboardController.UNAVAILABLE_PAYMENT_COUNT);
        RLM_CollectionsDashboardController.totalUp(data, 100, 0, 0, 20, null);

        Assert.areEqual(80, data.totalBalance, 'Invoices less the unapplied payment balance, which was read.');
        Assert.areEqual(80, data.totalOutstanding, 'Total outstanding still uses the balance.');
        Assert.areEqual(20, data.unappliedPaymentBalance, 'The balance is shown.');
        Assert.isNull(data.unappliedPaymentCount, 'Only the count is unavailable.');
        Map<String, Object> paymentsRow = data.totalBalanceBreakdown[3];
        Assert.areEqual(-20, paymentsRow.get('amount'), 'The payments row keeps its amount.');
        Assert.isFalse(paymentsRow.containsKey('unavailable'), 'And is not marked unavailable.');

        RLM_CollectionsDashboardController.CollectionsDashboardData noInvoices =
            new RLM_CollectionsDashboardController.CollectionsDashboardData();
        RLM_CollectionsDashboardController.totalUp(noInvoices, null, 0, 0, 20, 1);
        Assert.isNull(noInvoices.totalBalance, 'No total without the unpaid invoices, its main component.');
        Assert.isNull(noInvoices.totalOutstanding, 'Nor a total outstanding.');

        RLM_CollectionsDashboardController.CollectionsDashboardData noBalance =
            new RLM_CollectionsDashboardController.CollectionsDashboardData();
        RLM_CollectionsDashboardController.totalUp(noBalance, 100, 0, 0, null, 3);
        Assert.areEqual(100, noBalance.totalBalance, 'A refused balance is left out of the total.');
        Assert.isNull(noBalance.totalOutstanding, 'And there is no total outstanding without it.');
        Assert.areEqual(RLM_CollectionsDashboardController.UNAVAILABLE_PAYMENTS,
            noBalance.totalBalanceBreakdown[3].get('unavailable'), 'Its row is marked unavailable.');
    }

    // A refused read sends the user to an administrator, a failure to a retry: the two must not be
    // confused. The refusal messages are the ones a USER_MODE read throws (measured on 264).
    @isTest
    static void reasonFor_tellsARefusalFromAFailure() {
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_REFUSED, RLM_CollectionsDashboardController.reasonFor(
            new QueryException('sObject type \'DebitMemo\' is not supported. If you are attempting to use a custom object...')),
            'An object the user cannot read.');
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_REFUSED, RLM_CollectionsDashboardController.reasonFor(
            new QueryException('No such column \'ActivityDate\' on entity \'Task\'. If you are attempting...')),
            'A field the user cannot read.');
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_REFUSED, RLM_CollectionsDashboardController.reasonFor(
            new NoAccessException()), 'A NoAccessException.');
        // A dynamic query's error can echo the query before the column message.
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_REFUSED, RLM_CollectionsDashboardController.reasonFor(
            new QueryException('\nSELECT ActivityDate FROM Task\n       ^\nERROR at Row:1:Column:8\n'
                + 'No such column \'ActivityDate\' on entity \'Task\'. If you are attempting...')),
            'The column message is found after an echoed query.');
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_FAILED, RLM_CollectionsDashboardController.reasonFor(
            new QueryException('\nSELECT NotAField__x FROM Payment\n^\nERROR at Row:1:Column:8\n'
                + 'No such column \'NotAField__x\' on entity \'Payment\'.')),
            'An absent field after an echoed query is still a failure.');
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_TOO_MANY, RLM_CollectionsDashboardController.reasonFor(
            new RLM_CollectionsDashboardController.TooManyRowsException('More than 10000 invoices')),
            'Too many rows to total is its own reason.');
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_FAILED, RLM_CollectionsDashboardController.reasonFor(
            new QueryException('No such column \'NotAField__x\' on entity \'Payment\'. If you are attempting...')),
            'A field the org does not have (a single-currency org\'s CurrencyIsoCode) is a failure, not a refusal.');
        Assert.isTrue(RLM_CollectionsDashboardController.fieldExists('Task', 'ActivityDate'), 'PRECONDITION: the field exists.');
        Assert.isFalse(RLM_CollectionsDashboardController.fieldExists('Payment', 'NotAField__x'), 'And this one does not.');
        Assert.isFalse(RLM_CollectionsDashboardController.fieldExists('NotAnObject__x', 'Name'), 'Nor this object.');
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_FAILED, RLM_CollectionsDashboardController.reasonFor(
            new QueryException('Non-selective query against large object type')), 'Any other query error is a failure.');
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_FAILED, RLM_CollectionsDashboardController.reasonFor(
            new LimitException('Too many SOQL queries')), 'A limit is a failure.');
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_FAILED, RLM_CollectionsDashboardController.reasonFor(
            new CalloutException('timeout')), 'So is any other exception.');
    }

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

        List<Map<String, String>> accountOptions = RLM_CollectionsDashboardController.getAccountOptions().options;
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
    // schedule drive the SUM(RequestedAmount)/COUNT(Id) GROUP BY Status path; a third Draft item
    // on another account shows the account filter leaves it out.
    // A grouped SUM comes back in the corporate currency, so the items are created in it.
    @isTest
    static void getPaymentPromiseSummary_withSeededItems_aggregatesByStatus() {
        Account acc = new Account(Name = 'RLM Promise Summary Test');
        Account other = new Account(Name = 'RLM Promise Summary Other');
        insert new List<Account>{ acc, other };
        String corporate = corporateCurrency();
        PaymentSchedule ps = new PaymentSchedule(Status = 'Draft', TotalRequestedAmount = 190, CurrencyIsoCode = corporate);
        insert ps;
        insert new List<PaymentScheduleItem>{
            new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id, CurrencyIsoCode = corporate,
                RequestedAmount = 100, TargetPaymentProcessingDate = Date.today(), Status = 'Draft'),
            new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id, CurrencyIsoCode = corporate,
                RequestedAmount = 50, TargetPaymentProcessingDate = Date.today(), Status = 'Draft'),
            new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = other.Id, CurrencyIsoCode = corporate,
                RequestedAmount = 40, TargetPaymentProcessingDate = Date.today(), Status = 'Draft')
        };

        Test.startTest();
        Map<String, RLM_CollectionsDashboardController.PaymentPromiseBucket> unfiltered =
            bucketsByStatus(RLM_CollectionsDashboardController.getPaymentPromiseSummary(null, null));
        Map<String, RLM_CollectionsDashboardController.PaymentPromiseBucket> byAccount =
            bucketsByStatus(RLM_CollectionsDashboardController.getPaymentPromiseSummary(acc.Id, null));
        Test.stopTest();

        // The summary always returns all four buckets in fixed order.
        System.assertEquals(4, unfiltered.size(), 'Failed/Ready/Draft/Processing buckets are always present.');
        assertAmount(190, unfiltered.get('Draft').totalRequestedAmount,
            'Three Draft items of 100 + 50 + 40 sum to 190.');
        System.assertEquals(3, unfiltered.get('Draft').itemCount, 'All three Draft items counted.');
        assertAmount(0, unfiltered.get('Failed').totalRequestedAmount, 'No Failed items seeded.');

        assertAmount(150, byAccount.get('Draft').totalRequestedAmount,
            'The account filter keeps the account\'s two items (100 + 50), not the other account\'s 40.');
        System.assertEquals(2, byAccount.get('Draft').itemCount, 'Only the account\'s two items are counted.');
    }

    // The currency filter: an item in the corporate currency is summed under that currency and
    // left out under any other; with the account filter too, another account's item in the same
    // currency is left out. The SUM is grouped by Status, so it comes back in the corporate
    // currency whoever runs it, and the items are created in it.
    @isTest
    static void getPaymentPromiseSummary_appliesTheCurrencyFilter() {
        Account acc = newAccount('RLM CD Promise Currency');
        Account other = newAccount('RLM CD Promise Currency Other');
        String itemCurrency = corporateCurrency();
        String otherCurrency = anotherCurrency(itemCurrency);
        PaymentSchedule ps = new PaymentSchedule(Status = 'Draft', TotalRequestedAmount = 170, CurrencyIsoCode = itemCurrency);
        insert ps;
        PaymentScheduleItem psi = new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id,
            CurrencyIsoCode = itemCurrency, RequestedAmount = 100, TargetPaymentProcessingDate = Date.today(),
            Status = 'Draft');
        PaymentScheduleItem otherItem = new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = other.Id,
            CurrencyIsoCode = itemCurrency, RequestedAmount = 70, TargetPaymentProcessingDate = Date.today(),
            Status = 'Draft');
        insert new List<PaymentScheduleItem>{ psi, otherItem };
        Assert.areEqual(itemCurrency, [SELECT CurrencyIsoCode FROM PaymentScheduleItem WHERE Id = :psi.Id].CurrencyIsoCode,
            'PRECONDITION: the item is in the corporate currency.');

        Test.startTest();
        Map<String, RLM_CollectionsDashboardController.PaymentPromiseBucket> sameCurrency =
            bucketsByStatus(RLM_CollectionsDashboardController.getPaymentPromiseSummary(acc.Id, itemCurrency));
        Map<String, RLM_CollectionsDashboardController.PaymentPromiseBucket> currencyOnly =
            bucketsByStatus(RLM_CollectionsDashboardController.getPaymentPromiseSummary(null, itemCurrency));
        Map<String, RLM_CollectionsDashboardController.PaymentPromiseBucket> elsewhere =
            bucketsByStatus(RLM_CollectionsDashboardController.getPaymentPromiseSummary(acc.Id, otherCurrency));
        Test.stopTest();

        assertAmount(100, sameCurrency.get('Draft').totalRequestedAmount,
            'The account\'s item is in ' + itemCurrency + ', so both filters keep it and leave the other account\'s out.');
        Assert.areEqual(1, sameCurrency.get('Draft').itemCount, 'One Draft item for the account in ' + itemCurrency + '.');
        assertAmount(170, currencyOnly.get('Draft').totalRequestedAmount,
            'The currency filter alone keeps both accounts\' items (100 + 70).');
        Assert.areEqual(2, currencyOnly.get('Draft').itemCount, 'Both items are in ' + itemCurrency + '.');
        Assert.areEqual(4, elsewhere.size(), 'All four buckets are returned even when nothing matches.');
        assertAmount(0, elsewhere.get('Draft').totalRequestedAmount,
            'Another currency (' + otherCurrency + ') leaves the item out.');
        Assert.areEqual(0, elsewhere.get('Draft').itemCount, 'No item in another currency.');
    }

    @isTest
    static void optionLists_listAccountsByNameAndActiveCurrenciesCorporateFirst() {
        Account zeta = newAccount('RLM CD Zeta');
        Account alpha = newAccount('RLM CD Alpha');
        // The controller lists CurrencyType, so this module only deploys to a multi-currency org.
        String corporate = corporateCurrency();
        Integer activeCurrencies = [SELECT COUNT() FROM CurrencyType WHERE IsActive = true];

        Test.startTest();
        List<Map<String, String>> accounts = RLM_CollectionsDashboardController.getAccountOptions().options;
        List<Map<String, String>> currencies = RLM_CollectionsDashboardController.getCurrencyOptions();
        Test.stopTest();

        Assert.areEqual(3, accounts.size(), 'The sentinel plus the two accounts.');
        Assert.areEqual('', accounts[0].get('value'), 'The sentinel has a blank value.');
        Assert.areEqual('All Accounts', accounts[0].get('label'), 'The sentinel comes first.');
        Assert.areEqual(String.valueOf(alpha.Id), accounts[1].get('value'), 'Accounts are sorted by name.');
        Assert.areEqual('RLM CD Alpha', accounts[1].get('label'), 'The label is the account name.');
        Assert.areEqual(String.valueOf(zeta.Id), accounts[2].get('value'), 'Zeta sorts after Alpha.');

        Assert.areEqual(activeCurrencies + 1, currencies.size(), 'The sentinel plus every active currency.');
        Assert.areEqual('All Currencies', currencies[0].get('label'), 'The sentinel comes first.');
        Assert.areEqual(corporate, currencies[1].get('value'), 'The corporate currency follows the sentinel.');
    }

    // A Sale payment with a balance is an unapplied payment: it is counted and filtered by account
    // and currency like every card (always checked). The balance checks -- the unapplied balance,
    // the lower total balance and total outstanding, and the filtered balances -- compare ungrouped
    // SUMs, so they run only when the running user's currency is the corporate one (see
    // userCurrencyIsCorporate), and are skipped with a warning otherwise.
    @isTest
    static void getDashboardCards_unappliedPaymentIsCountedAndFiltered_balancesWhenTheUserCurrencyIsCorporate() {
        Account payer = newAccount('RLM CD Payer');
        Account other = newAccount('RLM CD Other');
        String paymentCurrency = corporateCurrency();
        Payment p = new Payment(AccountId = payer.Id, Amount = 250, Status = 'Processed',
            Type = 'Sale', ProcessingMode = 'External', CurrencyIsoCode = paymentCurrency);
        insert p;
        // Balance is maintained by the platform; only a positive balance is unapplied.
        Decimal expected = [SELECT Balance FROM Payment WHERE Id = :p.Id].Balance;
        Assert.isTrue(expected != null && expected > 0,
            'PRECONDITION: a new processed payment carries a positive balance. Got ' + expected);
        String otherCurrency = anotherCurrency(paymentCurrency);
        Assert.areEqual(paymentCurrency, [SELECT CurrencyIsoCode FROM Payment WHERE Id = :p.Id].CurrencyIsoCode,
            'PRECONDITION: the payment is in the corporate currency.');

        Test.startTest();
        RLM_CollectionsDashboardController.CollectionsDashboardData unfiltered =
            RLM_CollectionsDashboardController.getDashboardCards(null, null);
        RLM_CollectionsDashboardController.CollectionsDashboardData payerInCurrency =
            RLM_CollectionsDashboardController.getDashboardCards(payer.Id, paymentCurrency);
        RLM_CollectionsDashboardController.CollectionsDashboardData otherAccount =
            RLM_CollectionsDashboardController.getDashboardCards(other.Id, null);
        RLM_CollectionsDashboardController.CollectionsDashboardData payerElsewhere =
            RLM_CollectionsDashboardController.getDashboardCards(payer.Id, otherCurrency);
        Test.stopTest();

        Assert.areEqual(1, unfiltered.unappliedPaymentCount, 'The payment is counted when it has a balance.');
        Assert.isTrue(unfiltered.unavailable.isEmpty(), 'The admin reads every component: ' + unfiltered.unavailable);
        for (Map<String, Object> row : unfiltered.totalBalanceBreakdown) {
            Assert.isNotNull(row.get('amount'), 'A readable component has an amount, zero or not: ' + row.get('label'));
            Assert.isFalse(row.containsKey('unavailable'), 'And is not marked unavailable: ' + row.get('label'));
        }

        List<String> labels = new List<String>{ 'Unpaid Invoices', 'Debit Memos', 'Unapplied Credits', 'Unapplied Payments' };
        Assert.areEqual(labels.size(), unfiltered.totalBalanceBreakdown.size(), 'One breakdown row per balance component.');
        for (Integer i = 0; i < labels.size(); i++) {
            Assert.areEqual(labels[i], unfiltered.totalBalanceBreakdown[i].get('label'), 'Breakdown order, row ' + i);
        }

        List<String> agingKeys = new List<String>{ 'current', '1-30', '31-60', '61-90', '90+' };
        // Bucket and invoice amounts are not asserted here: no invoice can exist in a unit test, so
        // they are zero whatever the controller does. They are checked from invoice rows in
        // tallyInvoices_bucketsByDaysPastDueAndSplitsBySettlement.
        Assert.areEqual(agingKeys.size(), unfiltered.agingBuckets.size(), 'Five aging buckets.');
        for (Integer i = 0; i < agingKeys.size(); i++) {
            Assert.areEqual(agingKeys[i], unfiltered.agingBuckets[i].get('key'), 'Aging bucket order, bucket ' + i);
        }

        Assert.areEqual(1, payerInCurrency.unappliedPaymentCount,
            'The payer\'s own payment, in its own currency, is kept by both filters.');
        Assert.areEqual(4, otherAccount.totalBalanceBreakdown.size(), 'The cards were built, not returned early.');
        Assert.areEqual(4, payerElsewhere.totalBalanceBreakdown.size(), 'The cards were built, not returned early.');
        Assert.areEqual(0, otherAccount.unappliedPaymentCount, 'Another account\'s payment is not counted.');
        Assert.areEqual(0, payerElsewhere.unappliedPaymentCount,
            'A payment in ' + paymentCurrency + ' is not counted under ' + otherCurrency + '.');

        if (userCurrencyIsCorporate()) {
            assertAmount(expected, unfiltered.unappliedPaymentBalance, 'The payment balance is unapplied.');
            assertAmount(-expected, unfiltered.totalBalance, 'Total balance = invoices + debit memos - credits - payments.');
            assertAmount(-expected, unfiltered.totalOutstanding, 'Total outstanding = invoices - unapplied payments.');
            assertAmount(-expected, (Decimal) unfiltered.totalBalanceBreakdown[3].get('amount'),
                'Unapplied payments are shown as a reduction.');
            assertAmount(expected, payerInCurrency.unappliedPaymentBalance,
                'The payer\'s own payment balance passes both filters.');
            assertAmount(0, otherAccount.unappliedPaymentBalance, 'Another account\'s payment is filtered out.');
            assertAmount(0, payerElsewhere.unappliedPaymentBalance,
                'A payment in ' + paymentCurrency + ' is filtered out under ' + otherCurrency + '.');
        }
    }

    // Only a Processed payment's balance is unapplied. A Canceled, Draft, Pending or Failed payment
    // keeps its Balance but is not money to apply, so it is neither counted nor summed.
    @isTest
    static void getDashboardCards_onlyProcessedPaymentsAreUnapplied() {
        Account payer = newAccount('RLM CD Status Payer');
        String paymentCurrency = corporateCurrency();
        Payment kept = payment(payer.Id, 250, 'Processed', paymentCurrency);
        Payment canceled = payment(payer.Id, 100, 'Processed', paymentCurrency);
        List<Payment> others = new List<Payment>{
            payment(payer.Id, 30, 'Draft', paymentCurrency),
            payment(payer.Id, 40, 'Pending', paymentCurrency),
            payment(payer.Id, 50, 'Failed', paymentCurrency)
        };
        List<Payment> all = new List<Payment>{ kept, canceled };
        all.addAll(others);
        insert all;
        update new Payment(Id = canceled.Id, Status = 'Canceled');
        Set<Id> ids = new Map<Id, Payment>(all).keySet();
        for (Payment p : [SELECT Status, Balance FROM Payment WHERE Id IN :ids AND Id != :kept.Id]) {
            Assert.isTrue(p.Balance != null && p.Balance > 0,
                'PRECONDITION: a ' + p.Status + ' payment keeps a positive balance. Got ' + p.Balance);
        }
        Decimal expected = [SELECT Balance FROM Payment WHERE Id = :kept.Id].Balance;

        Test.startTest();
        RLM_CollectionsDashboardController.CollectionsDashboardData cards =
            RLM_CollectionsDashboardController.getDashboardCards(payer.Id, null);
        Test.stopTest();

        Assert.areEqual(1, cards.unappliedPaymentCount, 'Only the Processed payment is counted');
        if (userCurrencyIsCorporate()) {
            assertAmount(expected, cards.unappliedPaymentBalance, 'Only the Processed payment\'s balance is unapplied');
        }
    }

    private static Payment payment(Id accountId, Decimal amount, String status, String currencyCode) {
        return new Payment(AccountId = accountId, Amount = amount, Status = status,
            Type = 'Sale', ProcessingMode = 'External', CurrencyIsoCode = currencyCode);
    }

    // A Draft debit memo is not owed: only a posted memo not yet on a posted invoice counts.
    // The memo has a total and is on the filtered account, so its Draft status is what keeps it
    // out. A unit test cannot post one (its lines need a tax treatment), so the posted sum is
    // live-only.
    @isTest
    static void getDashboardCards_draftDebitMemoIsNotOwed() {
        Account a = newAccount('RLM CD Debit Memo');
        // The controller filters on BillToAccountId when DebitMemo has it, else on AccountId.
        String accountField = Schema.getGlobalDescribe().get('DebitMemo').getDescribe().fields.getMap()
            .containsKey('billtoaccountid') ? 'BillToAccountId' : 'AccountId';
        Map<String, Object> memoValues = new Map<String, Object>{
            'AccountId' => a.Id, 'Status' => 'Draft', 'InvoiceGenerationStatus' => 'None'
        };
        memoValues.put(accountField, a.Id);
        SObject memo = newRecord('DebitMemo', memoValues);
        newRecord('DebitMemoLine', new Map<String, Object>{
            'Name' => 'RLM CD Debit Memo Line', 'DebitMemoId' => memo.Id, 'ChargeAmount' => 10
        });
        Id memoId = memo.Id;
        SObject saved = Database.query('SELECT TotalAmount, Status FROM DebitMemo WHERE Id = :memoId')[0];
        Decimal memoTotal = (Decimal) saved.get('TotalAmount');
        Assert.isTrue(memoTotal != null && memoTotal > 0,
            'PRECONDITION: the Draft memo totals its line. Got ' + memoTotal);
        Assert.areEqual('Draft', saved.get('Status'), 'PRECONDITION: the memo is Draft.');
        // The controller's own aggregate, in user mode, with Status = 'Draft' in place of
        // 'Posted': the SUM runs and returns a positive total for the memo, so the controller's
        // query is not refused and its zero comes from the Status filter, not from a swallowed
        // error. Only the sign is checked, so the currency the SUM reports in does not matter.
        Id aId = a.Id;
        List<AggregateResult> control = Database.query(
            'SELECT SUM(TotalAmount) s FROM DebitMemo WHERE TotalAmount != null AND Status = \'Draft\''
            + ' AND InvoiceGenerationStatus != \'Posted Invoice Generated\' AND ' + accountField + ' = :aId',
            AccessLevel.USER_MODE);
        Decimal controlSum = (Decimal) control[0].get('s');
        Assert.isTrue(controlSum != null && controlSum > 0,
            'PRECONDITION: with Status = Draft, the controller\'s aggregate sums the memo. Got ' + controlSum);

        Test.startTest();
        RLM_CollectionsDashboardController.CollectionsDashboardData cards =
            RLM_CollectionsDashboardController.getDashboardCards(a.Id, null);
        Test.stopTest();

        Assert.areEqual(4, cards.totalBalanceBreakdown.size(), 'The cards were built, not returned early.');
        Assert.areEqual('Debit Memos', cards.totalBalanceBreakdown[1].get('label'), 'Second breakdown row.');
        assertAmount(0, (Decimal) cards.totalBalanceBreakdown[1].get('amount'), 'A Draft debit memo is not owed.');
        assertAmount(0, cards.totalBalance, 'Nothing is owed on the account.');
    }

    // Open cases are the disputed rows: one per account, carrying the newest case and a reason
    // built from its subject, description (cut at 200 characters) and Reason. With no invoices the
    // other two tabs were read and have no rows, and nothing is unavailable.
    @isTest
    static void getWorklist_openCasesListTheirAccountsAsDisputed() {
        Account c = newAccount('RLM CD Worklist C');
        Account a = newAccount('RLM CD Worklist A');
        Account b = newAccount('RLM CD Worklist B');
        String longDescription = 'x'.repeat(250);
        Case caseA = new Case(AccountId = a.Id, Subject = 'Invoice disputed', Description = longDescription,
            Reason = firstActivePicklistValue(Case.Reason));
        Case caseB = new Case(AccountId = b.Id, Description = 'Short note');
        Case caseC = new Case(AccountId = c.Id);
        // An older open case on account A, inserted first so only the CreatedDate ordering can
        // make the row carry the newer one.
        Case olderA = new Case(AccountId = a.Id, Subject = 'Older case on A');
        insert olderA;
        Test.setCreatedDate(olderA.Id, Datetime.now().addDays(-5));
        insert new List<Case>{ caseA, caseB, caseC };
        // Read back: CaseNumber is assigned on insert, and the org may default Reason.
        List<Id> caseIds = new List<Id>{ caseA.Id, caseB.Id, caseC.Id };
        Map<Id, Case> saved = new Map<Id, Case>([SELECT Id, CaseNumber, Reason FROM Case WHERE Id IN :caseIds]);
        String expectedA = 'Invoice disputed' + SUBJECT_SEPARATOR + longDescription.substring(0, 200) + '...'
            + reasonSuffix(saved.get(caseA.Id));
        String expectedB = 'Short note' + reasonSuffix(saved.get(caseB.Id));
        String expectedC = saved.get(caseC.Id).Reason != null ? saved.get(caseC.Id).Reason : 'Open case';

        Test.startTest();
        RLM_CollectionsDashboardController.WorklistData unfiltered =
            RLM_CollectionsDashboardController.getWorklist(null, null);
        RLM_CollectionsDashboardController.WorklistData onlyB =
            RLM_CollectionsDashboardController.getWorklist(b.Id, UserInfo.getDefaultCurrency());
        Test.stopTest();

        Assert.areEqual(3, unfiltered.disputedInvoices.size(),
            'One disputed row per account with an open case, not one per case.');
        Map<Id, RLM_CollectionsDashboardController.WorklistItem> disputed = byAccount(unfiltered.disputedInvoices);
        Assert.areEqual(3, disputed.size(), 'Each row is a different account.');

        RLM_CollectionsDashboardController.WorklistItem rowA = disputed.get(a.Id);
        Assert.areEqual(expectedA, rowA.disputeReason, 'Subject, description cut at 200, then the Reason.');
        Assert.areEqual(caseA.Id, rowA.caseId, 'The row links the newest case, not the older one.');
        Assert.areEqual(saved.get(caseA.Id).CaseNumber, rowA.caseNumber, 'The row shows the case number.');
        Assert.areEqual('RLM CD Worklist A', rowA.accountName, 'The row names the account.');
        Assert.areEqual('disputed', rowA.segment, 'Disputed segment.');
        Assert.areEqual('amber', rowA.healthScore, 'Disputed rows are amber.');
        Assert.areEqual(expectedB, disputed.get(b.Id).disputeReason, 'A description alone is the reason.');
        Assert.areEqual(expectedC, disputed.get(c.Id).disputeReason, 'A case with no text reads as an open case.');

        // A tab that was read and has no rows stays empty; the page says "No items in this view".
        Assert.isTrue(unfiltered.criticalFollowUpInvoices.isEmpty(), 'No invoices: no critical rows.');
        Assert.isTrue(unfiltered.highValueDelinquents.isEmpty(), 'No invoices: no high-value rows.');
        Assert.isTrue(unfiltered.unavailable.isEmpty(), 'Every tab was read: ' + unfiltered.unavailable);

        Assert.areEqual(1, onlyB.disputedInvoices.size(), 'The account filter keeps only that account\'s case.');
        Assert.areEqual(b.Id, onlyB.disputedInvoices[0].accountId, 'The filtered row is account B.');
        Assert.isTrue(onlyB.highValueDelinquents.isEmpty(), 'No rows from other accounts under the filter.');
    }

    // With no records at all every tab is read and has no rows: none is unavailable.
    @isTest
    static void getWorklist_withNoRecords_readsEveryTabWithNoRows() {
        Test.startTest();
        RLM_CollectionsDashboardController.WorklistData wl = RLM_CollectionsDashboardController.getWorklist(null, null);
        Test.stopTest();

        Assert.isTrue(wl.criticalFollowUpInvoices.isEmpty(), 'No invoices, no critical rows.');
        Assert.isTrue(wl.highValueDelinquents.isEmpty(), 'No invoices, no high-value rows.');
        Assert.isTrue(wl.disputedInvoices.isEmpty(), 'No cases, no disputed rows.');
        Assert.isTrue(wl.unavailable.isEmpty(), 'Empty is not unavailable: ' + wl.unavailable);
    }

    @isTest
    static void getMyCollectionPlans_listsTheUsersPlansByDueDate() {
        Account a = newAccount('RLM CD Plan Account');
        Account b = newAccount('RLM CD Plan Account B');
        // A Billing plan requires an account.
        CollectionPlan later = newPlan(a.Id, Date.today().addDays(10));
        CollectionPlan sooner = newPlan(b.Id, Date.today().addDays(2));
        insert new List<CollectionPlan>{ later, sooner };

        Test.startTest();
        List<RLM_CollectionsDashboardController.MyCollectionPlanItem> items =
            RLM_CollectionsDashboardController.getMyCollectionPlans().items;
        Test.stopTest();

        Assert.areEqual(2, items.size(), 'Both plans are owned by the running user.');
        Assert.areEqual(sooner.Id, items[0].collectionPlanId, 'The earliest due date comes first.');
        Assert.areEqual(Date.today().addDays(2), items[0].dueDate, 'The due date is carried.');
        Assert.areEqual(b.Id, items[0].accountId, 'Each plan carries its own account.');
        Assert.areEqual('RLM CD Plan Account B', items[0].accountName, 'And that account\'s name.');

        Assert.areEqual(later.Id, items[1].collectionPlanId, 'The later plan comes second.');
        Assert.areEqual(a.Id, items[1].accountId, 'The plan\'s account id.');
        Assert.areEqual('RLM CD Plan Account', items[1].accountName, 'The plan\'s account name.');
        Assert.isTrue(String.isNotBlank(items[1].name) && items[1].name != NO_VALUE, 'The plan\'s autonumber name.');
    }

    // One plan closed six days after it was created, one still open: half recovered, an
    // average of six days to close, and the average of the two plans' days past due.
    @isTest
    static void getCollectionsProgress_splitsClosedAndOpenPlans() {
        Account a = newAccount('RLM CD Progress');
        CollectionPlan closedPlan = newPlan(a.Id, Date.today().addDays(-20));
        closedPlan.ClosedDate = Date.today();
        closedPlan.DaysPastDue = 10;
        CollectionPlan openPlan = newPlan(a.Id, Date.today().addDays(-30));
        openPlan.DaysPastDue = 20;
        insert new List<CollectionPlan>{ closedPlan, openPlan };
        // Local noon, so the date part is six days back whatever the time zone or time of day.
        Test.setCreatedDate(closedPlan.Id, Datetime.newInstance(Date.today().addDays(-6), Time.newInstance(12, 0, 0, 0)));

        Test.startTest();
        RLM_CollectionsDashboardController.CollectionsProgressData progress =
            RLM_CollectionsDashboardController.getCollectionsProgress();
        Test.stopTest();

        Assert.areEqual(2, progress.totalPlans, 'Two plans.');
        Assert.areEqual(1, progress.recoveredCount, 'A plan with a closed date is recovered.');
        Assert.areEqual(1, progress.notRecoveredCount, 'The open plan is not.');
        assertAmount(50, progress.recoveredPercent, 'One of two plans recovered.');
        assertAmount(50, progress.notRecoveredPercent, 'One of two plans open.');
        assertAmount(6, progress.avgDaysToClose, 'Created six days before it closed.');
        assertAmount(15, progress.avgDaysPastDue, 'The average of 10 and 20 days past due.');
    }

    @isTest
    static void getCollectionPlanTasks_returnsTasksOnTheAccountsPlans() {
        Account a = newAccount('RLM CD Tasks A');
        Account b = newAccount('RLM CD Tasks B');
        CollectionPlan planA = newPlan(a.Id, Date.today());
        CollectionPlan planB = newPlan(b.Id, Date.today());
        insert new List<CollectionPlan>{ planA, planB };
        Task taskA = new Task(WhatId = planA.Id, Subject = 'Call about the plan', ActivityDate = Date.today().addDays(1));
        Task taskB = new Task(WhatId = planB.Id, Subject = 'Send a reminder', ActivityDate = Date.today());
        // Task A is due later but inserted last and back-dated, so neither insertion order nor
        // CreatedDate puts it first: only the ActivityDate ordering does.
        insert taskB;
        insert taskA;
        Test.setCreatedDate(taskA.Id, Datetime.now().addDays(-3));

        Test.startTest();
        List<RLM_CollectionsDashboardController.CpTaskItem> forA =
            RLM_CollectionsDashboardController.getCollectionPlanTasks(a.Id).items;
        List<RLM_CollectionsDashboardController.CpTaskItem> forAll =
            RLM_CollectionsDashboardController.getCollectionPlanTasks(null).items;
        Test.stopTest();

        Assert.areEqual(1, forA.size(), 'Only the task on account A\'s plan.');
        Assert.areEqual(taskA.Id, forA[0].taskId, 'The task id.');
        Assert.areEqual(planA.Id, forA[0].collectionPlanId, 'The task\'s plan.');
        Assert.areEqual('Call about the plan', forA[0].subject, 'The task subject.');
        Assert.areEqual(Date.today().addDays(1), forA[0].activityDate, 'The task due date.');
        Assert.isTrue(String.isNotBlank(forA[0].status), 'Status defaults on insert.');

        Assert.areEqual(2, forAll.size(), 'Without an account filter, every plan\'s tasks.');
        Assert.areEqual(taskA.Id, forAll[0].taskId, 'The latest activity date comes first.');
    }

    // A user who cannot read the billing objects gets every section unavailable as refused, not an
    // error and not an empty "none": each section catches its own refusal. The same records give the
    // admin a populated dashboard, so the refusals are what the user sees in place of data.
    @isTest
    static void allSections_forAUserWhoCannotReadThem_areUnavailableAsRefused() {
        User noAccess = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        Account a = newAccount('RLM CD Unreadable');
        CollectionPlan plan = newPlan(a.Id, Date.today());
        insert plan;
        insert new Task(WhatId = plan.Id, Subject = 'RLM CD unreadable task');
        insert new Case(AccountId = a.Id, Subject = 'RLM CD unreadable case');
        PaymentSchedule ps = new PaymentSchedule(Status = 'Draft', TotalRequestedAmount = 10);
        insert ps;
        insert new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = a.Id,
            RequestedAmount = 10, TargetPaymentProcessingDate = Date.today(), Status = 'Draft');

        // The admin's view of the same data: the cards are built (Invoice is readable), and the
        // open case, the plan's task, the plan and the schedule item all show.
        Assert.areEqual(4, RLM_CollectionsDashboardController.getDashboardCards(null, null).totalBalanceBreakdown.size(),
            'PRECONDITION: the admin gets the full breakdown.');
        RLM_CollectionsDashboardController.WorklistData adminWorklist =
            RLM_CollectionsDashboardController.getWorklist(null, null);
        Assert.areEqual(1, adminWorklist.disputedInvoices.size(), 'PRECONDITION: the admin sees the open case.');
        Assert.isTrue(adminWorklist.unavailable.isEmpty(), 'PRECONDITION: the admin reads every worklist tab.');
        Assert.areEqual(1, RLM_CollectionsDashboardController.getCollectionPlanTasks(null).items.size(),
            'PRECONDITION: the admin sees the plan\'s task.');
        Assert.areEqual(1, RLM_CollectionsDashboardController.getCollectionsProgress().totalPlans,
            'PRECONDITION: the admin measures the plan.');
        Assert.areEqual(1, RLM_CollectionsDashboardController.getMyCollectionPlans().items.size(),
            'PRECONDITION: the admin lists the plan they own.');
        Assert.areEqual(1, bucketsByStatus(RLM_CollectionsDashboardController.getPaymentPromiseSummary(null, null))
            .get('Draft').itemCount, 'PRECONDITION: the admin sees the schedule item.');

        List<String> readable = new List<String>();
        RLM_CollectionsDashboardController.CollectionsDashboardData cards;
        RLM_CollectionsDashboardController.WorklistData worklist;
        RLM_CollectionsDashboardController.PaymentPromiseSummary promises;
        RLM_CollectionsDashboardController.CpTaskList tasks;
        RLM_CollectionsDashboardController.CollectionsProgressData progress;
        RLM_CollectionsDashboardController.MyCollectionPlanList myPlans;
        Test.startTest();
        System.runAs(noAccess) {
            for (String objectName : new List<String>{ 'Account', 'Case', 'CollectionPlan', 'Invoice', 'PaymentScheduleItem' }) {
                if (!userModeQueryFails('SELECT Id FROM ' + objectName + ' LIMIT 1')) {
                    readable.add(objectName);
                }
            }
            cards = RLM_CollectionsDashboardController.getDashboardCards(null, null);
            worklist = RLM_CollectionsDashboardController.getWorklist(null, null);
            promises = RLM_CollectionsDashboardController.getPaymentPromiseSummary(null, null);
            tasks = RLM_CollectionsDashboardController.getCollectionPlanTasks(null);
            progress = RLM_CollectionsDashboardController.getCollectionsProgress();
            myPlans = RLM_CollectionsDashboardController.getMyCollectionPlans();
        }
        Test.stopTest();

        Assert.isTrue(readable.isEmpty(), 'PRECONDITION: the user cannot query ' + readable + ' in user mode.');
        Assert.isTrue(myPlans.unavailable, 'An unreadable plan list is unavailable, not "no plans".');
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_REFUSED, myPlans.unavailableReason, 'A refusal.');
        // Every card component is unavailable, not zero: the page says so instead of showing $0.00.
        Assert.areEqual(new List<String>{
            RLM_CollectionsDashboardController.UNAVAILABLE_INVOICES,
            RLM_CollectionsDashboardController.UNAVAILABLE_CREDITS,
            RLM_CollectionsDashboardController.UNAVAILABLE_DEBIT_MEMOS,
            RLM_CollectionsDashboardController.UNAVAILABLE_PAYMENTS,
            RLM_CollectionsDashboardController.UNAVAILABLE_PAYMENT_COUNT
        }, cards.unavailable, 'Each refused component is listed, in the order it is read.');
        Assert.isNull(cards.receivablesOutstanding, 'Receivables are not a zero.');
        Assert.isNull(cards.invoiceCount, 'Nor the invoice count.');
        Assert.isNull(cards.currentDue, 'Nor current due.');
        Assert.isNull(cards.overdue, 'Nor overdue.');
        Assert.isNull(cards.unappliedPaymentBalance, 'Nor the unapplied payments.');
        Assert.isNull(cards.unappliedPaymentCount, 'Nor their count.');
        Assert.isNull(cards.totalOutstanding, 'Nor the total outstanding.');
        Assert.isNull(cards.totalBalance, 'With nothing read there is no total balance, not a zero.');
        Assert.areEqual(4, cards.totalBalanceBreakdown.size(), 'The breakdown names every component.');
        for (Map<String, Object> row : cards.totalBalanceBreakdown) {
            Assert.isNull(row.get('amount'), 'No amount for ' + row.get('label'));
            Assert.isNotNull(row.get('unavailable'), 'Marked unavailable: ' + row.get('label'));
        }
        Assert.isTrue(cards.agingBuckets.isEmpty(), 'No aging bucket.');
        Assert.isTrue(worklist.disputedInvoices.isEmpty(), 'An unavailable tab carries no rows.');
        Assert.isTrue(worklist.highValueDelinquents.isEmpty(), 'An unavailable tab carries no rows.');
        Assert.isTrue(worklist.criticalFollowUpInvoices.isEmpty(), 'An unavailable tab carries no rows.');
        Assert.areEqual(new List<String>{
            RLM_CollectionsDashboardController.WORKLIST_CRITICAL,
            RLM_CollectionsDashboardController.WORKLIST_HIGH_VALUE,
            RLM_CollectionsDashboardController.WORKLIST_DISPUTED
        }, worklist.unavailable, 'Each refused tab is unavailable, not "nothing to work on".');
        Assert.isTrue(promises.unavailable, 'An unreadable schedule item is unavailable, not "no promises".');
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_REFUSED, promises.unavailableReason, 'A refusal.');
        Assert.isTrue(tasks.unavailable, 'An unreadable task list is unavailable, not "no tasks".');
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_REFUSED, tasks.unavailableReason, 'A refusal.');
        Assert.isTrue(progress.unavailable, 'Unreadable plans are unavailable, not "no plans".');
        Assert.areEqual(RLM_CollectionsDashboardController.REASON_REFUSED, progress.unavailableReason, 'A refusal.');
        for (String key : cards.unavailable) {
            Assert.areEqual(RLM_CollectionsDashboardController.REASON_REFUSED, cards.unavailableReason.get(key),
                'Each refused card component says so: ' + key);
        }
        for (String key : worklist.unavailable) {
            Assert.areEqual(RLM_CollectionsDashboardController.REASON_REFUSED, worklist.unavailableReason.get(key),
                'Each refused worklist tab says so: ' + key);
        }
    }

    // A user who cannot read Account gets only the "All Accounts" sentinel, like the other
    // lists that fall back when a read is refused, instead of a raw QueryException.
    @isTest
    static void getAccountOptions_forAUserWhoCannotReadAccounts_returnsOnlyTheSentinel() {
        User noAccess = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        newAccount('RLM CD Account Options Unreadable');

        List<Map<String, String>> options;
        Test.startTest();
        System.runAs(noAccess) {
            Assert.isTrue(userModeQueryFails('SELECT Id FROM Account LIMIT 1'),
                'PRECONDITION: the user cannot read Account.');
            options = RLM_CollectionsDashboardController.getAccountOptions().options;
        }
        Test.stopTest();

        Assert.areEqual(1, options.size(), 'Only the sentinel is offered; no account is listed.');
        Assert.areEqual('', options[0].get('value'), 'The sentinel has a blank value.');
        Assert.areEqual('All Accounts', options[0].get('label'), 'The sentinel is "All Accounts".');
    }

    // The collections persona reads its own plan through the USER_MODE queries. A permission gap would
    // show as an unavailable list or progress panel instead of the plan. The user holds the Billing and
    // Billing Advanced permission set licenses.
    @isTest
    static void collectionsSpecialist_readsTheirPlanInUserMode() {
        User specialist = RLM_BillingUITestUsers.create(
            new List<String>{
                'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations', 'BillingCollectionsAndRecoverySpecialist'
            },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL, RLM_BillingUITestUsers.BILLING_ADVANCED_PSL });
        Account a = newAccount('RLM CD Specialist');
        CollectionPlan plan = newPlan(a.Id, Date.today().addDays(5));
        plan.OwnerId = specialist.Id;
        plan.DaysPastDue = 12;
        insert plan;

        List<RLM_CollectionsDashboardController.MyCollectionPlanItem> mine;
        RLM_CollectionsDashboardController.CollectionsProgressData progress;
        Test.startTest();
        System.runAs(specialist) {
            mine = RLM_CollectionsDashboardController.getMyCollectionPlans().items;
            progress = RLM_CollectionsDashboardController.getCollectionsProgress();
        }
        Test.stopTest();

        Assert.areEqual(1, mine.size(), 'The specialist reads the plan they own.');
        Assert.areEqual(plan.Id, mine[0].collectionPlanId, 'Their plan.');
        Assert.areEqual(a.Id, mine[0].accountId, 'With its account.');
        Assert.areEqual(Date.today().addDays(5), mine[0].dueDate, 'And its due date.');
        Assert.areEqual(1, progress.totalPlans, 'The specialist measures the plan they can read.');
        Assert.areEqual(1, progress.notRecoveredCount, 'It is open.');
        assertAmount(12, progress.avgDaysPastDue, 'Its days past due.');
    }

    // Worklist rows sort by days overdue, most overdue first and unknown last. The shorter
    // constructors default the health score and leave the promise and reason empty.
    @isTest
    static void worklistItems_sortMostOverdueFirstWithUnknownLast() {
        RLM_CollectionsDashboardController.WorklistItem tenDays =
            new RLM_CollectionsDashboardController.WorklistItem(null, 'Ten', 100, 10, 'critical');
        RLM_CollectionsDashboardController.WorklistItem thirtyDays =
            new RLM_CollectionsDashboardController.WorklistItem(null, 'Thirty', 50, 30, 'critical', 'red');
        RLM_CollectionsDashboardController.WorklistItem unknown =
            new RLM_CollectionsDashboardController.WorklistItem(null, 'Unknown', 75, null, 'critical', 'green',
                Date.today(), 'A reason');
        List<RLM_CollectionsDashboardController.WorklistItem> items =
            new List<RLM_CollectionsDashboardController.WorklistItem>{ unknown, tenDays, thirtyDays };

        items.sort();

        Assert.areEqual('Thirty', items[0].accountName, 'Most overdue first.');
        Assert.areEqual('Ten', items[1].accountName, 'Then less overdue.');
        Assert.areEqual('Unknown', items[2].accountName, 'Unknown days overdue last.');
        Assert.areEqual(0, unknown.compareTo(
            new RLM_CollectionsDashboardController.WorklistItem(null, 'Also unknown', 0, null, 'critical')),
            'Two unknowns are equal.');
        Assert.areEqual('amber', tenDays.healthScore, 'The five-argument constructor defaults to amber.');
        Assert.areEqual('red', thirtyDays.healthScore, 'The six-argument constructor takes the health score.');
        Assert.isNull(thirtyDays.ptpDate, 'No promise to pay unless given.');
        Assert.isNull(thirtyDays.disputeReason, 'No dispute reason unless given.');
        Assert.areEqual(Date.today(), unknown.ptpDate, 'The eight-argument constructor takes the promise date.');
        Assert.areEqual('A reason', unknown.disputeReason, 'And the dispute reason.');
    }

    @isTest
    static void wrappers_fillDefaultsForMissingValues() {
        RLM_CollectionsDashboardController.CriticalFollowUpInvoiceItem invoiceRow =
            new RLM_CollectionsDashboardController.CriticalFollowUpInvoiceItem(null, null, 0, null, null, null, null, null);
        RLM_CollectionsDashboardController.MyCollectionPlanItem planRow =
            new RLM_CollectionsDashboardController.MyCollectionPlanItem(null, null, null, null, null, null);
        RLM_CollectionsDashboardController.PaymentPromiseBucket bucket =
            new RLM_CollectionsDashboardController.PaymentPromiseBucket('Draft', null, null);

        Assert.areEqual(NO_VALUE, invoiceRow.invoiceNumber, 'A missing invoice number shows a dash.');
        Assert.areEqual(NO_VALUE, invoiceRow.billingAccountName, 'A missing account name shows a dash.');
        Assert.areEqual(NO_VALUE, planRow.name, 'A missing plan name shows a dash.');
        Assert.areEqual(NO_VALUE, planRow.accountName, 'A missing account name shows a dash.');
        assertAmount(0, planRow.totalInvoiceBalance, 'A missing balance is zero.');
        assertAmount(0, bucket.totalRequestedAmount, 'A missing amount is zero.');
        Assert.areEqual(0, bucket.itemCount, 'A missing count is zero.');
    }

    // ─── Seams over queried invoices ─────────────────────────────────────────
    // Invoice cannot be inserted in Apex, so these build invoices with JSON.deserialize, read-only
    // fields included, and pass them to the methods the controller calls with the rows it queried.

    private static Invoice invoice(Map<String, Object> fields) {
        return (Invoice) JSON.deserialize(JSON.serialize(fields), Invoice.class);
    }

    private static Map<String, Object> amountsDue(Decimal balance, Decimal total, Date dueDate) {
        return new Map<String, Object>{ 'Balance' => balance, 'TotalAmount' => total, 'DueDate' => dueDate };
    }

    // Each unpaid invoice adds its balance to the total and to one aging bucket by days past due
    // (30, 60 and 90 close their buckets); one not yet due, or with no due date, is current. One
    // with a balance below its total is partially settled; the rest count as not settled.
    @isTest
    static void tallyInvoices_bucketsByDaysPastDueAndSplitsBySettlement() {
        Date today = Date.newInstance(2026, 6, 30);
        List<Invoice> invoices = new List<Invoice>{
            invoice(amountsDue(100, 100, today.addDays(5))),
            invoice(amountsDue(40, 100, today.addDays(-30))),
            invoice(amountsDue(50, 50, today.addDays(-60))),
            invoice(amountsDue(60, 0, today.addDays(-90))),
            invoice(amountsDue(70, 80, today.addDays(-91))),
            invoice(amountsDue(25, 25, null)),
            invoice(amountsDue(null, 100, null)),
            invoice(amountsDue(15, 15, today))
        };
        RLM_CollectionsDashboardController.CollectionsDashboardData data =
            new RLM_CollectionsDashboardController.CollectionsDashboardData();

        Test.startTest();
        RLM_CollectionsDashboardController.tallyInvoices(data, invoices, today);
        Test.stopTest();

        Assert.areEqual(360, data.receivablesOutstanding, 'Every balance adds up; a blank one adds nothing');
        Assert.areEqual(8, data.invoiceCount, 'Every invoice is counted');
        Assert.areEqual(140, data.currentDue, 'Due today, not yet due, or no due date, is current');
        Assert.areEqual(220, data.overdue, 'Past due balances are overdue');
        Assert.areEqual(2, data.partiallySettledCount, 'A balance below its total is partially settled');
        Assert.areEqual(110, data.partiallySettledSum, 'The partially settled balances add up');
        Assert.areEqual(6, data.notSettledCount,
            'Full balances, a zero total and a blank balance (even under a set total) are not settled');
        Assert.areEqual(250, data.notSettledSum, 'The not-settled balances add up');
        Map<String, Object> byKey = new Map<String, Object>();
        for (Map<String, Object> bucket : data.agingBuckets) {
            byKey.put((String) bucket.get('key'), bucket.get('amount'));
        }
        Assert.areEqual(140, (Decimal) byKey.get('current'), 'Due today, not yet due and no due date are current');
        Assert.areEqual(40, (Decimal) byKey.get('1-30'), 'Thirty days past due is still 1-30');
        Assert.areEqual(50, (Decimal) byKey.get('31-60'), 'Sixty days past due is still 31-60');
        Assert.areEqual(60, (Decimal) byKey.get('61-90'), 'Ninety days past due is still 61-90');
        Assert.areEqual(70, (Decimal) byKey.get('90+'), 'Ninety-one days past due is 90+');
    }

    // High-value delinquents are accounts whose balances add up to 2000 or more, largest first,
    // each with its most overdue days and its collection plan.
    @isTest
    static void addHighValueDelinquents_keepsAccountsOwingTwoThousandOrMore() {
        Account threeInvoices = newAccount('RLM High Value Three');
        Account justUnder = newAccount('RLM High Value Under');
        Account withPlan = newAccount('RLM High Value Plan');
        Date today = Date.newInstance(2026, 6, 30);
        CollectionPlan plan = newPlan(withPlan.Id, today.addDays(10));
        insert plan;
        List<Invoice> invoices = new List<Invoice>{
            invoice(new Map<String, Object>{ 'Balance' => 1000, 'DueDate' => today.addDays(-40), 'BillingAccountId' => threeInvoices.Id }),
            invoice(new Map<String, Object>{ 'Balance' => 600, 'DueDate' => today.addDays(-70), 'BillingAccountId' => threeInvoices.Id }),
            invoice(new Map<String, Object>{ 'Balance' => 400, 'DueDate' => today.addDays(-50), 'BillingAccountId' => threeInvoices.Id }),
            invoice(new Map<String, Object>{ 'Balance' => 1999, 'DueDate' => today.addDays(-90), 'BillingAccountId' => justUnder.Id }),
            invoice(new Map<String, Object>{ 'Balance' => 5000, 'DueDate' => today.addDays(-35), 'BillingAccountId' => withPlan.Id })
        };
        RLM_CollectionsDashboardController.WorklistData wl = new RLM_CollectionsDashboardController.WorklistData();

        Test.startTest();
        RLM_CollectionsDashboardController.addHighValueDelinquents(wl, invoices, 'BillingAccountId', today);
        Test.stopTest();

        Assert.areEqual(2, wl.highValueDelinquents.size(), 'An account owing 1999 is left out');
        RLM_CollectionsDashboardController.WorklistItem first = wl.highValueDelinquents[0];
        RLM_CollectionsDashboardController.WorklistItem second = wl.highValueDelinquents[1];
        Assert.areEqual(withPlan.Id, first.accountId, 'The largest balance comes first');
        Assert.areEqual(plan.Id, first.collectionPlanId, 'The account\'s collection plan is attached');
        Assert.areEqual(35, first.daysOverdue, 'Days overdue come from the due date');
        Assert.areEqual(threeInvoices.Id, second.accountId, 'Invoices adding up to exactly 2000 qualify');
        Assert.areEqual(2000, second.balance, 'The account\'s invoices add up');
        Assert.areEqual(70, second.daysOverdue, 'The most overdue invoice sets the days, not the first or last one');
        Assert.isNull(second.collectionPlanId, 'An account without a plan has none');
        Assert.isFalse(second.collectionPlanUnavailable, 'Read and empty: "no plan", not unavailable');
        Assert.areEqual('RLM High Value Three', second.accountName, 'The account name is looked up');
        Assert.isFalse(second.accountNameUnavailable, 'A read name is available');
        Assert.areEqual('red', second.healthScore, 'High-value rows are red');
    }

    // A user who cannot read Account still gets the rows (with a dash for the name) rather than the caller's
    // catch dropping the whole section; the critical follow-up builder shares the lookup. The same user
    // cannot read CollectionPlan either: the row's plan is marked unavailable, not "no plan".
    @isTest
    static void addHighValueDelinquents_forAUserWhoCannotReadAccounts_keepsRowsWithDashNames() {
        User noAccess = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        Account acc = newAccount('RLM High Value Unreadable');
        Date today = Date.newInstance(2026, 6, 30);
        List<Invoice> invoices = new List<Invoice>{
            invoice(new Map<String, Object>{ 'Balance' => 5000, 'DueDate' => today.addDays(-35), 'BillingAccountId' => acc.Id })
        };
        RLM_CollectionsDashboardController.WorklistData wl = new RLM_CollectionsDashboardController.WorklistData();

        Test.startTest();
        System.runAs(noAccess) {
            Assert.isTrue(userModeQueryFails('SELECT Id FROM Account LIMIT 1'),
                'PRECONDITION: the user cannot read Account.');
            RLM_CollectionsDashboardController.addHighValueDelinquents(wl, invoices, 'BillingAccountId', today);
        }
        Test.stopTest();

        Assert.areEqual(1, wl.highValueDelinquents.size(), 'The row is kept although the name read is refused.');
        Assert.areEqual(acc.Id, wl.highValueDelinquents[0].accountId, 'The row is the account\'s.');
        Assert.areEqual(NO_VALUE, wl.highValueDelinquents[0].accountName, 'No name, not a raw exception.');
        Assert.isTrue(wl.highValueDelinquents[0].accountNameUnavailable, 'A refused name read is not available, not "no name".');
        Assert.isTrue(wl.highValueDelinquents[0].collectionPlanUnavailable,
            'A refused plan lookup marks the plan unavailable (no Create offered), not "no plan".');
    }

    @isTest
    static void criticalFollowUps_forAUserWhoCannotReadAccounts_keepRows() {
        User noAccess = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        Account acc = newAccount('RLM Critical Unreadable');
        Date today = Date.newInstance(2026, 6, 30);
        List<Invoice> invoices = new List<Invoice>{
            // An Id, so the plan item lookup runs (and is refused for this user).
            invoice(new Map<String, Object>{ 'Id' => Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + '000000000009'),
                'Balance' => 5000, 'DueDate' => today.addDays(-35), 'BillingAccountId' => acc.Id })
        };
        RLM_CollectionsDashboardController.WorklistData critical = new RLM_CollectionsDashboardController.WorklistData();

        Test.startTest();
        System.runAs(noAccess) {
            Assert.isTrue(userModeQueryFails('SELECT Id FROM Account LIMIT 1'),
                'PRECONDITION: the user cannot read Account.');
            RLM_CollectionsDashboardController.addCriticalFollowUps(critical, invoices, false, false, today);
        }
        Test.stopTest();

        Assert.areEqual(1, critical.criticalFollowUpInvoices.size(), 'The critical follow-up row is kept.');
        Assert.areEqual(NO_VALUE, critical.criticalFollowUpInvoices[0].billingAccountName, 'No name.');
        Assert.isTrue(critical.criticalFollowUpInvoices[0].accountNameUnavailable, 'A refused name read is not available.');
        Assert.isTrue(critical.criticalFollowUpInvoices[0].collectionPlanUnavailable,
            'A refused plan item lookup marks the plan unavailable, not "no plan".');
    }

    // A critical follow-up row per invoice: days overdue from the field when the org has it and it
    // is set, else from the due date; a blank invoice number or account name shows a dash.
    @isTest
    static void addCriticalFollowUps_buildsOneRowPerInvoice() {
        Account acc = newAccount('RLM Critical Follow Up');
        Id contactId = Id.valueOf(Contact.SObjectType.getDescribe().getKeyPrefix() + '000000000001');
        Id invoiceA = Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + '000000000001');
        Id invoiceB = Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + '000000000002');
        Date today = Date.newInstance(2026, 6, 30);
        // Invoice.BillToContactId is optional to the controller, so it is set only where it exists.
        Boolean hasContactField = Invoice.SObjectType.getDescribe().fields.getMap().containsKey('BillToContactId');
        Map<String, Object> fullInvoice = new Map<String, Object>{ 'Id' => invoiceA, 'InvoiceNumber' => 'INV-1',
            'Balance' => 2500, 'DaysInvoiceOverdue' => 45, 'DueDate' => today.addDays(-10), 'BillingAccountId' => acc.Id };
        if (hasContactField) {
            fullInvoice.put('BillToContactId', contactId);
        }
        List<Invoice> invoices = new List<Invoice>{
            invoice(fullInvoice),
            invoice(new Map<String, Object>{ 'Id' => invoiceB, 'DueDate' => today.addDays(-33) })
        };
        RLM_CollectionsDashboardController.WorklistData withFields = new RLM_CollectionsDashboardController.WorklistData();
        RLM_CollectionsDashboardController.WorklistData withoutFields = new RLM_CollectionsDashboardController.WorklistData();

        Test.startTest();
        RLM_CollectionsDashboardController.addCriticalFollowUps(withFields, invoices, true, hasContactField, today);
        RLM_CollectionsDashboardController.addCriticalFollowUps(withoutFields, invoices, false, false, today);
        Test.stopTest();

        Assert.areEqual(2, withFields.criticalFollowUpInvoices.size(), 'One row per invoice');
        Assert.areEqual(2, withoutFields.criticalFollowUpInvoices.size(), 'One row per invoice, whatever fields the org has');
        RLM_CollectionsDashboardController.CriticalFollowUpInvoiceItem full = withFields.criticalFollowUpInvoices[0];
        Assert.areEqual(invoiceA, full.invoiceId, 'Rows keep the invoice order');
        Assert.areEqual('INV-1', full.invoiceNumber, 'The invoice number is shown');
        Assert.areEqual(2500, full.balance, 'The balance is shown');
        Assert.areEqual(45, full.daysInvoiceOverdue, 'The overdue-days field wins over the due date');
        Assert.areEqual(acc.Id, full.billingAccountId, 'The billing account is shown');
        Assert.areEqual('RLM Critical Follow Up', full.billingAccountName, 'The account name is looked up');
        if (hasContactField) {
            Assert.areEqual(contactId, full.billToContactId, 'The bill-to contact is shown');
        }

        RLM_CollectionsDashboardController.CriticalFollowUpInvoiceItem bare = withFields.criticalFollowUpInvoices[1];
        Assert.areEqual(33, bare.daysInvoiceOverdue, 'With the field blank, days come from the due date');
        Assert.areEqual(NO_VALUE, bare.invoiceNumber, 'A blank invoice number shows a dash');
        Assert.areEqual(NO_VALUE, bare.billingAccountName, 'No account shows a dash');
        Assert.areEqual(0, bare.balance, 'A blank balance shows zero');

        RLM_CollectionsDashboardController.CriticalFollowUpInvoiceItem noFields = withoutFields.criticalFollowUpInvoices[0];
        Assert.areEqual(10, noFields.daysInvoiceOverdue, 'Without the overdue-days field, days come from the due date');
        if (hasContactField) {
            Assert.isNull(noFields.billToContactId, 'Without the bill-to contact field, no contact is shown');
        }
    }

    // ------------------------------------------------------------------ helpers

    private static Account newAccount(String name) {
        Account a = new Account(Name = name);
        insert a;
        return a;
    }

    // Not inserted, so callers can set more fields first. UsageType is set by name, as
    // RLM_AccountUtilitiesTest does; no CollectionPlanReason, so RLM_Create_Case_for_Collection
    // does not raise a case of its own.
    private static CollectionPlan newPlan(Id accountId, Date dueDate) {
        CollectionPlan plan = new CollectionPlan(AccountId = accountId, Duedate = dueDate);
        plan.put('UsageType', 'Billing');
        return plan;
    }

    // Debit memos are created by name, as the controller reads them.
    private static SObject newRecord(String objectName, Map<String, Object> values) {
        SObject record = Schema.getGlobalDescribe().get(objectName).newSObject();
        for (String field : values.keySet()) {
            record.put(field, values.get(field));
        }
        insert record;
        return record;
    }

    // A grouped SUM of a currency field comes back in the corporate currency, so records whose
    // amounts are summed are created in it.
    private static String corporateCurrency() {
        return [SELECT IsoCode FROM CurrencyType WHERE IsCorporate = true LIMIT 1].IsoCode;
    }

    // An ungrouped SUM of a currency field is reported in a currency the platform picks (the
    // running user's or the corporate one); where the two are the same it reads the records'
    // own amounts. Logs a visible skip otherwise.
    private static Boolean userCurrencyIsCorporate() {
        if (UserInfo.getDefaultCurrency() == corporateCurrency()) {
            return true;
        }
        System.debug(LoggingLevel.WARN, 'SKIPPED: ungrouped currency aggregate depends on the running '
            + 'user\'s currency matching the corporate currency');
        return false;
    }

    // An active currency other than the given one; a code no record can carry if there is none.
    // An unknown code returns no rows rather than throwing; verified on a Release 264 org.
    private static String anotherCurrency(String isoCode) {
        List<CurrencyType> others = [
            SELECT IsoCode FROM CurrencyType WHERE IsActive = true AND IsoCode != :isoCode LIMIT 1
        ];
        return others.isEmpty() ? 'ZZZ' : others[0].IsoCode;
    }

    // True when the running user may not run the query in user mode.
    private static Boolean userModeQueryFails(String soql) {
        try {
            Database.query(soql, AccessLevel.USER_MODE);
            return false;
        } catch (Exception e) {
            return true;
        }
    }

    private static String firstActivePicklistValue(Schema.SObjectField field) {
        for (Schema.PicklistEntry entry : field.getDescribe().getPicklistValues()) {
            if (entry.isActive()) {
                return entry.getValue();
            }
        }
        return null;
    }

    // The controller appends a case's Reason in brackets after the subject or description.
    private static String reasonSuffix(Case c) {
        return c.Reason != null ? ' [' + c.Reason + ']' : '';
    }

    private static Map<Id, RLM_CollectionsDashboardController.WorklistItem> byAccount(
        List<RLM_CollectionsDashboardController.WorklistItem> items) {
        Map<Id, RLM_CollectionsDashboardController.WorklistItem> m =
            new Map<Id, RLM_CollectionsDashboardController.WorklistItem>();
        for (RLM_CollectionsDashboardController.WorklistItem item : items) {
            m.put(item.accountId, item);
        }
        return m;
    }

    // Fails on a null amount and names both values in the message; Decimal equality already
    // ignores scale.
    private static void assertAmount(Decimal expected, Decimal actual, String message) {
        Assert.isTrue(actual != null && actual == expected,
            message + ' Expected ' + expected + ', got ' + actual + '.');
    }

    private static Map<String, RLM_CollectionsDashboardController.PaymentPromiseBucket> bucketsByStatus(
        RLM_CollectionsDashboardController.PaymentPromiseSummary summary) {
        Assert.isFalse(summary.unavailable, 'PRECONDITION: the schedule items were read.');
        List<RLM_CollectionsDashboardController.PaymentPromiseBucket> buckets = summary.buckets;
        Map<String, RLM_CollectionsDashboardController.PaymentPromiseBucket> byStatus =
            new Map<String, RLM_CollectionsDashboardController.PaymentPromiseBucket>();
        for (RLM_CollectionsDashboardController.PaymentPromiseBucket b : buckets) {
            byStatus.put(b.status, b);
        }
        return byStatus;
    }
}
