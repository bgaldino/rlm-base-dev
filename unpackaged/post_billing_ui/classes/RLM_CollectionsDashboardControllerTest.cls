/**
 * Tests for RLM_CollectionsDashboardController.
 *
 * Invoice is createable=false, so no unit test can hold an invoice: the invoice loops
 * (cards aging, critical follow-ups, high-value delinquents and the worklist fallbacks)
 * can only be verified live. What a test can build -- payments, payment schedule items,
 * collection plans, tasks, cases and debit memos -- is built here, and the cards, worklist,
 * plans, progress and tasks are asserted against it where a test can tell the result apart.
 * Records are created in admin context. Two tests then run as other
 * users: a collections specialist, who reads their own plan, and a user with no access, who
 * gets empty sections. The specialist takes a seat of the Billing and the Billing Advanced
 * licenses for the test, as RLM_BillingUITestUsers documents, so it fails on the license in an
 * org whose seats are all assigned; the no-access user takes a Salesforce user licence but no
 * Billing seat.
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
        List<Map<String, String>> accounts = RLM_CollectionsDashboardController.getAccountOptions();
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

        List<String> labels = new List<String>{ 'Unpaid Invoices', 'Debit Memos', 'Unapplied Credits', 'Unapplied Payments' };
        Assert.areEqual(labels.size(), unfiltered.totalBalanceBreakdown.size(), 'One breakdown row per balance component.');
        for (Integer i = 0; i < labels.size(); i++) {
            Assert.areEqual(labels[i], unfiltered.totalBalanceBreakdown[i].get('label'), 'Breakdown order, row ' + i);
        }

        List<String> agingKeys = new List<String>{ 'current', '1-30', '31-60', '61-90', '90+' };
        // Bucket and invoice amounts are not asserted: no invoice can exist in a unit test, so
        // they are zero whatever the controller does.
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

    // A Draft debit memo is not owed: only a posted memo not yet on a posted invoice counts.
    // The memo has a total and is on the filtered account, so its Draft status is what keeps it
    // out. A unit test cannot post one (its lines need a tax treatment), so the posted sum is
    // live-only.
    @isTest
    static void getDashboardCards_draftDebitMemoIsNotOwed() {
        Account a = newAccount('RLM CD Debit Memo');
        SObject memo = newRecord('DebitMemo', new Map<String, Object>{
            'AccountId' => a.Id, 'Status' => 'Draft', 'InvoiceGenerationStatus' => 'None'
        });
        newRecord('DebitMemoLine', new Map<String, Object>{
            'Name' => 'RLM CD Debit Memo Line', 'DebitMemoId' => memo.Id, 'ChargeAmount' => 10
        });
        Id memoId = memo.Id;
        SObject saved = Database.query('SELECT TotalAmount, Status FROM DebitMemo WHERE Id = :memoId')[0];
        Decimal memoTotal = (Decimal) saved.get('TotalAmount');
        Assert.isTrue(memoTotal != null && memoTotal > 0,
            'PRECONDITION: the Draft memo totals its line. Got ' + memoTotal);
        Assert.areEqual('Draft', saved.get('Status'), 'PRECONDITION: the memo is Draft.');
        // The controller filters on BillToAccountId when DebitMemo has it, else on AccountId.
        Assert.isFalse(Schema.getGlobalDescribe().get('DebitMemo').getDescribe().fields.getMap().containsKey('billtoaccountid'),
            'PRECONDITION: DebitMemo has no BillToAccountId, so the controller filters on AccountId.');
        // The controller's own aggregate, in user mode, with Status = 'Draft' in place of
        // 'Posted': the SUM runs and returns a positive total for the memo, so the controller's
        // query is not refused and its zero comes from the Status filter, not from a swallowed
        // error. Only the sign is checked, so the currency the SUM reports in does not matter.
        Id aId = a.Id;
        List<AggregateResult> control = Database.query(
            'SELECT SUM(TotalAmount) s FROM DebitMemo WHERE TotalAmount != null AND Status = \'Draft\''
            + ' AND InvoiceGenerationStatus != \'Posted Invoice Generated\' AND AccountId = :aId',
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
    // built from its subject, description (cut at 200 characters) and Reason. With no invoices,
    // the other two sections hold their placeholder rows.
    @isTest
    static void getWorklist_openCasesListTheirAccountsAsDisputed() {
        // Inserted out of name order, so only the name ordering makes A the placeholder's account.
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

        Assert.areEqual(1, unfiltered.criticalFollowUpInvoices.size(), 'One placeholder critical row.');
        RLM_CollectionsDashboardController.CriticalFollowUpInvoiceItem critical = unfiltered.criticalFollowUpInvoices[0];
        Assert.isNull(critical.invoiceId, 'The placeholder names no invoice.');
        Assert.areEqual('No invoices overdue >= 30 days', critical.invoiceNumber, 'The placeholder explains itself.');
        assertAmount(0, critical.balance, 'The placeholder has no balance.');
        Assert.areEqual(NO_VALUE, critical.billingAccountName, 'The placeholder has no account.');

        Assert.areEqual(1, unfiltered.highValueDelinquents.size(), 'One placeholder high-value row.');
        RLM_CollectionsDashboardController.WorklistItem highValue = unfiltered.highValueDelinquents[0];
        Assert.areEqual(a.Id, highValue.accountId, 'The placeholder uses the first account by name.');
        Assert.areEqual('highValue', highValue.segment, 'High-value segment.');
        Assert.areEqual('red', highValue.healthScore, 'High-value rows are red.');

        Assert.areEqual(1, onlyB.disputedInvoices.size(), 'The account filter keeps only that account\'s case.');
        Assert.areEqual(b.Id, onlyB.disputedInvoices[0].accountId, 'The filtered row is account B.');
        Assert.areEqual(1, onlyB.highValueDelinquents.size(), 'The filtered worklist has its placeholder row.');
        Assert.areEqual(a.Id, onlyB.highValueDelinquents[0].accountId,
            'Known gap: the placeholder row ignores the account filter and uses the first account by '
            + 'name. Update this test when it is fixed.');
    }

    // The placeholders borrow an account, so with no account at all there are none.
    @isTest
    static void getWorklist_withNoAccounts_addsNoPlaceholderRows() {
        Test.startTest();
        RLM_CollectionsDashboardController.WorklistData wl = RLM_CollectionsDashboardController.getWorklist(null, null);
        Test.stopTest();

        Assert.isTrue(wl.criticalFollowUpInvoices.isEmpty(), 'No placeholder without an account.');
        Assert.isTrue(wl.highValueDelinquents.isEmpty(), 'No placeholder without an account.');
        Assert.isTrue(wl.disputedInvoices.isEmpty(), 'No cases, no disputed rows.');
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
            RLM_CollectionsDashboardController.getMyCollectionPlans();
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
            RLM_CollectionsDashboardController.getCollectionPlanTasks(a.Id);
        List<RLM_CollectionsDashboardController.CpTaskItem> forAll =
            RLM_CollectionsDashboardController.getCollectionPlanTasks(null);
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

    // A user who cannot read the billing objects gets empty sections, not an error: each one
    // catches its own failure. The same records give the admin a populated dashboard. The empty
    // cards and promise buckets need the user-mode queries to throw (a readable, empty result
    // would still build them); the case, task, plan and placeholder empties could also come from
    // sharing.
    @isTest
    static void allSections_forAUserWhoCannotReadThem_degradeToEmpty() {
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
        // open case, the placeholder, the plan's task, the plan and the schedule item all show.
        Assert.areEqual(4, RLM_CollectionsDashboardController.getDashboardCards(null, null).totalBalanceBreakdown.size(),
            'PRECONDITION: the admin gets the full breakdown.');
        RLM_CollectionsDashboardController.WorklistData adminWorklist =
            RLM_CollectionsDashboardController.getWorklist(null, null);
        Assert.areEqual(1, adminWorklist.disputedInvoices.size(), 'PRECONDITION: the admin sees the open case.');
        Assert.areEqual(1, adminWorklist.highValueDelinquents.size(), 'PRECONDITION: the admin gets the placeholder.');
        Assert.areEqual(1, RLM_CollectionsDashboardController.getCollectionPlanTasks(null).size(),
            'PRECONDITION: the admin sees the plan\'s task.');
        Assert.areEqual(1, RLM_CollectionsDashboardController.getCollectionsProgress().totalPlans,
            'PRECONDITION: the admin measures the plan.');
        Assert.areEqual(1, bucketsByStatus(RLM_CollectionsDashboardController.getPaymentPromiseSummary(null, null))
            .get('Draft').itemCount, 'PRECONDITION: the admin sees the schedule item.');

        List<String> readable = new List<String>();
        RLM_CollectionsDashboardController.CollectionsDashboardData cards;
        RLM_CollectionsDashboardController.WorklistData worklist;
        List<RLM_CollectionsDashboardController.PaymentPromiseBucket> promises;
        List<RLM_CollectionsDashboardController.CpTaskItem> tasks;
        RLM_CollectionsDashboardController.CollectionsProgressData progress;
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
        }
        Test.stopTest();

        Assert.isTrue(readable.isEmpty(), 'PRECONDITION: the user cannot query ' + readable + ' in user mode.');
        Assert.isTrue(cards.totalBalanceBreakdown.isEmpty(),
            'An unreadable Invoice returns the cards before any breakdown is built.');
        Assert.isTrue(cards.agingBuckets.isEmpty(), 'Nor any aging bucket.');
        Assert.isTrue(worklist.disputedInvoices.isEmpty(), 'The open case is not listed (access or sharing).');
        Assert.isTrue(worklist.highValueDelinquents.isEmpty(), 'No placeholder row (access or sharing).');
        Assert.isTrue(worklist.criticalFollowUpInvoices.isEmpty(), 'No placeholder row (access or sharing).');
        Assert.isTrue(promises.isEmpty(), 'An unreadable schedule item returns no buckets.');
        Assert.isTrue(tasks.isEmpty(), 'The plan\'s task is not listed (access or sharing).');
        Assert.areEqual(0, progress.totalPlans, 'The plan is not measured (access or sharing).');
    }

    // The collections persona reads its own plan through the USER_MODE queries. A permission
    // gap would show as an empty list, since both methods swallow their query errors. The user
    // takes a Billing and a Billing Advanced seat for the test.
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
            mine = RLM_CollectionsDashboardController.getMyCollectionPlans();
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
        List<RLM_CollectionsDashboardController.PaymentPromiseBucket> buckets) {
        Map<String, RLM_CollectionsDashboardController.PaymentPromiseBucket> byStatus =
            new Map<String, RLM_CollectionsDashboardController.PaymentPromiseBucket>();
        for (RLM_CollectionsDashboardController.PaymentPromiseBucket b : buckets) {
            byStatus.put(b.status, b);
        }
        return byStatus;
    }
}
