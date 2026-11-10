@isTest
private class RLM_PaymentsDataControllerTest {

    @isTest
    static void optionLists_returnSafeDefaults() {
        Test.startTest();
        String currencyCode = RLM_PaymentsDataController.getOrgDefaultCurrency();
        List<Map<String, String>> accountOptions = RLM_PaymentsDataController.getAccountOptions();
        List<Map<String, String>> currencyOptions = RLM_PaymentsDataController.getCurrencyOptions();
        Test.stopTest();

        System.assert(String.isNotBlank(currencyCode), 'A default currency code is always returned.');
        System.assert(accountOptions.size() >= 1, 'The "All Accounts" sentinel option is always present.');
        System.assertEquals('All Accounts', accountOptions[0].get('label'), 'First account option is the sentinel.');
        System.assert(currencyOptions.size() >= 1, 'The "All Currencies" sentinel option is always present.');
    }

    // The all-items branch (null filters) always returns one summary per tracked status with zero
    // totals when there is no data.
    @isTest
    static void getPaymentScheduleItems_noData_returnsZeroedSummaries() {
        Test.startTest();
        List<RLM_PaymentsDataController.PaymentStatusSummary> summaries =
            RLM_PaymentsDataController.getPaymentScheduleItems(null, null);
        Test.stopTest();

        System.assertEquals(5, summaries.size(),
            'Failed/Ready/Applied/Draft/Processing summaries are always returned.');
        for (RLM_PaymentsDataController.PaymentStatusSummary s : summaries) {
            System.assertEquals(0, s.itemCount, 'No data -> zero items for ' + s.status);
            System.assertEquals(0, s.totalRequestedAmount, 'No data -> zero total for ' + s.status);
        }
    }

    // PaymentScheduleItem is Apex-createable, so the per-status summarization can be exercised with
    // real data. Two Draft items for an account drive the account-filtered branch and addItem().
    @isTest
    static void getPaymentScheduleItems_seededDraftItems_summarized() {
        Account acc = new Account(Name = 'RLM PSI Summary Test');
        insert acc;
        PaymentSchedule ps = new PaymentSchedule(Status = 'Draft', TotalRequestedAmount = 150);
        insert ps;
        insert new List<PaymentScheduleItem>{
            new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id,
                RequestedAmount = 100, TargetPaymentProcessingDate = Date.today(), Status = 'Draft'),
            new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id,
                RequestedAmount = 50, TargetPaymentProcessingDate = Date.today(), Status = 'Draft')
        };

        Test.startTest();
        List<RLM_PaymentsDataController.PaymentStatusSummary> summaries =
            RLM_PaymentsDataController.getPaymentScheduleItems(acc.Id, null);
        Test.stopTest();

        RLM_PaymentsDataController.PaymentStatusSummary draft = null;
        for (RLM_PaymentsDataController.PaymentStatusSummary s : summaries) {
            if (s.status == 'Draft') { draft = s; }
        }
        System.assertNotEquals(null, draft, 'A Draft summary should be present.');
        System.assertEquals(2, draft.itemCount, 'Two Draft items were seeded.');
        System.assertEquals(150, draft.totalRequestedAmount, 'Draft requested total is 100 + 50.');
    }

    // PaymentScheduleItem is Apex-createable, so the account-options aggregate (GROUP BY
    // PaymentAccountId) can be exercised with real data: a seeded item's account must appear.
    @isTest
    static void getAccountOptions_withSeededItem_includesAccount() {
        Account acc = new Account(Name = 'RLM Payments Account Option Test');
        insert acc;
        PaymentSchedule ps = new PaymentSchedule(Status = 'Draft', TotalRequestedAmount = 100);
        insert ps;
        insert new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id,
            RequestedAmount = 100, TargetPaymentProcessingDate = Date.today(), Status = 'Draft');

        Test.startTest();
        List<Map<String, String>> options = RLM_PaymentsDataController.getAccountOptions();
        Test.stopTest();

        Boolean found = false;
        for (Map<String, String> option : options) {
            if (option.get('value') == String.valueOf(acc.Id)) {
                found = true;
                System.assertEquals('RLM Payments Account Option Test', option.get('label'),
                    'The account label should match the seeded account name.');
            }
        }
        System.assert(found, 'An account with a PaymentScheduleItem should appear in the options.');
        System.assert(options.size() >= 2, 'Sentinel "All Accounts" plus the seeded account.');
    }

    // PaymentLineInvoiceLine rows come only from the payment apply API, so the line-level merge
    // is exercised with in-memory rows. JSON builds them with the read-only invoice fields set.
    private static Id fakeId(Schema.SObjectType t, Integer n) {
        return Id.valueOf(t.getDescribe().getKeyPrefix() + String.valueOf(n).leftPad(12, '0'));
    }

    private static PaymentLineInvoiceLine lineApplication(Id paymentId, Id invoiceId, Decimal amount) {
        return (PaymentLineInvoiceLine) JSON.deserialize(JSON.serialize(new Map<String, Object>{
            'PaymentId' => paymentId,
            'Amount' => amount,
            'InvoiceLine' => new Map<String, Object>{
                'Invoice' => new Map<String, Object>{
                    'Id' => invoiceId, 'InvoiceNumber' => 'INV-' + invoiceId, 'TotalAmount' => 500, 'Balance' => 100
                }
            }
        }), PaymentLineInvoiceLine.class);
    }

    @isTest
    static void addLineLevelApplications_sumsLinesPerPaymentAndInvoice() {
        Id pay = fakeId(Payment.SObjectType, 1);
        Id inv1 = fakeId(Invoice.SObjectType, 1);
        Id inv2 = fakeId(Invoice.SObjectType, 2);
        Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>> m =
            new Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>>();

        RLM_PaymentsDataController.addLineLevelApplications(m, new List<PaymentLineInvoiceLine>{
            lineApplication(pay, inv1, 250), lineApplication(pay, inv1, 150), lineApplication(pay, inv2, 50)
        });

        System.assertEquals(2, m.get(pay).size(), 'One entry per invoice.');
        Map<Id, Decimal> applied = new Map<Id, Decimal>();
        for (RLM_PaymentsDataController.InvoiceWrapper iw : m.get(pay)) applied.put(iw.id, iw.appliedAmount);
        System.assertEquals(400, applied.get(inv1), 'Two lines of one invoice are summed.');
        System.assertEquals(50, applied.get(inv2), 'A second invoice keeps its own total.');
        System.assertEquals(100, m.get(pay)[0].balance, 'Invoice fields come from the related invoice.');
    }

    @isTest
    static void addLineLevelApplications_addsToHeaderLevelEntry() {
        Id pay = fakeId(Payment.SObjectType, 1);
        Id inv = fakeId(Invoice.SObjectType, 1);
        RLM_PaymentsDataController.InvoiceWrapper header = new RLM_PaymentsDataController.InvoiceWrapper(
            (Invoice) JSON.deserialize(JSON.serialize(new Map<String, Object>{ 'Id' => inv, 'Balance' => 100 }), Invoice.class));
        header.appliedAmount = 30;
        Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>> m =
            new Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>>{
                pay => new List<RLM_PaymentsDataController.InvoiceWrapper>{ header }
            };

        RLM_PaymentsDataController.addLineLevelApplications(m, new List<PaymentLineInvoiceLine>{ lineApplication(pay, inv, 20) });

        System.assertEquals(1, m.get(pay).size(), 'The invoice is listed once.');
        System.assertEquals(50, m.get(pay)[0].appliedAmount, 'Header 30 plus line 20.');
    }

    @isTest
    static void addHeaderLevelApplications_sumsRepeatApplicationsOfOneInvoice() {
        Id pay = fakeId(Payment.SObjectType, 1);
        Id inv = fakeId(Invoice.SObjectType, 1);
        List<PaymentLineInvoice> rows = new List<PaymentLineInvoice>();
        for (Decimal amount : new List<Decimal>{ 30, 45 }) {
            rows.add((PaymentLineInvoice) JSON.deserialize(JSON.serialize(new Map<String, Object>{
                'PaymentId' => pay, 'InvoiceId' => inv, 'Amount' => amount,
                'Invoice' => new Map<String, Object>{ 'Id' => inv, 'Balance' => 25, 'TotalAmount' => 100 }
            }), PaymentLineInvoice.class));
        }
        Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>> m =
            new Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>>();

        RLM_PaymentsDataController.addHeaderLevelApplications(m, rows);

        System.assertEquals(1, m.get(pay).size(), 'Two applications to one invoice are listed once.');
        System.assertEquals(75, m.get(pay)[0].appliedAmount, '30 + 45.');
        System.assertEquals(25, m.get(pay)[0].balance, 'Invoice fields come from the related invoice.');
    }

    @isTest
    static void addLineLevelApplications_skipsRowsWithoutAReadableInvoice() {
        Id pay = fakeId(Payment.SObjectType, 1);
        PaymentLineInvoiceLine orphan = (PaymentLineInvoiceLine) JSON.deserialize(
            JSON.serialize(new Map<String, Object>{ 'PaymentId' => pay, 'Amount' => 10 }), PaymentLineInvoiceLine.class);
        Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>> m =
            new Map<Id, List<RLM_PaymentsDataController.InvoiceWrapper>>();

        RLM_PaymentsDataController.addLineLevelApplications(m, new List<PaymentLineInvoiceLine>{ orphan });

        System.assert(m.isEmpty(), 'A row without its invoice is skipped, not a NullPointerException.');
    }

    // The two currency-filtered queries: with and without an account. An item in the user's
    // currency is kept under that currency and left out under any other.
    @isTest
    static void getPaymentScheduleItems_filtersByCurrencyWithAndWithoutAccount() {
        Account acc = new Account(Name = 'RLM PSI Currency Test');
        insert acc;
        PaymentSchedule ps = new PaymentSchedule(Status = 'Draft', TotalRequestedAmount = 80);
        insert ps;
        PaymentScheduleItem psi = new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id,
            RequestedAmount = 80, TargetPaymentProcessingDate = Date.today(), Status = 'Draft');
        insert psi;
        String userCurrency = UserInfo.getDefaultCurrency();
        String otherCurrency = anotherCurrency(userCurrency);
        Assert.areEqual(userCurrency, [SELECT CurrencyIsoCode FROM PaymentScheduleItem WHERE Id = :psi.Id].CurrencyIsoCode,
            'PRECONDITION: the item is in the user\'s currency.');

        Test.startTest();
        RLM_PaymentsDataController.PaymentStatusSummary accountInCurrency =
            draft(RLM_PaymentsDataController.getPaymentScheduleItems(acc.Id, userCurrency));
        RLM_PaymentsDataController.PaymentStatusSummary anyAccountInCurrency =
            draft(RLM_PaymentsDataController.getPaymentScheduleItems(null, userCurrency));
        RLM_PaymentsDataController.PaymentStatusSummary accountElsewhere =
            draft(RLM_PaymentsDataController.getPaymentScheduleItems(acc.Id, otherCurrency));
        RLM_PaymentsDataController.PaymentStatusSummary anyAccountElsewhere =
            draft(RLM_PaymentsDataController.getPaymentScheduleItems(null, otherCurrency));
        Test.stopTest();

        Assert.areEqual(1, accountInCurrency.itemCount, 'Account and currency both match.');
        assertAmount(80, accountInCurrency.totalRequestedAmount, 'The item\'s requested amount.');
        Assert.areEqual(userCurrency, accountInCurrency.items[0].currencyCode, 'The item carries its currency.');
        Assert.areEqual(1, anyAccountInCurrency.itemCount, 'The currency alone matches.');
        Assert.areEqual(0, accountElsewhere.itemCount,
            'Under ' + otherCurrency + ' the account\'s item is left out.');
        Assert.areEqual(0, anyAccountElsewhere.itemCount, 'Under ' + otherCurrency + ' no item matches.');
        assertAmount(0, anyAccountElsewhere.totalRequestedAmount, 'Nothing requested in another currency.');
    }

    // An item linked to a payment shows that payment and its own amounts. The schedule is a
    // promise to pay on a collection plan, so the schedule-reference and payment-application
    // lookups run for coverage; no invoice can exist in a unit test, so what they list is
    // verified live.
    @isTest
    static void getPaymentScheduleItems_showsTheItemsPayment() {
        Account acc = new Account(Name = 'RLM PSI Payment Test');
        insert acc;
        Payment pmt = new Payment(AccountId = acc.Id, Amount = 60, Status = 'Processed',
            Type = 'Sale', ProcessingMode = 'External');
        insert pmt;
        CollectionPlan plan = new CollectionPlan(AccountId = acc.Id);
        plan.put('UsageType', 'Billing');
        insert plan;
        PaymentSchedule promise = new PaymentSchedule(
            ReferenceEntityId = plan.Id,
            Type = 'PromiseToPay',
            UsageType = 'CollectionPlan',
            Status = 'Draft',
            TotalRequestedAmount = 60
        );
        insert promise;
        insert new PaymentScheduleItem(PaymentScheduleId = promise.Id, PaymentAccountId = acc.Id,
            PaymentId = pmt.Id, RequestedAmount = 60, TargetPaymentProcessingDate = Date.today(), Status = 'Draft');

        Test.startTest();
        RLM_PaymentsDataController.PaymentStatusSummary summary =
            draft(RLM_PaymentsDataController.getPaymentScheduleItems(acc.Id, null));
        Test.stopTest();

        Assert.areEqual(1, summary.itemCount, 'One Draft item.');
        RLM_PaymentsDataController.PaymentItemWrapper item = summary.items[0];
        Assert.areEqual(pmt.Id, item.paymentId, 'The item shows its payment.');
        Assert.isTrue(item.hasPayment, 'The item has a payment.');
        assertAmount(60, item.requestedAmount, 'The requested amount.');
        Assert.areEqual(Date.today(), item.targetDate, 'The target processing date.');
    }

    // Only the five tracked statuses are summarized; an item in any other is left out.
    @isTest
    static void getPaymentScheduleItems_leavesOutUntrackedStatuses() {
        Account acc = new Account(Name = 'RLM PSI Canceled Test');
        insert acc;
        PaymentSchedule ps = new PaymentSchedule(Status = 'Draft', TotalRequestedAmount = 50);
        insert ps;
        // Items are created Draft; Canceled is a status a user may set afterwards. The Draft
        // item shows the account's items are read, so only the Canceled one is left out.
        PaymentScheduleItem psi = new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id,
            RequestedAmount = 30, TargetPaymentProcessingDate = Date.today(), Status = 'Draft');
        PaymentScheduleItem kept = new PaymentScheduleItem(PaymentScheduleId = ps.Id, PaymentAccountId = acc.Id,
            RequestedAmount = 20, TargetPaymentProcessingDate = Date.today(), Status = 'Draft');
        insert new List<PaymentScheduleItem>{ psi, kept };
        // Update the status alone: the item's other fields are not all updateable.
        update new PaymentScheduleItem(Id = psi.Id, Status = 'Canceled');
        Assert.areEqual('Canceled', [SELECT Status FROM PaymentScheduleItem WHERE Id = :psi.Id].Status,
            'PRECONDITION: the item is Canceled.');

        Test.startTest();
        List<RLM_PaymentsDataController.PaymentStatusSummary> summaries =
            RLM_PaymentsDataController.getPaymentScheduleItems(acc.Id, null);
        Test.stopTest();

        Integer summarized = 0;
        for (RLM_PaymentsDataController.PaymentStatusSummary s : summaries) {
            summarized += s.itemCount;
        }
        Assert.areEqual(1, summarized, 'Of the two items only the Draft one is summarized.');
        Assert.areEqual(kept.Id, draft(summaries).items[0].id, 'The summarized item is the Draft one.');
    }

    // Each tracked status carries its theme and icon; any other status gets the defaults.
    @isTest
    static void paymentStatusSummary_stylesEachStatus() {
        Map<String, String> themes = new Map<String, String>{
            'Failed' => 'slds-theme_error',
            'Ready for Processing' => 'slds-theme_warning',
            'Applied' => 'slds-theme_success',
            'Draft' => 'slds-theme_info',
            'Processing' => 'slds-theme_alt-inverse'
        };
        Map<String, String> icons = new Map<String, String>{
            'Failed' => 'utility:error',
            'Ready for Processing' => 'utility:clock',
            'Applied' => 'utility:success',
            'Draft' => 'utility:edit',
            'Processing' => 'utility:sync'
        };

        Test.startTest();
        List<RLM_PaymentsDataController.PaymentStatusSummary> summaries =
            RLM_PaymentsDataController.getPaymentScheduleItems(null, null);
        RLM_PaymentsDataController.PaymentStatusSummary untracked =
            new RLM_PaymentsDataController.PaymentStatusSummary('Canceled');
        Test.stopTest();

        Set<String> seen = new Set<String>();
        for (RLM_PaymentsDataController.PaymentStatusSummary s : summaries) {
            seen.add(s.status);
            Assert.areEqual(themes.get(s.status), s.statusClass, 'Theme for ' + s.status);
            Assert.areEqual(icons.get(s.status), s.iconName, 'Icon for ' + s.status);
        }
        Assert.areEqual(themes.keySet(), seen, 'One summary per tracked status.');
        Assert.areEqual('slds-theme_default', untracked.statusClass, 'An untracked status gets the default theme.');
        Assert.areEqual('utility:moneybag', untracked.iconName, 'An untracked status gets the default icon.');
        Assert.areEqual(0, untracked.itemCount, 'A new summary is empty.');
    }

    // An invoice is settled when it has no balance left, or no balance recorded.
    @isTest
    static void invoiceWrapper_isSettledOnlyWithoutABalance() {
        Id inv = fakeId(Invoice.SObjectType, 1);
        RLM_PaymentsDataController.InvoiceWrapper openInvoice = invoiceWithBalance(inv, 100);
        RLM_PaymentsDataController.InvoiceWrapper paid = invoiceWithBalance(inv, 0);
        RLM_PaymentsDataController.InvoiceWrapper unknown = invoiceWithBalance(inv, null);

        Assert.isFalse(openInvoice.isSettled, 'A balance of 100 is open.');
        Assert.isTrue(paid.isSettled, 'A zero balance is settled.');
        Assert.isTrue(unknown.isSettled, 'No balance is treated as settled.');
        Assert.isNull(openInvoice.appliedAmount, 'An invoice read directly has no applied amount.');
    }

    private static RLM_PaymentsDataController.InvoiceWrapper invoiceWithBalance(Id invoiceId, Decimal balance) {
        Map<String, Object> fields = new Map<String, Object>{ 'Id' => invoiceId };
        if (balance != null) {
            fields.put('Balance', balance);
        }
        return new RLM_PaymentsDataController.InvoiceWrapper(
            (Invoice) JSON.deserialize(JSON.serialize(fields), Invoice.class));
    }

    private static RLM_PaymentsDataController.PaymentStatusSummary draft(
        List<RLM_PaymentsDataController.PaymentStatusSummary> summaries) {
        for (RLM_PaymentsDataController.PaymentStatusSummary s : summaries) {
            if (s.status == 'Draft') {
                return s;
            }
        }
        Assert.fail('No Draft summary returned.');
        return null;
    }

    // An active currency other than the given one; a code no record can carry if there is none.
    // The controller lists CurrencyType, so this module only deploys to a multi-currency org.
    private static String anotherCurrency(String isoCode) {
        List<CurrencyType> others = [
            SELECT IsoCode FROM CurrencyType WHERE IsActive = true AND IsoCode != :isoCode LIMIT 1
        ];
        return others.isEmpty() ? 'ZZZ' : others[0].IsoCode;
    }

    // Compares amounts by value, so 0 and 0.00 match.
    private static void assertAmount(Decimal expected, Decimal actual, String message) {
        Assert.isTrue(actual != null && actual == expected,
            message + ' Expected ' + expected + ', got ' + actual + '.');
    }
}
