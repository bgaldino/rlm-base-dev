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
    // balance by its balance.
    // Known gap: SUM() returns the corporate-converted total even with GROUP BY CurrencyIsoCode,
    // and correctConversion returns early when the payment and account currencies match. So
    // for an account in a non-corporate currency the summary shows the corporate-converted
    // amount in the account's currency (on a live org, a 100 AUD payment on an AUD account
    // showed as 69.92 AUD). This test pins the corporate currency and does not cover that case.
    @isTest
    static void getBillingSummary_processedPayment_lowersTheNetBalance() {
        String paymentReadError = userModeError(PAYMENT_READ);
        Assert.isNull(paymentReadError,
            'PRECONDITION: the running user can read Payment, so its balance query runs: ' + paymentReadError);
        String corporate = corporateCurrency();
        Account acc = new Account(Name = 'RLM On-Account Billing Payment Test');
        acc.put('CurrencyIsoCode', corporate);
        insert acc;
        Payment pmt = newProcessedPayment(acc.Id, 250, corporate);
        Decimal balance = [SELECT Balance FROM Payment WHERE Id = :pmt.Id].Balance;
        Assert.areEqual(250, balance, 'PRECONDITION: an unapplied processed payment\'s balance is its amount.');

        Test.startTest();
        Map<String, Object> result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
        Test.stopTest();

        Assert.areEqual(250, (Decimal) result.get('paymentBalance'),
            'The payment balance is the processed payment\'s unapplied balance.');
        Assert.areEqual(-250, (Decimal) result.get('netAccountBalance'),
            'With nothing else on the account, the net balance is minus the payment balance.');
        Assert.areEqual(corporate, (String) result.get('currencyIsoCode'),
            'The summary is shown in the account\'s currency.');
        Assert.areEqual(true, (Boolean) result.get('isMultiCurrency'), 'This org is multi-currency.');
    }

    // SUM() returns a multi-currency total in the corporate currency at the standard rate;
    // the controller undoes that and re-converts at the dated rate (the standard rate when
    // there are no dated rates). A payment in another currency must come back converted
    // into the account's currency at that rate.
    // A second active currency comes only from the qb or q3 pricing data; without one the
    // test is skipped, visibly, rather than failing the deploy.
    @isTest
    static void getBillingSummary_foreignCurrencyPayment_isConverted_whenASecondCurrencyIsActive() {
        String corporate = corporateCurrency();
        Map<String, Decimal> standardRates = activeRates();
        Map<String, Decimal> datedRates = datedRatesToday();
        Map<String, Decimal> effective = datedRates.isEmpty() ? standardRates : datedRates;
        // Deterministic: the first currency by ISO code whose effective rate differs from the
        // corporate currency's, so the payment cannot come back unconverted and still pass.
        String foreign = null;
        for (CurrencyType ct : [SELECT IsoCode FROM CurrencyType WHERE IsActive = true ORDER BY IsoCode]) {
            if (ct.IsoCode != corporate && rateOf(effective, ct.IsoCode) != rateOf(effective, corporate)) {
                foreign = ct.IsoCode;
                break;
            }
        }
        if (foreign == null) {
            System.debug(LoggingLevel.WARN,
                'SKIPPED: no second active currency with a different rate (the qb or q3 pricing data adds them).');
            return;
        }
        String paymentReadError = userModeError(PAYMENT_READ);
        Assert.isNull(paymentReadError,
            'PRECONDITION: the running user can read Payment, so its balance query runs: ' + paymentReadError);

        Account acc = new Account(Name = 'RLM On-Account Billing FX Test');
        acc.put('CurrencyIsoCode', corporate);
        insert acc;
        Payment pmt = newProcessedPayment(acc.Id, 1000, foreign);
        Decimal foreignBalance = [SELECT Balance FROM Payment WHERE Id = :pmt.Id].Balance;
        Assert.areEqual(1000, foreignBalance,
            'PRECONDITION: an unapplied processed payment\'s balance is its amount, in its own currency.');
        Decimal expected = foreignBalance.divide(rateOf(effective, foreign), 10, RoundingMode.HALF_UP)
            * rateOf(effective, corporate);

        Test.startTest();
        Map<String, Object> result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
        Test.stopTest();

        Decimal actual = (Decimal) result.get('paymentBalance');
        Assert.isTrue(Math.abs(actual - expected) < 0.01,
            foreignBalance + ' ' + foreign + ' should convert to ~' + expected + ' ' + corporate + ', got ' + actual);
        Assert.areEqual(-actual, (Decimal) result.get('netAccountBalance'),
            'The converted payment balance is subtracted from the net balance.');
    }

    // A collection plan on the account puts it in collections.
    @isTest
    static void getBillingSummary_accountWithCollectionPlan_isInCollections() {
        String planReadError = userModeError('SELECT Id, AccountId FROM CollectionPlan LIMIT 1');
        Assert.isNull(planReadError,
            'PRECONDITION: the running user can read CollectionPlan, so its count runs: ' + planReadError);
        Account acc = new Account(Name = 'RLM On-Account Billing Collections Test');
        insert acc;
        // No CollectionPlanReason: with one, RLM_Create_Case_for_Collection raises a case
        // from org data a unit test cannot see.
        insert new CollectionPlan(AccountId = acc.Id, UsageType = 'Billing');

        Test.startTest();
        Map<String, Object> result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
        Test.stopTest();

        Assert.areEqual(true, (Boolean) result.get('inCollections'),
            'An account with a collection plan is in collections.');
    }

    // The aggregate balance reads, and the partially-paid, written-off, dispute and collections
    // reads, swallow a query the user may not run and report zero, so a zero proves nothing by
    // itself. For a billing operations user holding RLM_BillingUI this checks, in USER_MODE,
    // that each object the summary sums or counts is readable with the fields it uses, and that
    // the summary ran all of its queries. Collection plans are the exception: this role cannot
    // read them, and the summary shows "not in collections" instead of failing.
    @isTest
    static void getBillingSummary_billingOperationsUser_runsEveryBalanceQuery() {
        Account acc = new Account(Name = 'RLM On-Account Billing Role Test');
        insert acc;
        // A collection plan the admin sees, so "not in collections" for this role comes from
        // its access, not from the account. No CollectionPlanReason (see above).
        insert new CollectionPlan(AccountId = acc.Id, UsageType = 'Billing');
        Assert.areEqual(true, (Boolean) RLM_OnAccountBillingController.getBillingSummary(acc.Id).get('inCollections'),
            'PRECONDITION: for the admin, the account is in collections.');
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });

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
            collectionPlanError = userModeError('SELECT Id FROM CollectionPlan WHERE AccountId != null LIMIT 1');
            Integer queriesBefore = Limits.getQueries();
            result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
            summaryQueries = Limits.getQueries() - queriesBefore;
        }
        Test.stopTest();

        Assert.isTrue(readErrors.isEmpty(), 'PRECONDITION: the summary\'s reads run for this role: ' + readErrors);
        Assert.isNotNull(collectionPlanError, 'PRECONDITION: this role cannot read collection plans.');
        // Account currency, standard and dated rates, five balance aggregates, and seven status
        // reads. The eighth status read, the collection plan count, is rejected for this role
        // before it runs, and a rejected query does not count toward the query limit.
        Assert.areEqual(SUMMARY_QUERY_COUNT, summaryQueries, 'The summary runs every read this role may run.');

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

    private static final String PAYMENT_READ =
        'SELECT Id, Balance, AccountId, Status, CurrencyIsoCode FROM Payment LIMIT 1';
    // Measured live on a Release 264 org: the reads getBillingSummary runs for a billing
    // operations user. A query USER_MODE rejects for an unsupported object (the collection plan
    // count) does not count toward the query limit. A refactor of the controller's reads must
    // update this number.
    private static final Integer SUMMARY_QUERY_COUNT = 15;

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
    // so CurrencyType and DatedConversionRate are always present.
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

    // Dated rates are kept only with advanced currency management; otherwise none cover today.
    private static Map<String, Decimal> datedRatesToday() {
        Map<String, Decimal> rates = new Map<String, Decimal>();
        for (DatedConversionRate dcr : [
            SELECT IsoCode, ConversionRate FROM DatedConversionRate
            WHERE StartDate <= TODAY AND NextStartDate > TODAY
        ]) {
            rates.put(dcr.IsoCode, dcr.ConversionRate);
        }
        return rates;
    }

    // Returns the error a USER_MODE query raises for the running user, or null if it runs.
    private static String userModeError(String soql) {
        try {
            Database.query(soql, AccessLevel.USER_MODE);
            return null;
        } catch (Exception e) {
            return e.getMessage();
        }
    }

    private static Decimal rateOf(Map<String, Decimal> rates, String isoCode) {
        return rates.containsKey(isoCode) ? rates.get(isoCode) : 1;
    }
}
