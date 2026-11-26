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
    // zero balances and clean status flags. A refused balance or status read returns null, not
    // zero or false (see the refused-read tests below), so these zeros show the reads ran. See
    // getBillingSummary_billingOperationsUser_canRunEachSummaryReadButCollectionPlans for a role.
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
    }

    // SUM() with GROUP BY CurrencyIsoCode returns the corporate-currency total; the controller
    // converts it into the account's currency at each currency's dated rate (its standard rate
    // when it has no dated rate: the controller's effectiveRate rule). A corporate-currency payment on an account in another currency must
    // come back in the account's currency at that rate.
    // A second active currency with an effective rate different from the corporate one comes
    // from a pricing data plan (qb, q3 or mfg); without one the test is skipped, visibly,
    // rather than failing the deploy.
    // Not covered: the controller's standard-rate undo step. This corporate-to-foreign direction
    // never exercises it, because the corporate rate is 1; and without advanced currency
    // management the undo and the re-conversion cancel for any direction.
    @isTest
    static void getBillingSummary_paymentIsConvertedToTheAccountCurrency_whenASecondCurrencyIsActive() {
        String corporate = corporateCurrency();
        // The currency is picked from the effective rates the admin reads (dated if any, else
        // standard). Dated rates the billing user cannot read are skipped visibly below;
        // differing standard rates, or a partial read, fail as a precondition.
        Map<String, Decimal> adminRates = effectiveRates(AccessLevel.SYSTEM_MODE);
        String foreign = foreignCurrency(adminRates, corporate);
        if (foreign == null) {
            System.debug(LoggingLevel.WARN, SKIP_NO_SECOND_CURRENCY);
            return;
        }
        User u = billingOperationsUser();
        // Dated rates exist only with advanced currency management. If the admin reads dated
        // rates for these codes but the billing user cannot read the table (the controller then
        // refuses with its fixed rates sentence), skip visibly rather than fail the deploy over
        // that optional feature.
        Map<String, Decimal> adminDated = datedRates(AccessLevel.SYSTEM_MODE);
        if ((adminDated.containsKey(foreign) || adminDated.containsKey(corporate)) && datedRatesAs(u).isEmpty()) {
            System.debug(LoggingLevel.WARN, SKIP_DATED_RATES_UNREADABLE);
            return;
        }
        Map<String, Decimal> effective = userRatesMatchingAdmin(u, adminRates, new List<String>{ foreign, corporate });
        Account acc = newAccountOwnedBy(u, 'RLM On-Account Billing FX Test', foreign);
        Payment pmt = newProcessedPayment(acc.Id, 1000, corporate);
        Decimal balance = [SELECT Balance FROM Payment WHERE Id = :pmt.Id].Balance;
        Assert.areEqual(1000, balance, 'PRECONDITION: an unapplied processed payment\'s balance is its amount.');
        Decimal expected = balance.divide(rateOf(effective, corporate), 10, RoundingMode.HALF_UP)
            * rateOf(effective, foreign);
        if (Math.abs(expected - balance) <= 0.01) {
            System.debug(LoggingLevel.WARN, SKIP_RATE_TOO_CLOSE);
            return;
        }

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
    // were in the account's currency. This pins accepted behaviour (owner decision 2026-11-25, pack
    // 433); the expected value changes only if the controller is deliberately changed.
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
        // SUM() rounds the corporate total to the corporate currency's decimal places.
        Integer decimalPlaces = [SELECT DecimalPlaces FROM CurrencyType WHERE IsoCode = :corporate LIMIT 1].DecimalPlaces;
        Decimal tolerance = Math.max(0.01, 0.5 * Math.pow(10, -decimalPlaces));
        if (Math.abs(corporateSum - balance) <= tolerance) {
            System.debug(LoggingLevel.WARN, SKIP_RATE_TOO_CLOSE);
            return;
        }

        Test.startTest();
        Map<String, Object> result = paymentSummaryAs(u, acc.Id, pmt.Id);
        Test.stopTest();

        Decimal actual = (Decimal) result.get('paymentBalance');
        Assert.areEqual(foreign, (String) result.get('currencyIsoCode'),
            'PRECONDITION: the summary is labelled in the account\'s (non-corporate) currency.');
        Assert.isTrue(Math.abs(actual - corporateSum) <= tolerance,
            'Accepted behaviour: correctConversion returns the corporate-converted SUM when the account and payment '
            + 'share a non-corporate currency; update this test only if that is changed. Expected ~' + corporateSum
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

    // A refused balance or status read is null, not zero or false, so the zeros below show the reads
    // ran. For a billing operations user holding RLM_BillingUI this also runs, in USER_MODE, a
    // probe of each read the summary makes (account currency, standard rates, and each object
    // it sums or counts, with the fields it uses); those probes are the evidence that this role
    // can run the summary's reads. Dated rates are left out: that table has rows only with
    // advanced currency management; without them an unreadable table reads as empty, and with them
    // the controller refuses with its fixed rates sentence (see loadDatedRates).
    // Collection plans are the exception: this role on its own (without the standalone
    // RLM_BillingCollectionsRead set, next test) cannot read them, so the summary reports
    // collections as unavailable (null), not "not in collections", and does not fail. Measured on a
    // 264 org (2026-11-26): RLM_BillingUI's CollectionPlan read grant does not make it readable;
    // CollectionPlan also needs the Collections and Recovery Specialist user permission, which the
    // user license refuses ("doesn't allow the permission") without the Billing Advanced license.
    @isTest
    static void getBillingSummary_billingOperationsUser_canRunEachSummaryReadButCollectionPlans() {
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
                'CurrencyType' => 'SELECT IsoCode, ConversionRate FROM CurrencyType LIMIT 1',
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
        Assert.isTrue(result.containsKey('inCollections'), 'inCollections is returned.');
        Assert.isNull(result.get('inCollections'),
            'A role that cannot read collection plans gets collections as unavailable, not "not in collections" '
            + '(the account has a plan).');
    }

    // Each billing persona (its group, RLM_BillingUI, the standalone RLM_BillingCollectionsRead set,
    // Billing and Billing Advanced licenses; owner decision, todo 452) reads collection plans, so an
    // account with a plan is in collections (the pill reads "In Collections"), not unavailable.
    // The admin owns the plan: CollectionPlan's internal org-wide default is Public Read/Write
    // (EntityDefinition.InternalSharingModel = ReadWrite, measured 2026-11-26 on this 264 org and, by
    // the orchestrator, on both build orgs), so a plan the persona does not own still counts.
    // Skipped visibly where the personas bundle is not deployed.
    @isTest
    static void getBillingSummary_eachBillingPersonaWithTheCollectionsSet_readsCollectionPlans() {
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
            Account acc = newAccountOwnedBy(personas.get(groupName), 'RLM On-Account ' + groupName, null);
            insert new CollectionPlan(AccountId = acc.Id);
            accountByGroup.put(groupName, acc.Id);
        }

        Map<String, String> readErrors = new Map<String, String>();
        Map<String, Map<String, Object>> results = new Map<String, Map<String, Object>>();
        Test.startTest();
        for (String groupName : personas.keySet()) {
            System.runAs(personas.get(groupName)) {
                readErrors.put(groupName, userModeError(COLLECTION_PLAN_READ));
                results.put(groupName, RLM_OnAccountBillingController.getBillingSummary(accountByGroup.get(groupName)));
            }
        }
        Test.stopTest();

        for (String groupName : personas.keySet()) {
            Assert.isNull(readErrors.get(groupName), groupName + ' persona can read collection plans: ' + readErrors.get(groupName));
            Assert.areEqual(true, (Boolean) results.get(groupName).get('inCollections'),
                groupName + ' persona: the account with a plan (owned by the admin) is in collections, not unavailable.');
        }
    }

    // The standalone set carries exactly the collections read the personas need, and no persona
    // group contains it: a group with it fails to deploy while any holder lacks Billing Advanced.
    @isTest
    static void billingCollectionsReadSet_pinsItsContentAndIsInNoGroup() {
        String setName = RLM_BillingUITestUsers.COLLECTIONS_READ_SET;
        List<PermissionSet> sets = [SELECT Id, PermissionsCollectionsAndRecoverySpecialist FROM PermissionSet WHERE Name = :setName];
        if (sets.isEmpty()) {
            System.debug(LoggingLevel.WARN, 'SKIPPED: ' + setName + ' is not deployed (personas off).');
            return;
        }
        Id setId = sets[0].Id;
        Assert.isTrue(sets[0].PermissionsCollectionsAndRecoverySpecialist, setName + ' carries the Collections and Recovery Specialist user permission.');
        Map<String, ObjectPermissions> objects = new Map<String, ObjectPermissions>();
        for (ObjectPermissions op : [SELECT SobjectType, PermissionsRead, PermissionsCreate, PermissionsEdit, PermissionsDelete
                                     FROM ObjectPermissions WHERE ParentId = :setId]) {
            objects.put(op.SobjectType, op);
        }
        Assert.areEqual(new Set<String>{ 'CollectionPlan', 'CollectionPlanItem' }, objects.keySet(), setName + ' grants exactly these objects.');
        for (ObjectPermissions op : objects.values()) {
            Assert.isTrue(op.PermissionsRead && !op.PermissionsCreate && !op.PermissionsEdit && !op.PermissionsDelete,
                setName + ' grants read only on ' + op.SobjectType + '.');
        }
        List<FieldPermissions> fields = [SELECT Field, PermissionsRead, PermissionsEdit FROM FieldPermissions WHERE ParentId = :setId];
        Assert.areEqual(1, fields.size(), setName + ' grants exactly one field read: ' + fields);
        Assert.areEqual('CollectionPlan.AccountId', fields[0].Field, setName + ' grants CollectionPlan.AccountId.');
        Assert.isTrue(fields[0].PermissionsRead && !fields[0].PermissionsEdit, 'Read only.');
        Assert.areEqual(0, [SELECT COUNT() FROM PermissionSetGroupComponent WHERE PermissionSetId = :setId],
            setName + ' is in no permission set group.');
    }

    // With advanced currency management the dated rates need not cover every currency: such a
    // currency falls back to its standard rate rather than becoming unavailable or converting at 1.
    // GBP (non-corporate, standard 0.8, no dated rate) tells the two apart: its standard-rate undo
    // and its fallback dated rate cancel (100 * 0.8 / 0.8), where a dated rate of 1 would not
    // (100 * 0.8 / 1). Only a currency in neither map (JPY) is unavailable.
    @isTest
    static void correctConversion_aCurrencyWithoutADatedRate_usesItsStandardRate() {
        Map<String, Decimal> standard = new Map<String, Decimal>{ 'USD' => 1, 'EUR' => 0.5, 'GBP' => 0.8 };
        Map<String, Decimal> dated = new Map<String, Decimal>{ 'EUR' => 0.6 };
        Assert.areEqual(100, RLM_OnAccountBillingController.correctConversion(100, 'GBP', 'USD', standard, dated),
            'GBP has no dated rate: 100 * 0.8 (standard GBP) / 0.8 (standard GBP, the fallback) * 1 (USD) = 100; '
            + 'a dated rate of 1 would give 80.');
        Assert.areEqual(60, RLM_OnAccountBillingController.correctConversion(100, 'GBP', 'EUR', standard, dated),
            '100 * 0.8 / 0.8 (fallback) * 0.6 (dated EUR) = 60; a dated rate of 1 would give 48.');
        Decimal back = RLM_OnAccountBillingController.correctConversion(100, 'EUR', 'GBP', standard, dated);
        Assert.isTrue(back != null && Math.abs(back - 66.6666666667) < 0.0001,
            '100 * 0.5 (standard EUR) / 0.6 (dated EUR) * 0.8 (fallback GBP) = 66.67 (rate 1 would give 83.33), got ' + back);
        Assert.isNull(RLM_OnAccountBillingController.correctConversion(100, 'JPY', 'USD', standard, dated),
            'JPY is in neither map: unavailable, not converted at 1.');
    }

    // queryAggregate: a balance in a currency with no rate is unavailable (null), not converted at 1.
    @isTest
    static void queryAggregate_aBalanceInACurrencyWithNoRate_isUnavailable() {
        String corporate = corporateCurrency();
        Account acc = new Account(Name = 'RLM On-Account No Rate');
        insert acc;
        newProcessedPayment(acc.Id, 100, corporate);
        Test.startTest();
        Decimal withRates = RLM_OnAccountBillingController.queryAggregate('Payment', 'Balance', 'AccountId',
            'Status = \'Processed\' AND Balance != 0', acc.Id, corporate, activeRates(), activeRates(), true);
        Decimal noRate = RLM_OnAccountBillingController.queryAggregate('Payment', 'Balance', 'AccountId',
            'Status = \'Processed\' AND Balance != 0', acc.Id, 'ZZZ', new Map<String, Decimal>(), new Map<String, Decimal>(), true);
        Test.stopTest();
        Assert.areEqual(100, withRates, 'PRECONDITION: with the rates read, the payment balance sums.');
        Assert.isNull(noRate, 'No rate for the payment\'s currency or the target: unavailable, not 100 at rate 1.');
    }

    // Without advanced currency management (no dated rows: SELECT COUNT() FROM DatedConversionRate
    // returned 0 as admin on rlm-base__apexcov-ac1125-r1 and rlm-base__hdr-hdr-r1, both multi-currency,
    // measured 2026-11-26) a user whose dated-rate read is refused or empty gets an empty map, not an
    // error: every currency then converts at its standard rate. The ACM-on refusal (dated rows the
    // user cannot read -> fixed sentence) cannot be set up in a test: dated rates exist only with
    // ACM enabled, an org setting, and Apex cannot insert DatedConversionRate rows.
    @isTest
    static void loadDatedRates_withoutAdvancedCurrencyManagement_isEmptyForAnyUser() {
        // The count is read here, not through datedRatesExist(), which this test also checks.
        Integer datedRows;
        try {
            datedRows = Database.countQuery('SELECT COUNT() FROM DatedConversionRate', AccessLevel.SYSTEM_MODE);
        } catch (Exception e) {
            datedRows = 0;
        }
        Assert.areEqual(datedRows > 0, RLM_OnAccountBillingController.datedRatesExist(),
            'datedRatesExist() agrees with a system-mode count of ' + datedRows + ' dated rows.');
        if (datedRows > 0) {
            System.debug(LoggingLevel.WARN, 'SKIPPED: this org has ' + datedRows + ' dated rates (advanced currency management on).');
            return;
        }
        User noAccess = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        Map<String, Decimal> adminRates = RLM_OnAccountBillingController.loadDatedRates();
        Map<String, Decimal> userRates;
        Test.startTest();
        String userReadError;
        System.runAs(noAccess) {
            // Which branch this run takes: a refused read (the catch) or an empty one.
            // Diagnostic only: any exception becomes the logged message, so it cannot fail the test.
            try {
                userReadError = userModeError('SELECT IsoCode, ConversionRate FROM DatedConversionRate LIMIT 1');
            } catch (Exception e) {
                userReadError = e.getTypeName() + ': ' + e.getMessage();
            }
            userRates = RLM_OnAccountBillingController.loadDatedRates();
        }
        Test.stopTest();
        System.debug(LoggingLevel.INFO, 'DatedConversionRate probe as a no-access user: '
            + (userReadError == null ? 'read ran and returned no rows' : 'read refused (' + userReadError + ')'));
        Assert.isTrue(adminRates.isEmpty(), 'No dated rates for the admin.');
        Assert.isTrue(userRates.isEmpty(), 'No dated rates, and no error, for a user with no access.');
    }

    // A currency with no rate is never converted at 1: the balance is unavailable (null).
    @isTest
    static void correctConversion_withAMissingRate_isUnavailable() {
        Map<String, Decimal> rates = new Map<String, Decimal>{ 'USD' => 1, 'EUR' => 0.5 };
        Assert.areEqual(100, RLM_OnAccountBillingController.correctConversion(100, 'EUR', 'EUR', rates, rates),
            'Same currency is returned as is.');
        Assert.areEqual(50, RLM_OnAccountBillingController.correctConversion(100, 'USD', 'EUR', rates, rates),
            'With both rates present: 100 * 1 (undo USD) / 1 * 0.5 (EUR) = 50.');
        Assert.isNull(RLM_OnAccountBillingController.correctConversion(100, 'GBP', 'USD', rates, rates),
            'No rate for the source currency: unavailable, not converted at 1.');
        Assert.isNull(RLM_OnAccountBillingController.correctConversion(100, 'USD', 'GBP', rates, rates),
            'No rate for the target currency: unavailable, not converted at 1.');
    }

    private static final String COLLECTION_PLAN_READ = 'SELECT Id FROM CollectionPlan WHERE AccountId != null LIMIT 1';
    private static final String PAYMENT_READ =
        'SELECT Id, Balance, AccountId, Status, CurrencyIsoCode FROM Payment LIMIT 1';
    private static final String SKIP_NO_SECOND_CURRENCY =
        'SKIPPED: no second active currency with a different rate (a pricing data plan (qb, q3 or mfg) adds them).';

    private static final String SKIP_DATED_RATES_UNREADABLE =
        'SKIPPED: DatedConversionRate is not readable for the billing user';
    private static final String SKIP_RATE_TOO_CLOSE =
        'SKIPPED: the second currency\'s rate is too close to the corporate rate to tell conversion apart';

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

    // Every currency's standard rate, active or not, as the controller reads them.
    private static Map<String, Decimal> activeRates() {
        Map<String, Decimal> rates = new Map<String, Decimal>();
        for (CurrencyType ct : [SELECT IsoCode, ConversionRate FROM CurrencyType]) {
            rates.put(ct.IsoCode, ct.ConversionRate);
        }
        return rates;
    }

    // The effective rates as the given user reads them in USER_MODE: each currency's dated rate for
    // today, else its standard rate (the controller's effectiveRate rule). Only QueryException is
    // caught. Dated rates the user cannot read are skipped visibly by the FX test; differing
    // standard rates, or a partial read, fail userRatesMatchingAdmin's precondition.
    private static Map<String, Decimal> effectiveRatesAs(User u) {
        Map<String, Decimal> rates;
        System.runAs(u) {
            rates = effectiveRates(AccessLevel.USER_MODE);
        }
        return rates;
    }

    // The billing user's effective rates, after asserting that for each given code both its
    // effective rate and its standard (CurrencyType) rate equal the admin's. The FX test skips
    // visibly, before calling this, when the user cannot read dated rates; differing standard
    // rates, or a partial read, fail here as a precondition.
    private static Map<String, Decimal> userRatesMatchingAdmin(
        User u, Map<String, Decimal> adminRates, List<String> codes
    ) {
        Map<String, Decimal> userRates = effectiveRatesAs(u);
        Map<String, Decimal> adminStandard = activeRates();
        Map<String, Decimal> userStandard = new Map<String, Decimal>();
        System.runAs(u) {
            for (SObject ct : Database.query(
                'SELECT IsoCode, ConversionRate FROM CurrencyType', AccessLevel.USER_MODE
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

    // Each currency's dated rate for today, else its standard rate (every currency, active or not),
    // read at the given level: the controller's rule (effectiveRate).
    private static Map<String, Decimal> effectiveRates(AccessLevel level) {
        Map<String, Decimal> rates = new Map<String, Decimal>();
        try {
            for (SObject ct : Database.query('SELECT IsoCode, ConversionRate FROM CurrencyType', level)) {
                rates.put((String) ct.get('IsoCode'), (Decimal) ct.get('ConversionRate'));
            }
        } catch (QueryException e) {
            System.debug(LoggingLevel.INFO, 'Standard rates unreadable: ' + e.getMessage());
        }
        rates.putAll(datedRates(level));
        return rates;
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

    // The rate for a currency; a missing rate fails the test rather than reading as 1.
    private static Decimal rateOf(Map<String, Decimal> rates, String isoCode) {
        Assert.isTrue(rates.containsKey(isoCode), 'PRECONDITION: a rate for ' + isoCode + ' is read.');
        return rates.get(isoCode);
    }

    // A user who cannot read Account gets a fixed sentence, not the platform's query error and not
    // balances converted into a default currency.
    @isTest
    static void currencyOf_forAUserWhoCannotReadAccounts_throwsAFixedSentence() {
        User noAccess = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        Account acc = new Account(Name = 'RLM On-Account Unreadable');
        insert acc;
        String message;

        Test.startTest();
        System.runAs(noAccess) {
            Assert.isFalse(Schema.SObjectType.Account.isAccessible(), 'PRECONDITION: the user cannot read Account.');
            try {
                RLM_OnAccountBillingController.currencyOf(acc.Id);
            } catch (AuraHandledException e) {
                message = e.getMessage();
            }
        }
        Test.stopTest();

        Assert.isNotNull(message, 'The refused read is reported.');
        Assert.areEqual('Unable to read the account\'s currency, so its balances are not shown. Contact your administrator.',
            message, 'The user-facing sentence is fixed; no platform text is echoed.');
    }

    // ---- Refused reads (pack 452): a refused balance is unavailable (null), never counted as zero ----

    @isTest
    static void netOf_isUnavailableWhenAnyBalanceIs() {
        Assert.areEqual(100 + 20 - 5 - 30 + 2, RLM_OnAccountBillingController.netOf(100, 20, 5, 30, 2),
            'All balances read: invoices + debit memos - credit memos - payments + refunds.');
        Assert.isNull(RLM_OnAccountBillingController.netOf(null, 20, 5, 30, 2), 'Invoices refused: no net balance.');
        Assert.isNull(RLM_OnAccountBillingController.netOf(100, null, 5, 30, 2), 'Debit memos refused: no net balance.');
        Assert.isNull(RLM_OnAccountBillingController.netOf(100, 20, null, 30, 2), 'Credit memos refused: no net balance.');
        Assert.isNull(RLM_OnAccountBillingController.netOf(100, 20, 5, null, 2), 'Payments refused: no net balance.');
        Assert.isNull(RLM_OnAccountBillingController.netOf(100, 20, 5, 30, null), 'Refunds refused: no net balance.');
    }

    // A billing user who reads the account and its invoices but none of the other billing objects:
    // each of those balances, the net balance, the dispute count and the collections flag are
    // unavailable (null); the invoice balance and the invoice counts are real zeros.
    @isTest
    static void getBillingSummary_forAUserWhoReadsOnlyInvoices_showsTheOtherBalancesTheNetAndTheirCountsUnavailable() {
        User u = billingUserReading(new List<String>{ 'Account', 'Invoice' });
        Account acc = newAccountOwnedBy(u, 'RLM On-Account Invoices Only', null);
        Map<String, Object> result;
        Test.startTest();
        System.runAs(u) {
            assertReads(new List<String>{ ACCOUNT_READ, INVOICE_READ, PARTIALLY_PAID_READ },
                new List<String>{ DEBIT_MEMO_READ, CREDIT_MEMO_READ, PAYMENT_SUM_READ, REFUND_READ, DISPUTE_READ, COLLECTION_PLAN_READ });
            result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
        }
        Test.stopTest();

        Assert.areEqual(0, (Decimal) result.get('invoiceBalance'), 'The readable invoice balance is a real zero.');
        for (String key : new List<String>{ 'debitMemoBalance', 'creditMemoBalance', 'paymentBalance', 'refundBalance' }) {
            Assert.isTrue(result.containsKey(key), key + ' is returned.');
            Assert.isNull(result.get(key), key + ' is unavailable (null), not zero, when its read is refused.');
        }
        Assert.isNull(result.get('netAccountBalance'), 'The net balance includes the refused parts, so it is unavailable.');
        Assert.areEqual(0, (Integer) result.get('totalInvoices'), 'The invoice counts still run.');
        Assert.areEqual(0, (Integer) result.get('writtenOffCount'), 'The written-off count reads Invoice, so its zero is real.');
        Assert.areEqual(0, (Integer) result.get('partiallyPaidOverdueCount'),
            'The partially-paid count reads Invoice (granted, probed above), so its zero is real.');
        for (String key : new List<String>{ 'disputeCount', 'inCollections' }) {
            Assert.isTrue(result.containsKey(key), key + ' is returned.');
            Assert.isNull(result.get(key), key + ' is unavailable (null), not zero or false, when its read is refused.');
        }
    }

    // Per balance: with Payment also readable, the payment balance is a real zero while the
    // refused debit memo, credit memo and refund balances, and the net balance, are unavailable.
    @isTest
    static void getBillingSummary_forAUserWhoReadsInvoicesAndPayments_showsOnlyTheRefusedBalancesUnavailable() {
        User u = billingUserReading(new List<String>{ 'Account', 'Invoice', 'Payment' });
        Account acc = newAccountOwnedBy(u, 'RLM On-Account Invoices And Payments', null);
        Map<String, Object> result;
        Test.startTest();
        System.runAs(u) {
            assertReads(new List<String>{ ACCOUNT_READ, INVOICE_READ, PAYMENT_SUM_READ },
                new List<String>{ DEBIT_MEMO_READ, CREDIT_MEMO_READ, REFUND_READ });
            result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
        }
        Test.stopTest();

        Assert.areEqual(0, (Decimal) result.get('invoiceBalance'), 'The invoice balance is read, so its zero is real.');
        Assert.areEqual(0, (Decimal) result.get('paymentBalance'), 'The payment balance is read, so its zero is real.');
        for (String key : new List<String>{ 'debitMemoBalance', 'creditMemoBalance', 'refundBalance' }) {
            Assert.isNull(result.get(key), key + ' is unavailable (null), not zero, when its read is refused.');
        }
        Assert.isNull(result.get('netAccountBalance'), 'The net balance includes refused parts, so it is unavailable.');
    }

    // Without Invoice the summary cannot show the balances or the status: a fixed sentence, not the
    // platform's query error and not invoice counts of zero ("no billing activity").
    @isTest
    static void getBillingSummary_forAUserWhoCannotReadInvoices_throwsAFixedSentence() {
        User u = billingUserReading(new List<String>{ 'Account', 'DebitMemo', 'CreditMemo', 'Payment', 'Refund' });
        Account acc = newAccountOwnedBy(u, 'RLM On-Account No Invoices', null);
        String message;
        Test.startTest();
        System.runAs(u) {
            assertReads(new List<String>{ ACCOUNT_READ }, new List<String>{ INVOICE_READ });
            try {
                RLM_OnAccountBillingController.getBillingSummary(acc.Id);
            } catch (AuraHandledException e) {
                message = e.getMessage();
            }
        }
        Test.stopTest();

        Assert.areEqual('Unable to read this account\'s invoices, so its balances are not shown. Contact your administrator.',
            message, 'The user-facing sentence is fixed; no platform text is echoed.');
    }

    // The summary's reads, as the controller makes them (multi-currency: grouped by currency).
    private static final String ACCOUNT_READ = 'SELECT Id, CurrencyIsoCode FROM Account LIMIT 1';
    private static final String INVOICE_READ =
        'SELECT SUM(Balance) total, CurrencyIsoCode curr FROM Invoice WHERE BillingAccountId != null AND Status = \'Posted\' AND Balance != 0 GROUP BY CurrencyIsoCode';
    private static final String DEBIT_MEMO_READ =
        'SELECT SUM(TotalChargeAmount) total, CurrencyIsoCode curr FROM DebitMemo WHERE AccountId != null AND Status = \'Posted\' AND TotalChargeAmount != 0 AND InvoiceGenerationStatus != \'Posted Invoice Generated\' GROUP BY CurrencyIsoCode';
    private static final String CREDIT_MEMO_READ =
        'SELECT SUM(Balance) total, CurrencyIsoCode curr FROM CreditMemo WHERE BillingAccountId != null AND Status = \'Posted\' AND Balance != 0 GROUP BY CurrencyIsoCode';
    private static final String PARTIALLY_PAID_READ =
        'SELECT Id, Balance, TotalAmountWithTax FROM Invoice WHERE Status = \'Posted\' AND Balance > 0 LIMIT 1';
    private static final String DISPUTE_READ =
        'SELECT COUNT(Id) cnt FROM Dispute WHERE Invoice.BillingAccountId != null AND Status != \'Closed\'';
    private static final String PAYMENT_SUM_READ =
        'SELECT SUM(Balance) total, CurrencyIsoCode curr FROM Payment WHERE AccountId != null AND Status = \'Processed\' AND Balance != 0 GROUP BY CurrencyIsoCode';
    private static final String REFUND_READ =
        'SELECT SUM(Balance) total, CurrencyIsoCode curr FROM Refund WHERE AccountId != null AND Status = \'Processed\' AND Balance != 0 GROUP BY CurrencyIsoCode';

    // A billing user (Billing license and access permission) that reads and sees all records of
    // exactly the given objects, and nothing else.
    private static User billingUserReading(List<String> objects) {
        return RLM_BillingUITestUsers.createWithBillingAccess(
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL }, new List<String>(), objects);
    }

    // PRECONDITION for the running user: each of the first queries runs in user mode, and each of
    // the second is refused, so the result shows the controller's handling of that refusal.
    private static void assertReads(List<String> granted, List<String> refused) {
        for (String soql : granted) {
            String error = userModeError(soql);
            Assert.isNull(error, 'PRECONDITION: the user can run ' + soql + ': ' + error);
        }
        for (String soql : refused) {
            Assert.isNotNull(userModeError(soql), 'PRECONDITION: the user cannot run ' + soql);
        }
    }

    // An org without the license-gated Dispute fields the count reads has no disputes: a real
    // zero, not unavailable. Simulated by naming a field this org's Dispute lacks; the same
    // account as a user who cannot read Dispute shows the gate runs before the read.
    @isTest
    static void getBillingSummary_withoutTheDisputeFields_countsZeroDisputes() {
        User u = billingUserReading(new List<String>{ 'Account', 'Invoice' });
        Account acc = newAccountOwnedBy(u, 'RLM On-Account No Dispute Fields', null);
        RLM_OnAccountBillingController.disputeFields = new Set<String>{ 'InvoiceId', 'Status', 'RLM_NoSuchField__c' };
        Map<String, Object> result;
        Test.startTest();
        System.runAs(u) {
            assertReads(new List<String>{ ACCOUNT_READ, INVOICE_READ }, new List<String>{ DISPUTE_READ });
            result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
        }
        Test.stopTest();

        Assert.isTrue(Schema.getGlobalDescribe().containsKey('Dispute'), 'PRECONDITION: the Dispute object exists in this org.');
        Assert.areEqual(0, (Integer) result.get('disputeCount'),
            'Without the dispute fields there are no disputes: a real zero, even for a user who cannot read Dispute.');
    }
}
