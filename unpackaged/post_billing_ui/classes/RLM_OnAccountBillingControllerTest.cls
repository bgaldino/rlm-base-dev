@isTest
private class RLM_OnAccountBillingControllerTest {

    @isTest
    static void getBillingSummary_nullAccount_returnsEmptyMap() {
        Test.startTest();
        Map<String, Object> result = RLM_OnAccountBillingController.getBillingSummary(null);
        Test.stopTest();
        System.assertNotEquals(null, result, 'A non-null map should always be returned.');
        System.assertEquals(0, result.size(), 'A null account id should short-circuit to an empty map.');
    }

    // Invoices cannot be created in an Apex test, and debit memos cannot be posted. This
    // account has no billing records at all, so every aggregate and count runs its empty
    // path, and the summary must report zero balances and clean status flags.
    @isTest
    static void getBillingSummary_accountWithNoBilling_returnsZeroBalances() {
        Account acc = new Account(Name = 'RLM On-Account Billing Test');
        insert acc;

        Test.startTest();
        Map<String, Object> result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
        Test.stopTest();

        System.assertNotEquals(null, result, 'A result map should be returned.');
        System.assertEquals(0, (Decimal) result.get('invoiceBalance'), 'No invoices -> zero balance.');
        System.assertEquals(0, (Decimal) result.get('debitMemoBalance'), 'No debit memos -> zero balance.');
        System.assertEquals(0, (Decimal) result.get('creditMemoBalance'), 'No credit memos -> zero balance.');
        System.assertEquals(0, (Decimal) result.get('paymentBalance'), 'No payments -> zero balance.');
        System.assertEquals(0, (Decimal) result.get('netAccountBalance'), 'No activity -> zero net balance.');
        System.assertEquals(0, (Integer) result.get('totalInvoices'), 'No invoices -> zero count.');
        System.assertEquals(0, (Integer) result.get('overdueCount'), 'No invoices -> zero overdue.');
        System.assertEquals(false, (Boolean) result.get('inCollections'),
            'No collection plans -> account is not in collections.');
    }

    // Payment, unlike invoices, is Apex-createable. A processed payment in the corporate
    // currency, on an account in the corporate currency, is summed as is and lowers the net
    // balance by its balance. (A non-corporate account currency is covered below.)
    // The positive paths here run as a billing operations user, not the deploying admin:
    // RLM_BillingUI is assigned only after this bundle deploys. That user is read-only, so the
    // admin creates the records: the account is owned by the user, and a payment (which has no
    // owner) is checked to be visible to the user before the summary runs.
    @isTest
    static void getBillingSummary_processedPayment_lowersTheNetBalance() {
        User u = billingOperationsUser();
        String corporate = corporateCurrency();
        Account acc = newAccountOwnedBy(u, 'RLM On-Account Billing Payment Test', corporate);
        Payment pmt = newProcessedPayment(acc.Id, 250, corporate);
        Decimal balance = [SELECT Balance FROM Payment WHERE Id = :pmt.Id].Balance;
        Assert.areEqual(250, balance, 'PRECONDITION: an unapplied processed payment\'s balance is its amount.');

        Test.startTest();
        Map<String, Object> result = paymentSummaryAs(u, acc.Id, pmt.Id);
        Test.stopTest();

        Assert.areEqual(250, (Decimal) result.get('paymentBalance'),
            'The payment balance is the processed payment\'s unapplied balance.');
        Assert.areEqual(-250, (Decimal) result.get('netAccountBalance'),
            'With nothing else on the account, the net balance is minus the payment balance.');
        Assert.areEqual(corporate, (String) result.get('currencyIsoCode'),
            'The summary is shown in the account\'s currency.');
        Assert.areEqual(true, (Boolean) result.get('isMultiCurrency'), 'This org is multi-currency.');
    }

    // SUM() with GROUP BY CurrencyIsoCode returns the corporate-currency total; the controller
    // converts it into the account's currency at the dated rate (the standard rate when there
    // are no dated rates). A corporate-currency payment on an account in another currency must
    // come back in the account's currency at that rate. The expected rates are read as the
    // billing user, the way the controller reads them.
    // A second active currency comes from a pricing data plan (qb, q3 or mfg); without one the
    // test is skipped, visibly, rather than failing the deploy.
    @isTest
    static void getBillingSummary_paymentIsConvertedToTheAccountCurrency_whenASecondCurrencyIsActive() {
        User u = billingOperationsUser();
        String corporate = corporateCurrency();
        Map<String, Decimal> effective = controllerRatesAs(u);
        String foreign = foreignCurrency(effective, corporate);
        if (foreign == null) {
            System.debug(LoggingLevel.WARN, SKIP_NO_SECOND_CURRENCY);
            return;
        }
        Account acc = newAccountOwnedBy(u, 'RLM On-Account Billing FX Test', foreign);
        Payment pmt = newProcessedPayment(acc.Id, 1000, corporate);
        Decimal balance = [SELECT Balance FROM Payment WHERE Id = :pmt.Id].Balance;
        Assert.areEqual(1000, balance, 'PRECONDITION: an unapplied processed payment\'s balance is its amount.');
        Decimal expected = balance.divide(rateOf(effective, corporate), 10, RoundingMode.HALF_UP)
            * rateOf(effective, foreign);

        Test.startTest();
        Map<String, Object> result = paymentSummaryAs(u, acc.Id, pmt.Id);
        Test.stopTest();

        Decimal actual = (Decimal) result.get('paymentBalance');
        Assert.areEqual(foreign, (String) result.get('currencyIsoCode'), 'The summary is in the account\'s currency.');
        Assert.isTrue(Math.abs(actual - expected) < 0.01,
            balance + ' ' + corporate + ' should convert to ~' + expected + ' ' + foreign + ', got ' + actual);
        Assert.areEqual(-actual, (Decimal) result.get('netAccountBalance'),
            'The converted payment balance is subtracted from the net balance.');
    }

    // When the account and the payment share a non-corporate currency, correctConversion
    // returns early (the currencies match), so the corporate-converted SUM is shown as if it
    // were in the account's currency. This pins today's behaviour; the expected value changes
    // to the payment's own amount when the controller is fixed.
    // SUM() converts at the STANDARD rate, so the currency is picked by standard rate: a
    // currency whose standard rate equals the corporate one would make the pin vacuous.
    @isTest
    static void getBillingSummary_sameNonCorporateCurrency_showsTheCorporateSum_whenASecondCurrencyIsActive() {
        String corporate = corporateCurrency();
        Map<String, Decimal> standardRates = activeRates();
        String foreign = foreignCurrency(standardRates, corporate);
        if (foreign == null) {
            System.debug(LoggingLevel.WARN, SKIP_NO_SECOND_CURRENCY);
            return;
        }
        User u = billingOperationsUser();
        Account acc = newAccountOwnedBy(u, 'RLM On-Account Billing Same Currency Test', foreign);
        Payment pmt = newProcessedPayment(acc.Id, 100, foreign);
        Decimal balance = [SELECT Balance FROM Payment WHERE Id = :pmt.Id].Balance;
        Assert.areEqual(100, balance, 'PRECONDITION: an unapplied processed payment\'s balance is its amount.');
        // SUM() converts at the standard rate, into the corporate currency.
        Decimal corporateSum = balance.divide(standardRates.get(foreign), 10, RoundingMode.HALF_UP)
            * standardRates.get(corporate);

        Test.startTest();
        Map<String, Object> result = paymentSummaryAs(u, acc.Id, pmt.Id);
        Test.stopTest();

        Decimal actual = (Decimal) result.get('paymentBalance');
        Assert.isTrue(Math.abs(actual - corporateSum) < 0.01,
            'Known gap: correctConversion returns the corporate-converted SUM when the account and payment '
            + 'share a non-corporate currency; update this test when it is fixed. Expected ~' + corporateSum
            + ' (100 ' + foreign + ' in ' + corporate + '), got ' + actual + ' ' + foreign);
    }

    // A collection plan on the account puts it in collections, for a collections user who can
    // read collection plans. The account and the plan are owned by that user.
    @isTest
    static void getBillingSummary_accountWithCollectionPlan_isInCollections() {
        User u = collectionsUser();
        Account acc = newAccountOwnedBy(u, 'RLM On-Account Billing Collections Test', null);
        // No CollectionPlanReason: with one, RLM_Create_Case_for_Collection raises a case
        // from org data a unit test cannot see.
        insert new CollectionPlan(AccountId = acc.Id, OwnerId = u.Id, UsageType = 'Billing');

        Map<String, Object> result;
        Test.startTest();
        System.runAs(u) {
            String planReadError = userModeError(COLLECTION_PLAN_READ);
            Assert.isNull(planReadError,
                'PRECONDITION: a collections user can read CollectionPlan, so its count runs: ' + planReadError);
            result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
        }
        Test.stopTest();

        Assert.areEqual(true, (Boolean) result.get('inCollections'),
            'An account with a collection plan is in collections.');
    }

    // The aggregate balance reads, and the partially-paid, written-off, dispute and collections
    // reads, swallow a query the user may not run and report zero, so a zero proves nothing by
    // itself. For a billing operations user holding RLM_BillingUI this checks, in USER_MODE,
    // that each object the summary sums or counts is readable with the fields it uses.
    // Collection plans are the exception: this role cannot read them, and the summary shows
    // "not in collections" instead of failing.
    @isTest
    static void getBillingSummary_billingOperationsUser_runsEveryBalanceQuery() {
        User u = billingOperationsUser();
        User collections = collectionsUser();
        Account acc = newAccountOwnedBy(u, 'RLM On-Account Billing Role Test', null);
        // A collection plan a collections user sees, so "not in collections" for this role comes
        // from its access, not from the account. No CollectionPlanReason (see above).
        insert new CollectionPlan(AccountId = acc.Id, OwnerId = collections.Id, UsageType = 'Billing');
        System.runAs(collections) {
            Assert.areEqual(true, (Boolean) RLM_OnAccountBillingController.getBillingSummary(acc.Id).get('inCollections'),
                'PRECONDITION: for a collections user, the account is in collections.');
        }

        Map<String, String> readErrors = new Map<String, String>();
        String collectionPlanError;
        Integer summaryQueries;
        Map<String, Object> result;
        Test.startTest();
        System.runAs(u) {
            Map<String, String> probes = new Map<String, String>{
                'Invoice' => 'SELECT Id, Balance, TotalAmountWithTax, DueDate, Status, BillingAccountId, CurrencyIsoCode FROM Invoice LIMIT 1',
                'DebitMemo' => 'SELECT Id, TotalChargeAmount, AccountId, Status, InvoiceGenerationStatus, CurrencyIsoCode FROM DebitMemo LIMIT 1',
                'CreditMemo' => 'SELECT Id, Balance, BillingAccountId, Status, CurrencyIsoCode FROM CreditMemo LIMIT 1',
                'Payment' => PAYMENT_READ,
                'Refund' => 'SELECT Id, Balance, AccountId, Status, CurrencyIsoCode FROM Refund LIMIT 1',
                'Dispute' => 'SELECT Id, Status, Invoice.BillingAccountId FROM Dispute LIMIT 1'
            };
            for (String objectName : probes.keySet()) {
                String error = userModeError(probes.get(objectName));
                if (error != null) {
                    readErrors.put(objectName, error);
                }
            }
            collectionPlanError = userModeError(COLLECTION_PLAN_READ);
            Integer queriesBefore = Limits.getQueries();
            result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
            summaryQueries = Limits.getQueries() - queriesBefore;
        }
        Test.stopTest();

        Assert.isTrue(readErrors.isEmpty(), 'PRECONDITION: the summary\'s reads run for this role: ' + readErrors);
        Assert.isNotNull(collectionPlanError, 'PRECONDITION: this role cannot read collection plans.');
        // The readErrors probes above prove the reads succeed. This bound only shows the summary
        // did not short-circuit: the account currency and the standard and dated rates (this
        // bundle is multi-currency only), the five balance aggregates and seven status reads.
        // The collection plan count is rejected for this role and does not count.
        Assert.isTrue(summaryQueries >= 15,
            'The summary runs its balance and status reads; it ran ' + summaryQueries + ' queries.');

        for (String key : new List<String>{
            'invoiceBalance', 'debitMemoBalance', 'creditMemoBalance',
            'paymentBalance', 'refundBalance', 'netAccountBalance'
        }) {
            Assert.areEqual(0, (Decimal) result.get(key), key + ' should be zero with no billing activity.');
        }
        for (String key : new List<String>{
            'totalInvoices', 'overdueCount', 'delinquentCount', 'partiallyPaidOverdueCount',
            'openWithBalance', 'writtenOffCount', 'disputeCount'
        }) {
            Assert.areEqual(0, (Integer) result.get(key), key + ' should be zero with no billing activity.');
        }
        Assert.areEqual(false, (Boolean) result.get('inCollections'),
            'A role that cannot read collection plans is shown as not in collections, though the account has one.');
    }

    private static final String COLLECTION_PLAN_READ = 'SELECT Id FROM CollectionPlan WHERE AccountId != null LIMIT 1';
    private static final String PAYMENT_READ =
        'SELECT Id, Balance, AccountId, Status, CurrencyIsoCode FROM Payment LIMIT 1';
    private static final String SKIP_NO_SECOND_CURRENCY =
        'SKIPPED: no second active currency with a different rate (a pricing data plan (qb, q3 or mfg) adds them).';

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

    // An account owned by the test user, so it is visible to that user whatever the org's
    // sharing defaults; currencyCode may be null for the default currency.
    private static Account newAccountOwnedBy(User u, String name, String currencyCode) {
        Account acc = new Account(Name = name, OwnerId = u.Id);
        if (currencyCode != null) {
            acc.put('CurrencyIsoCode', currencyCode);
        }
        insert acc;
        return acc;
    }

    // Runs the summary as the given user, after checking that user can read Payment with the
    // fields the payment balance sums, and can see the payment (Payment has no owner to set).
    private static Map<String, Object> paymentSummaryAs(User u, Id accountId, Id paymentId) {
        Map<String, Object> result;
        System.runAs(u) {
            String readError = userModeError(PAYMENT_READ);
            Assert.isNull(readError,
                'PRECONDITION: a billing operations user can read Payment, so its balance query runs: ' + readError);
            Assert.areEqual(1, [SELECT COUNT() FROM Payment WHERE Id = :paymentId WITH USER_MODE],
                'PRECONDITION: the billing operations user can see the payment.');
            result = RLM_OnAccountBillingController.getBillingSummary(accountId);
        }
        return result;
    }

    private static Payment newProcessedPayment(Id accountId, Decimal amount, String currencyCode) {
        Payment p = new Payment(
            AccountId = accountId,
            Amount = amount,
            Status = 'Processed',
            Type = 'Sale',
            ProcessingMode = 'External'
        );
        p.put('CurrencyIsoCode', currencyCode);
        insert p;
        return p;
    }

    // This module deploys only to multi-currency orgs (its controllers select CurrencyIsoCode),
    // so CurrencyType is always present.
    private static String corporateCurrency() {
        return [SELECT IsoCode FROM CurrencyType WHERE IsCorporate = true LIMIT 1].IsoCode;
    }

    private static Map<String, Decimal> activeRates() {
        Map<String, Decimal> rates = new Map<String, Decimal>();
        for (CurrencyType ct : [SELECT IsoCode, ConversionRate FROM CurrencyType WHERE IsActive = true]) {
            rates.put(ct.IsoCode, ct.ConversionRate);
        }
        return rates;
    }

    // The rates the controller converts with, read the way it reads them: as the given user, in
    // USER_MODE, an unreadable rate table treated as empty, and the standard rates used when
    // there are no dated rates for today.
    private static Map<String, Decimal> controllerRatesAs(User u) {
        Map<String, Decimal> standard = new Map<String, Decimal>();
        Map<String, Decimal> dated = new Map<String, Decimal>();
        System.runAs(u) {
            try {
                for (SObject ct : Database.query(
                    'SELECT IsoCode, ConversionRate FROM CurrencyType WHERE IsActive = true', AccessLevel.USER_MODE
                )) {
                    standard.put((String) ct.get('IsoCode'), (Decimal) ct.get('ConversionRate'));
                }
            } catch (QueryException e) {
                System.debug(LoggingLevel.INFO, 'Standard rates unreadable, as in the controller: ' + e.getMessage());
            }
            try {
                for (SObject dcr : Database.query(
                    'SELECT IsoCode, ConversionRate FROM DatedConversionRate '
                    + 'WHERE StartDate <= TODAY AND NextStartDate > TODAY', AccessLevel.USER_MODE
                )) {
                    dated.put((String) dcr.get('IsoCode'), (Decimal) dcr.get('ConversionRate'));
                }
            } catch (QueryException e) {
                System.debug(LoggingLevel.INFO, 'Dated rates unreadable, as in the controller: ' + e.getMessage());
            }
        }
        return dated.isEmpty() ? standard : dated;
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

    // Deterministic: the first active currency by ISO code whose rate in the given map differs
    // from the corporate currency's, or null when there is none.
    private static String foreignCurrency(Map<String, Decimal> rates, String corporate) {
        for (CurrencyType ct : [SELECT IsoCode FROM CurrencyType WHERE IsActive = true ORDER BY IsoCode]) {
            if (ct.IsoCode != corporate && rateOf(rates, ct.IsoCode) != rateOf(rates, corporate)) {
                return ct.IsoCode;
            }
        }
        return null;
    }

    private static Decimal rateOf(Map<String, Decimal> rates, String isoCode) {
        return rates.containsKey(isoCode) ? rates.get(isoCode) : 1;
    }
}
