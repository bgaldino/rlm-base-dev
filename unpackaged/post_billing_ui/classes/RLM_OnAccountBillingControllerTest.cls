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

    // Invoices/DebitMemos/CreditMemos/Payments/Refunds are system-managed and not insertable
    // in Apex tests. An Account with no billing activity drives every aggregate and count down
    // its empty path, verifying the summary returns zero balances and clean status flags.
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

    // Payment, unlike invoices and memos, is Apex-createable. A processed payment in the
    // account's own currency is summed as is and lowers the net balance by its balance.
    @isTest
    static void getBillingSummary_processedPayment_lowersTheNetBalance() {
        String corporate = corporateCurrency();
        Assert.isNotNull(corporate, 'PRECONDITION: the org has a corporate currency.');
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
        Assert.areEqual(0, (Decimal) result.get('invoiceBalance'), 'A payment adds no invoice balance.');
        Assert.areEqual(0, (Decimal) result.get('refundBalance'), 'A payment adds no refund balance.');
        Assert.areEqual(corporate, (String) result.get('currencyIsoCode'),
            'The summary is shown in the account\'s currency.');
        Assert.areEqual(true, (Boolean) result.get('isMultiCurrency'), 'This org is multi-currency.');
    }

    // SUM() returns a multi-currency total in the corporate currency at the standard rate;
    // the controller undoes that and re-converts at the dated rate (the standard rate when
    // there are no dated rates). A payment in another currency must come back converted
    // into the account's currency at that rate.
    @isTest
    static void getBillingSummary_foreignCurrencyPayment_isConvertedToTheAccountCurrency() {
        String corporate = corporateCurrency();
        Map<String, Decimal> standardRates = activeRates();
        String foreign = null;
        for (String iso : standardRates.keySet()) {
            if (iso != corporate) {
                foreign = iso;
                break;
            }
        }
        Assert.isNotNull(corporate, 'PRECONDITION: the org has a corporate currency.');
        Assert.isNotNull(foreign, 'PRECONDITION: a second active currency exists to convert from.');
        Account acc = new Account(Name = 'RLM On-Account Billing FX Test');
        acc.put('CurrencyIsoCode', corporate);
        insert acc;
        Payment pmt = newProcessedPayment(acc.Id, 1000, foreign);
        Decimal foreignBalance = [SELECT Balance FROM Payment WHERE Id = :pmt.Id].Balance;
        Assert.areEqual(1000, foreignBalance,
            'PRECONDITION: an unapplied processed payment\'s balance is its amount, in its own currency.');

        Map<String, Decimal> datedRates = datedRatesToday();
        Map<String, Decimal> effective = datedRates.isEmpty() ? standardRates : datedRates;
        Decimal expected = foreignBalance.divide(rateOf(effective, foreign), 10, RoundingMode.HALF_UP)
            * rateOf(effective, corporate);

        Test.startTest();
        Map<String, Object> result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
        Test.stopTest();

        Decimal actual = (Decimal) result.get('paymentBalance');
        Assert.isNotNull(actual, 'A payment balance is always returned.');
        Assert.isTrue(Math.abs(actual - expected) < 0.01,
            foreignBalance + ' ' + foreign + ' should convert to ~' + expected + ' ' + corporate + ', got ' + actual);
        Assert.areEqual(-actual, (Decimal) result.get('netAccountBalance'),
            'The converted payment balance is subtracted from the net balance.');
    }

    // A collection plan on the account puts it in collections.
    @isTest
    static void getBillingSummary_accountWithCollectionPlan_isInCollections() {
        Account acc = new Account(Name = 'RLM On-Account Billing Collections Test');
        insert acc;
        Schema.SObjectType planType = Schema.getGlobalDescribe().get('CollectionPlan');
        Assert.isNotNull(planType, 'PRECONDITION: collection plans exist in this org (RLM_BillingUI grants them).');
        // No CollectionPlanReason: with one, RLM_Create_Case_for_Collection raises a case
        // from org data a unit test cannot see.
        SObject plan = planType.newSObject();
        plan.put('AccountId', acc.Id);
        plan.put('UsageType', 'Billing');
        insert plan;

        Test.startTest();
        Map<String, Object> result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
        Test.stopTest();

        Assert.areEqual(true, (Boolean) result.get('inCollections'),
            'An account with a collection plan is in collections.');
        Assert.areEqual(0, (Integer) result.get('totalInvoices'), 'A collection plan adds no invoices.');
    }

    // The balance and status reads swallow a query the user may not run and report zero, so
    // a zero proves nothing by itself. For a billing operations user holding RLM_BillingUI
    // this checks, in USER_MODE, that each object the summary sums or counts is readable with
    // the fields it uses, so its zeros come from running the queries. Collection plans are the
    // exception: this role cannot read them, and the summary shows "not in collections"
    // instead of failing.
    @isTest
    static void getBillingSummary_billingOperationsUser_runsEveryBalanceQuery() {
        Account acc = new Account(Name = 'RLM On-Account Billing Role Test');
        insert acc;
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });

        Map<String, String> readErrors = new Map<String, String>();
        String collectionPlanError;
        Map<String, Object> result;
        Test.startTest();
        System.runAs(u) {
            Map<String, String> probes = new Map<String, String>{
                'Invoice' => 'SELECT Id, Balance, TotalAmountWithTax, DueDate, Status, BillingAccountId, CurrencyIsoCode FROM Invoice LIMIT 1',
                'DebitMemo' => 'SELECT Id, TotalChargeAmount, AccountId, Status, InvoiceGenerationStatus, CurrencyIsoCode FROM DebitMemo LIMIT 1',
                'CreditMemo' => 'SELECT Id, Balance, BillingAccountId, Status, CurrencyIsoCode FROM CreditMemo LIMIT 1',
                'Payment' => 'SELECT Id, Balance, AccountId, Status, CurrencyIsoCode FROM Payment LIMIT 1',
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
            'A role that cannot read collection plans is shown as not in collections.');
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
    // so CurrencyType and DatedConversionRate are always present.
    private static String corporateCurrency() {
        List<CurrencyType> rows = [SELECT IsoCode FROM CurrencyType WHERE IsCorporate = true LIMIT 1];
        return rows.isEmpty() ? null : rows[0].IsoCode;
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
