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

    // Checks that, as the admin, the summary for an account with no billing records returns
    // zero balances and clean status flags. Most reads (the aggregate balances and the
    // partially-paid, written-off, dispute and collection reads) are swallowed into zeros when
    // they fail, so this does not prove they run; the four Invoice counts and the account
    // currency read would throw instead. getBillingSummary_billingOperationsUser_runsEachReadButCollectionPlans
    // is the proof that the reads run.
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
    // balance by its balance. (A non-corporate account currency is covered below, when one is
    // active.)
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
    // come back in the account's currency at that rate.
    // A second active currency with an effective rate different from the corporate one comes
    // from a pricing data plan (qb, q3 or mfg); without one the test is skipped, visibly,
    // rather than failing the deploy.
    @isTest
    static void getBillingSummary_paymentIsConvertedToTheAccountCurrency_whenASecondCurrencyIsActive() {
        String corporate = corporateCurrency();
        // The currency is picked from the effective rates the admin reads (dated if any, else
        // standard); the billing user's rates must then match them, so a rate table that user
        // cannot read fails the precondition instead of skipping.
        Map<String, Decimal> adminRates = effectiveRates(AccessLevel.SYSTEM_MODE);
        String foreign = foreignCurrency(adminRates, corporate);
        if (foreign == null) {
            System.debug(LoggingLevel.WARN, SKIP_NO_SECOND_CURRENCY);
            return;
        }
        User u = billingOperationsUser();
        // Dated rates exist only with advanced currency management. If the admin reads dated
        // rates for these codes but the billing user cannot read the table (its rates fall back
        // to standard), skip visibly rather than fail the deploy over that optional feature.
        Map<String, Decimal> adminDated = datedRates(AccessLevel.SYSTEM_MODE);
        if ((adminDated.containsKey(foreign) || adminDated.containsKey(corporate)) && datedRatesAs(u).isEmpty()) {
            System.debug(LoggingLevel.WARN, 'SKIPPED: DatedConversionRate is not readable for the billing user');
            return;
        }
        Map<String, Decimal> effective = userRatesMatchingAdmin(u, adminRates, new List<String>{ foreign, corporate });
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

    // The controller's standard-rate undo step (for a payment in a non-corporate currency) is
    // only observable when dated rates differ from standard rates, which needs advanced
    // currency management, so it is not tested here.

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
        Assert.areEqual(foreign, (String) result.get('currencyIsoCode'),
            'PRECONDITION: the summary is labelled in the account\'s (non-corporate) currency.');
        // SUM() rounds the corporate total to the corporate currency's decimal places.
        Integer decimalPlaces = [SELECT DecimalPlaces FROM CurrencyType WHERE IsoCode = :corporate LIMIT 1].DecimalPlaces;
        Decimal tolerance = Math.max(0.01, 0.5 * Math.pow(10, -decimalPlaces));
        Assert.isTrue(Math.abs(actual - corporateSum) < tolerance,
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
        insert new CollectionPlan(AccountId = acc.Id, OwnerId = u.Id);

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
    // itself. For a billing operations user holding RLM_BillingUI this runs, in USER_MODE, a
    // probe of each read the summary makes (account currency, standard rates, and each object
    // it sums or counts, with the fields it uses); those probes are the evidence that this role
    // can run the summary's reads. Dated rates are left out: that table exists only with
    // advanced currency management, and the controller treats an unreadable one as empty.
    // Collection plans are the exception: this role cannot read them, and the summary shows
    // "not in collections" instead of failing.
    @isTest
    static void getBillingSummary_billingOperationsUser_runsEachReadButCollectionPlans() {
        User u = billingOperationsUser();
        Account acc = newAccountOwnedBy(u, 'RLM On-Account Billing Role Test', null);
        // A collection plan on the account, so "not in collections" for this role comes from its
        // access, not from the account. No CollectionPlanReason (see above).
        insert new CollectionPlan(AccountId = acc.Id);
        Assert.areEqual(1, [SELECT COUNT() FROM CollectionPlan WHERE AccountId = :acc.Id],
            'PRECONDITION: the account has a collection plan.');

        Map<String, String> readErrors = new Map<String, String>();
        String collectionPlanError;
        Map<String, Object> result;
        Test.startTest();
        System.runAs(u) {
            Map<String, String> probes = new Map<String, String>{
                'Account' => 'SELECT Id, CurrencyIsoCode FROM Account LIMIT 1',
                'CurrencyType' => 'SELECT IsoCode, ConversionRate FROM CurrencyType WHERE IsActive = true LIMIT 1',
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
            result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
        }
        Test.stopTest();

        Assert.isTrue(readErrors.isEmpty(), 'PRECONDITION: the summary\'s reads run for this role: ' + readErrors);
        Assert.isNotNull(collectionPlanError, 'PRECONDITION: this role cannot read collection plans.');
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

    // The effective rates as the given user reads them in USER_MODE: dated rates for today if
    // there are any, else the standard rates (the controller's rule). Only QueryException is
    // caught; an unreadable table changes the result, which userRatesMatchingAdmin then fails.
    private static Map<String, Decimal> effectiveRatesAs(User u) {
        Map<String, Decimal> rates;
        System.runAs(u) {
            rates = effectiveRates(AccessLevel.USER_MODE);
        }
        return rates;
    }

    // The billing user's effective rates, after asserting that for each given code both its
    // effective rate and its standard (CurrencyType) rate equal the admin's: a rate table the
    // user cannot read (an empty map, or dated rates silently falling back to standard ones)
    // then fails as a precondition.
    private static Map<String, Decimal> userRatesMatchingAdmin(
        User u, Map<String, Decimal> adminRates, List<String> codes
    ) {
        Map<String, Decimal> userRates = effectiveRatesAs(u);
        Map<String, Decimal> adminStandard = activeRates();
        Map<String, Decimal> userStandard = new Map<String, Decimal>();
        System.runAs(u) {
            for (SObject ct : Database.query(
                'SELECT IsoCode, ConversionRate FROM CurrencyType WHERE IsActive = true', AccessLevel.USER_MODE
            )) {
                userStandard.put((String) ct.get('IsoCode'), (Decimal) ct.get('ConversionRate'));
            }
        }
        for (String code : codes) {
            Assert.areEqual(adminRates.get(code), userRates.get(code),
                'PRECONDITION: the billing user reads the same effective rate for ' + code + ' as the admin.');
            Assert.areEqual(adminStandard.get(code), userStandard.get(code),
                'PRECONDITION: the billing user reads the same standard rate for ' + code + ' as the admin.');
        }
        return userRates;
    }

    // Dated rates for today if there are any, else the standard rates, read at the given level.
    private static Map<String, Decimal> effectiveRates(AccessLevel level) {
        Map<String, Decimal> dated = datedRates(level);
        if (!dated.isEmpty()) {
            return dated;
        }
        Map<String, Decimal> standard = new Map<String, Decimal>();
        try {
            for (SObject ct : Database.query(
                'SELECT IsoCode, ConversionRate FROM CurrencyType WHERE IsActive = true', level
            )) {
                standard.put((String) ct.get('IsoCode'), (Decimal) ct.get('ConversionRate'));
            }
        } catch (QueryException e) {
            System.debug(LoggingLevel.INFO, 'Standard rates unreadable: ' + e.getMessage());
        }
        return standard;
    }

    // Today's dated rates read at the given level; empty without advanced currency management
    // or when the table is unreadable.
    private static Map<String, Decimal> datedRates(AccessLevel level) {
        Map<String, Decimal> dated = new Map<String, Decimal>();
        try {
            for (SObject dcr : Database.query(
                'SELECT IsoCode, ConversionRate FROM DatedConversionRate '
                + 'WHERE StartDate <= TODAY AND NextStartDate > TODAY', level
            )) {
                dated.put((String) dcr.get('IsoCode'), (Decimal) dcr.get('ConversionRate'));
            }
        } catch (QueryException e) {
            System.debug(LoggingLevel.INFO, 'Dated rates unreadable: ' + e.getMessage());
        }
        return dated;
    }

    // Today's dated rates as the given user reads them in USER_MODE.
    private static Map<String, Decimal> datedRatesAs(User u) {
        Map<String, Decimal> dated;
        System.runAs(u) {
            dated = datedRates(AccessLevel.USER_MODE);
        }
        return dated;
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
