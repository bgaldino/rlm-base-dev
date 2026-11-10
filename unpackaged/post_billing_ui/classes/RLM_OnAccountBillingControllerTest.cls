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
        Account acc = new Account(Name = 'RLM On-Account Billing Payment Test');
        if (corporate != null) {
            acc.put('CurrencyIsoCode', corporate);
        }
        insert acc;
        Payment pmt = newProcessedPayment(acc.Id, 250, corporate);
        Decimal balance = [SELECT Balance FROM Payment WHERE Id = :pmt.Id].Balance;
        Assert.isTrue(balance != null && balance > 0,
            'Premise: an unapplied processed payment carries a balance, got ' + balance);

        Test.startTest();
        Map<String, Object> result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
        Test.stopTest();

        Assert.areEqual(balance, (Decimal) result.get('paymentBalance'),
            'The payment balance is the processed payment\'s unapplied balance.');
        Assert.areEqual(-balance, (Decimal) result.get('netAccountBalance'),
            'With nothing else on the account, the net balance is minus the payment balance.');
        Assert.areEqual(0, (Decimal) result.get('invoiceBalance'), 'A payment adds no invoice balance.');
        Assert.areEqual(0, (Decimal) result.get('refundBalance'), 'A payment adds no refund balance.');
        if (corporate != null) {
            Assert.areEqual(corporate, (String) result.get('currencyIsoCode'),
                'The summary is shown in the account\'s currency.');
            Assert.areEqual(true, (Boolean) result.get('isMultiCurrency'), 'This org is multi-currency.');
        }
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
        if (corporate == null || foreign == null) {
            // Single-currency org, or only one active currency: there is nothing to convert.
            return;
        }
        Account acc = new Account(Name = 'RLM On-Account Billing FX Test');
        acc.put('CurrencyIsoCode', corporate);
        insert acc;
        Payment pmt = newProcessedPayment(acc.Id, 1000, foreign);
        Decimal foreignBalance = [SELECT Balance FROM Payment WHERE Id = :pmt.Id].Balance;
        Assert.isTrue(foreignBalance != null && foreignBalance > 0,
            'Premise: an unapplied processed payment carries a balance, got ' + foreignBalance);

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
        if (planType == null) {
            // Collections are not provisioned in this org variant.
            return;
        }
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

    // The summary runs every read in USER_MODE. A billing operations user holding RLM_BillingUI
    // must get a complete summary: every balance and status key present and zero for an
    // account with no billing activity, rather than a failure on one of the queries.
    @isTest
    static void getBillingSummary_billingOperationsUser_getsACompleteSummary() {
        Account acc = new Account(Name = 'RLM On-Account Billing Role Test');
        insert acc;
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });

        Map<String, Object> result;
        Test.startTest();
        System.runAs(u) {
            result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
        }
        Test.stopTest();

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
        Assert.areEqual(false, (Boolean) result.get('inCollections'), 'No collection plan -> not in collections.');
    }

    private static Payment newProcessedPayment(Id accountId, Decimal amount, String currencyCode) {
        Payment p = new Payment(
            AccountId = accountId,
            Amount = amount,
            Status = 'Processed',
            Type = 'Sale',
            ProcessingMode = 'External'
        );
        if (currencyCode != null) {
            p.put('CurrencyIsoCode', currencyCode);
        }
        insert p;
        return p;
    }

    // CurrencyType and DatedConversionRate exist only in multi-currency orgs, so they are
    // queried by name.
    private static String corporateCurrency() {
        if (!UserInfo.isMultiCurrencyOrganization()) {
            return null;
        }
        List<SObject> rows = Database.query('SELECT IsoCode FROM CurrencyType WHERE IsCorporate = true LIMIT 1');
        return rows.isEmpty() ? null : (String) rows[0].get('IsoCode');
    }

    private static Map<String, Decimal> activeRates() {
        Map<String, Decimal> rates = new Map<String, Decimal>();
        if (!UserInfo.isMultiCurrencyOrganization()) {
            return rates;
        }
        for (SObject ct : Database.query('SELECT IsoCode, ConversionRate FROM CurrencyType WHERE IsActive = true')) {
            rates.put((String) ct.get('IsoCode'), (Decimal) ct.get('ConversionRate'));
        }
        return rates;
    }

    // Dated rates exist only with advanced currency management; without it there are none.
    private static Map<String, Decimal> datedRatesToday() {
        Map<String, Decimal> rates = new Map<String, Decimal>();
        if (!Schema.getGlobalDescribe().containsKey('DatedConversionRate')) {
            return rates;
        }
        for (SObject dcr : Database.query(
            'SELECT IsoCode, ConversionRate FROM DatedConversionRate '
            + 'WHERE StartDate <= TODAY AND NextStartDate > TODAY'
        )) {
            rates.put((String) dcr.get('IsoCode'), (Decimal) dcr.get('ConversionRate'));
        }
        return rates;
    }

    private static Decimal rateOf(Map<String, Decimal> rates, String isoCode) {
        return rates.containsKey(isoCode) ? rates.get(isoCode) : 1;
    }
}
