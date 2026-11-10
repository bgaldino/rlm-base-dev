/**
 * Tests for RLM_BillingScheduleGroupService.
 *
 * The native standard-action invoke (createBillingSchedulesFromTrxn) is not run in
 * these tests: the create-via-API path is covered through the @TestVisible mock seam
 * (mockActionOutputs) plus direct coverage of the pure payload-build and result-parse
 * helpers, so the real invoke and its failed-result handling stay uncovered. Validation
 * guards are covered by asserting AuraHandledException on bad input. The create tests do
 * not observe the payload passed to the action, so the argument wiring from
 * createBillingScheduleGroupAndScheduleViaAPI into buildTransactionDetailsJson is unverified
 * (capturing it needs a production seam). The System.runAs
 * test creates its user through RLM_BillingUITestUsers, which takes a Billing permission
 * set license seat.
 *
 * Known gap (documented from a diagnostic run, not asserted by a test): on a Release 264
 * org, a run of the action with real records and this service's payload returned
 * isSuccess() = false with REQUIRED_FIELD_MISSING for billToContact, then paymentTermID,
 * then shippingAddress, as each earlier one was supplied on the records. The payload sends
 * none of these, so the create path may fail for a typical account.
 * buildTransactionDetailsJson_mapsInputsToStandardContextFields pins the payload's exact
 * key set, so it catches a fix only if the fix adds payload keys; prerequisites supplied on
 * records through the context mapping would not show there.
 *
 * Known gap (documented, not pinned): getAccountBillingInfo reads one arbitrary
 * BillingAccount for the account (LIMIT 1 with no ORDER BY, ignoring
 * IsDefaultBillingProfile). With more than one billing account the result is
 * nondeterministic, so an assertion could not pin it reliably; the tests use at most one.
 *
 * Known gap (pinned): getAccountBillingInfo never resolves a billing account linked to the
 * account only through AccountBillingAccount, although the create path does resolve that
 * link. See getAccountBillingInfo_junctionOnlyBillingAccount_isNotResolved.
 */
@isTest
private class RLM_BillingScheduleGroupServiceTest {
    private static Id fakeId(Schema.SObjectType t) {
        return (Id) (t.getDescribe().getKeyPrefix() + '000000000000');
    }

    @isTest
    static void getAccountBillingInfo_nullArg_throws() {
        Boolean threw = false;
        try {
            RLM_BillingScheduleGroupService.getAccountBillingInfo(null);
        } catch (AuraHandledException e) {
            threw = true;
        }
        System.assert(threw, 'Expected AuraHandledException for null accountId');
    }

    @isTest
    static void getAccountBillingInfo_accountNotFound_throws() {
        Boolean threw = false;
        try {
            RLM_BillingScheduleGroupService.getAccountBillingInfo(fakeId(Account.SObjectType));
        } catch (AuraHandledException e) {
            threw = true;
        }
        System.assert(threw, 'Expected AuraHandledException for missing account');
    }

    @isTest
    static void createViaAPI_validationGuards() {
        // Null billing account -> throws before any query.
        System.assert(throwsViaApi(null), 'null billing account throws');
        // Valid-shaped but non-existent billing account -> "not found".
        System.assert(throwsViaApi(fakeId(BillingAccount.SObjectType)), 'missing billing account throws');
    }

    @isTest
    static void createViaAPI_happyPath_returnsRequestId() {
        Account a = new Account(Name = 'BSG ViaApi Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG ViaApi BA', AccountId = a.Id);
        insert ba;

        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{
            'requestId' => 'REQ-PLACEHOLDER',
            'statusUrl' => '/services/data/v68.0/sobjects/AsyncOperationTracker/REQ-PLACEHOLDER'
        };

        Test.startTest();
        RLM_BillingScheduleGroupService.CreateResult r =
            RLM_BillingScheduleGroupService.createBillingScheduleGroupAndScheduleViaAPI(
                ba.Id, 'Month', 12, 'Advance', 2, fakeId(LegalEntity.SObjectType),
                fakeId(TaxTreatment.SObjectType), 'USD', 10, 240, 'San Francisco',
                fakeId(Product2.SObjectType), 'Widget', Date.newInstance(2026, 1, 1),
                1, 1, 'Termed', Date.newInstance(2026, 12, 31)
            );
        Test.stopTest();

        Assert.areEqual('REQ-PLACEHOLDER', r.requestId, 'requestId surfaced from action output');
    }

    @isTest
    static void invokeAndParse_viaMockSeam() {
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{
            'requestId' => 'REQ-PLACEHOLDER',
            'statusUrl' => '/services/data/v68.0/sobjects/AsyncOperationTracker/REQ-PLACEHOLDER'
        };
        Map<String, Object> out =
            RLM_BillingScheduleGroupService.invokeStandaloneBillingScheduleCreate('{"Transaction":[]}');
        RLM_BillingScheduleGroupService.CreateResult r =
            RLM_BillingScheduleGroupService.parseCreateResult(out);
        Assert.areEqual('REQ-PLACEHOLDER', r.requestId);
        System.assert(r.statusUrl.contains('AsyncOperationTracker'), 'statusUrl mapped');
        System.assertNotEquals(null, r.apiResponse, 'apiResponse serialized');
    }

    @isTest
    static void parseCreateResult_handlesNullAndIds() {
        RLM_BillingScheduleGroupService.CreateResult empty =
            RLM_BillingScheduleGroupService.parseCreateResult(null);
        System.assertEquals(null, empty.requestId);

        Id anyId = fakeId(Account.SObjectType);
        Map<String, Object> out = new Map<String, Object>{
            'billingScheduleGroupId' => anyId,
            'billingScheduleIds' => new List<Object>{ anyId }
        };
        RLM_BillingScheduleGroupService.CreateResult r =
            RLM_BillingScheduleGroupService.parseCreateResult(out);
        System.assertEquals(anyId, r.billingScheduleGroupId);
        System.assertEquals(anyId, r.billingScheduleId);
    }

    @isTest
    static void innerClasses_construct() {
        Id acc = fakeId(Account.SObjectType);
        RLM_BillingScheduleGroupService.LegalEntityOption le =
            new RLM_BillingScheduleGroupService.LegalEntityOption(acc, 'LE');
        RLM_BillingScheduleGroupService.TaxTreatmentOption tt =
            new RLM_BillingScheduleGroupService.TaxTreatmentOption(acc, 'TT');
        RLM_BillingScheduleGroupService.ProductOption po =
            new RLM_BillingScheduleGroupService.ProductOption(acc, 'Prod');
        RLM_BillingScheduleGroupService.PicklistOption pl =
            new RLM_BillingScheduleGroupService.PicklistOption('Label', 'Value');
        RLM_BillingScheduleGroupService.AccountInfo ai =
            new RLM_BillingScheduleGroupService.AccountInfo('Acct', acc, 'BA', 'City');
        System.assertEquals('LE', le.name);
        System.assertEquals('TT', tt.name);
        System.assertEquals('Prod', po.name);
        System.assertEquals('Value', pl.value);
        System.assertEquals('City', ai.billingCity);
    }

    // ---- getAccountBillingInfo ----

    @isTest
    static void getAccountBillingInfo_withBillingAccount_returnsAccountAndBillingDetails() {
        Account a = new Account(Name = 'BSG Info Acct', BillingCity = 'Austin');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG Info BA', AccountId = a.Id);
        insert ba;

        Test.startTest();
        RLM_BillingScheduleGroupService.AccountInfo info =
            RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        Test.stopTest();

        Assert.areEqual('BSG Info Acct', info.accountName, 'Account name surfaced.');
        Assert.areEqual(ba.Id, info.billingAccountId, 'The billing account linked to the account is returned.');
        Assert.areEqual('BSG Info BA', info.billingAccountName, 'Billing account name surfaced.');
        Assert.areEqual('Austin', info.billingCity, 'Billing city comes from the billing account\'s account.');
    }

    @isTest
    static void getAccountBillingInfo_withoutBillingAccount_returnsAccountNameOnly() {
        Account a = new Account(Name = 'BSG No BA Acct', BillingCity = 'Denver');
        insert a;

        Test.startTest();
        RLM_BillingScheduleGroupService.AccountInfo info =
            RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        Test.stopTest();

        Assert.areEqual('BSG No BA Acct', info.accountName, 'Account name is returned without a billing account.');
        Assert.isNull(info.billingAccountId, 'No billing account -> no billing account id.');
        Assert.isNull(info.billingAccountName, 'No billing account -> no billing account name.');
        Assert.isNull(info.billingCity, 'Billing city is read through the billing account, so it is blank too.');
    }

    @isTest
    static void getAccountBillingInfo_junctionOnlyBillingAccount_isNotResolved() {
        Account a = new Account(Name = 'BSG Junction Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG Junction BA');
        insert ba;
        insert new AccountBillingAccount(AccountId = a.Id, BillingAccountId = ba.Id);
        Assert.isNull([SELECT AccountId FROM BillingAccount WHERE Id = :ba.Id].AccountId,
            'PRECONDITION: inserting the junction row does not set BillingAccount.AccountId.');

        Test.startTest();
        RLM_BillingScheduleGroupService.AccountInfo info =
            RLM_BillingScheduleGroupService.getAccountBillingInfo(a.Id);
        Test.stopTest();

        Assert.areEqual('BSG Junction Acct', info.accountName);
        Assert.isNull(info.billingAccountId,
            'Known gap: getAccountBillingInfo does not resolve a billing account linked only through '
            + 'AccountBillingAccount; update this test when it is fixed.');
    }

    // ---- option queries ----

    @isTest
    static void getProducts_returnsActiveSoftwareProductsSortedByName() {
        Product2 zeta = new Product2(Name = 'BSG Zeta Software', Family = 'Software', IsActive = true);
        Product2 alpha = new Product2(Name = 'BSG Alpha Software', Family = 'Software', IsActive = true);
        Product2 inactive = new Product2(Name = 'BSG Inactive Software', Family = 'Software', IsActive = false);
        Product2 noFamily = new Product2(Name = 'BSG No Family', IsActive = true);
        insert new List<Product2>{ zeta, alpha, inactive, noFamily };

        Test.startTest();
        List<RLM_BillingScheduleGroupService.ProductOption> options =
            RLM_BillingScheduleGroupService.getProducts();
        Test.stopTest();

        Assert.areEqual(2, options.size(), 'Only active products in the Software family are offered.');
        Assert.areEqual(alpha.Id, options[0].id, 'Options are sorted by name.');
        Assert.areEqual('BSG Alpha Software', options[0].name);
        Assert.areEqual(zeta.Id, options[1].id);
        Assert.areEqual('BSG Zeta Software', options[1].name);
    }

    // Product2 has no record sharing, so this proves a billing role can run the USER_MODE
    // product query (object read plus Name/IsActive/Family) without depending on OWD.
    @isTest
    static void getProducts_asBillingRole_returnsTheProducts() {
        Product2 prod = new Product2(Name = 'BSG Role Software', Family = 'Software', IsActive = true);
        insert prod;
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });

        List<RLM_BillingScheduleGroupService.ProductOption> options;
        Test.startTest();
        System.runAs(u) {
            options = RLM_BillingScheduleGroupService.getProducts();
        }
        Test.stopTest();

        Assert.areEqual(1, options.size(), 'The billing role sees the active Software product.');
        Assert.areEqual(prod.Id, options[0].id);
    }

    @isTest
    static void getLegalEntities_returnsAllSortedByName() {
        LegalEntity zulu = new LegalEntity(Name = 'BSG LE Zulu', Status = 'Active');
        LegalEntity alpha = new LegalEntity(Name = 'BSG LE Alpha', Status = 'Active');
        insert new List<LegalEntity>{ zulu, alpha };

        Test.startTest();
        List<RLM_BillingScheduleGroupService.LegalEntityOption> options =
            RLM_BillingScheduleGroupService.getLegalEntities();
        Test.stopTest();

        Assert.areEqual(2, options.size(), 'Every legal entity is offered.');
        Assert.areEqual(alpha.Id, options[0].id, 'Options are sorted by name.');
        Assert.areEqual('BSG LE Alpha', options[0].name);
        Assert.areEqual(zulu.Id, options[1].id);
        Assert.areEqual('BSG LE Zulu', options[1].name);
    }

    @isTest
    static void getTaxTreatments_returnsAllSortedByName() {
        // Two treatments on one legal entity with no tax policy or product code collided on
        // TaxTreatment's unique key, so each gets its own legal entity.
        LegalEntity le1 = new LegalEntity(Name = 'BSG TT LE 1', Status = 'Active');
        LegalEntity le2 = new LegalEntity(Name = 'BSG TT LE 2', Status = 'Active');
        insert new List<LegalEntity>{ le1, le2 };
        TaxTreatment ttSecond = new TaxTreatment(Name = 'BSG TT Second', Status = 'Draft', LegalEntityId = le1.Id);
        TaxTreatment ttFirst = new TaxTreatment(Name = 'BSG TT First', Status = 'Draft', LegalEntityId = le2.Id);
        insert new List<TaxTreatment>{ ttSecond, ttFirst };

        Test.startTest();
        List<RLM_BillingScheduleGroupService.TaxTreatmentOption> options =
            RLM_BillingScheduleGroupService.getTaxTreatments();
        Test.stopTest();

        Assert.areEqual(2, options.size(), 'Every tax treatment is offered.');
        Assert.areEqual(ttFirst.Id, options[0].id, 'Options are sorted by name.');
        Assert.areEqual('BSG TT First', options[0].name);
        Assert.areEqual(ttSecond.Id, options[1].id);
        Assert.areEqual('BSG TT Second', options[1].name);
    }

    @isTest
    static void optionQueries_noRecords_returnEmptyLists() {
        Test.startTest();
        List<RLM_BillingScheduleGroupService.LegalEntityOption> les =
            RLM_BillingScheduleGroupService.getLegalEntities();
        List<RLM_BillingScheduleGroupService.TaxTreatmentOption> tts =
            RLM_BillingScheduleGroupService.getTaxTreatments();
        List<RLM_BillingScheduleGroupService.ProductOption> prods =
            RLM_BillingScheduleGroupService.getProducts();
        Test.stopTest();

        Assert.isTrue(les.isEmpty(), 'No legal entities -> empty list, not null.');
        Assert.isTrue(tts.isEmpty(), 'No tax treatments -> empty list, not null.');
        Assert.isTrue(prods.isEmpty(), 'No products -> empty list, not null.');
    }

    // The expected options are built from the same BillingSchedule describe the service reads,
    // so these tests prove the describe source is used (labels, values and order). That this
    // rules out the hard-coded fallback (not exercised) relies on the shipped value sets being
    // larger than the fallback lists. Each test also checks one shipped value is offered.
    @isTest
    static void billingTermUnitOptions_comeFromTheBillingSchedulePicklist() {
        List<String> expected = picklistLabelsAndValues('BillingTermUnit');
        Test.startTest();
        List<RLM_BillingScheduleGroupService.PicklistOption> options =
            RLM_BillingScheduleGroupService.getBillingScheduleBillingTermUnitOptions();
        Test.stopTest();

        assertOptions(expected, options);
        Assert.isTrue(optionValues(options).contains('Month'), 'The shipped Month unit is offered: ' + expected);
    }

    @isTest
    static void pricingTermUnitOptions_comeFromTheBillingSchedulePicklist() {
        List<String> expected = picklistLabelsAndValues('PricingTermUnit');
        Test.startTest();
        List<RLM_BillingScheduleGroupService.PicklistOption> options =
            RLM_BillingScheduleGroupService.getPricingTermUnitOptions();
        Test.stopTest();

        assertOptions(expected, options);
        Assert.isTrue(optionValues(options).contains('Months'), 'The shipped Months unit is offered: ' + expected);
    }

    // ---- createBillingScheduleGroupAndScheduleViaAPI ----

    // Every input guard after the account is resolved, flipped one at a time from inputs that
    // pass. The baseline call proves the defaults are valid, so each rejection is caused by
    // the one input that changed.
    @isTest
    static void createViaAPI_rejectsEachInvalidInput() {
        Id baId = insertBillingAccount('BSG Guards');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-OK' };

        Map<String, CreateArgs> invalidInputs = new Map<String, CreateArgs>();
        CreateArgs a;
        a = new CreateArgs(baId); a.billingTermUnit = null;       invalidInputs.put('null billing term unit', a);
        a = new CreateArgs(baId); a.billingTermUnit = '  ';       invalidInputs.put('blank billing term unit', a);
        a = new CreateArgs(baId); a.quantity = null;              invalidInputs.put('null quantity', a);
        a = new CreateArgs(baId); a.quantity = -1;                invalidInputs.put('negative quantity', a);
        a = new CreateArgs(baId); a.legalEntityId = null;         invalidInputs.put('null legal entity', a);
        a = new CreateArgs(baId); a.taxTreatmentId = null;        invalidInputs.put('null tax treatment', a);
        a = new CreateArgs(baId); a.currencyIsoCode = '';         invalidInputs.put('blank currency', a);
        a = new CreateArgs(baId); a.unitPrice = null;             invalidInputs.put('null unit price', a);
        a = new CreateArgs(baId); a.unitPrice = -0.01;            invalidInputs.put('negative unit price', a);
        a = new CreateArgs(baId); a.billingCity = ' ';            invalidInputs.put('blank billing city', a);
        a = new CreateArgs(baId); a.productId = null;             invalidInputs.put('null product', a);
        a = new CreateArgs(baId); a.startDate = null;             invalidInputs.put('null start date', a);
        a = new CreateArgs(baId); a.billingDayOfMonth = null;     invalidInputs.put('null billing day', a);
        a = new CreateArgs(baId); a.billingDayOfMonth = 0;        invalidInputs.put('billing day 0', a);
        a = new CreateArgs(baId); a.billingDayOfMonth = 32;       invalidInputs.put('billing day 32', a);
        a = new CreateArgs(baId); a.billingStartMonth = null;     invalidInputs.put('null start month', a);
        a = new CreateArgs(baId); a.billingStartMonth = 0;        invalidInputs.put('start month 0', a);
        a = new CreateArgs(baId); a.billingStartMonth = 13;       invalidInputs.put('start month 13', a);

        List<String> accepted = new List<String>();
        Test.startTest();
        Assert.areEqual('REQ-OK', new CreateArgs(baId).call().requestId, 'PRECONDITION: the default inputs are valid.');
        for (String label : invalidInputs.keySet()) {
            if (!throwsAura(invalidInputs.get(label))) {
                accepted.add(label);
            }
        }
        Test.stopTest();

        Assert.isTrue(accepted.isEmpty(), 'Invalid input was accepted: ' + String.join(accepted, ', '));
    }

    @isTest
    static void createViaAPI_acceptsBoundaryValues() {
        Id baId = insertBillingAccount('BSG Boundaries');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-EDGE' };

        List<CreateArgs> edges = new List<CreateArgs>();
        CreateArgs a;
        a = new CreateArgs(baId); a.quantity = 0; a.unitPrice = 0; edges.add(a);
        a = new CreateArgs(baId); a.billingDayOfMonth = 1; a.billingStartMonth = 12; edges.add(a);
        a = new CreateArgs(baId); a.billingDayOfMonth = 31; a.billingStartMonth = 1; edges.add(a);

        Test.startTest();
        for (CreateArgs edge : edges) {
            RLM_BillingScheduleGroupService.CreateResult r = edge.call();
            Assert.areEqual('REQ-EDGE', r.requestId,
                'Boundary values (0 quantity/price, day 1-31, month 1-12) are valid.');
        }
        Test.stopTest();
    }

    @isTest
    static void createViaAPI_mapsEveryActionOutput() {
        Id baId = insertBillingAccount('BSG Outputs');
        Id bsgId = fakeId(BillingScheduleGroup.SObjectType);
        Id bsId = fakeId(BillingSchedule.SObjectType);
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{
            'requestId' => 'REQ-1',
            'statusUrl' => '/services/data/v68.0/sobjects/AsyncOperationTracker/REQ-1',
            'billingScheduleGroupId' => bsgId,
            'billingScheduleId' => bsId
        };

        Test.startTest();
        RLM_BillingScheduleGroupService.CreateResult r = new CreateArgs(baId).call();
        Test.stopTest();

        Assert.areEqual('REQ-1', r.requestId);
        Assert.areEqual('/services/data/v68.0/sobjects/AsyncOperationTracker/REQ-1', r.statusUrl);
        Assert.areEqual(bsgId, r.billingScheduleGroupId, 'A synchronous BSG id is passed through.');
        Assert.areEqual(bsId, r.billingScheduleId, 'A synchronous schedule id is passed through.');
        Map<String, Object> echoed = (Map<String, Object>) System.JSON.deserializeUntyped(r.apiResponse);
        Assert.areEqual('REQ-1', echoed.get('requestId'), 'apiResponse is the serialized action output.');
    }

    // A billing account with no AccountId but an AccountBillingAccount row is accepted. The
    // orphan test below is the same input without the junction row, which is rejected, so the
    // junction row is what lets the create through. The mock does not capture the payload, so
    // which account id is sent is not observed.
    @isTest
    static void createViaAPI_billingAccountLinkedThroughJunction_isAccepted() {
        Account a = new Account(Name = 'BSG Junction Create Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = 'BSG Junction Create BA');
        insert ba;
        insert new AccountBillingAccount(AccountId = a.Id, BillingAccountId = ba.Id);
        Assert.isNull([SELECT AccountId FROM BillingAccount WHERE Id = :ba.Id].AccountId,
            'PRECONDITION: inserting the junction row does not set BillingAccount.AccountId.');
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-JN' };

        Test.startTest();
        RLM_BillingScheduleGroupService.CreateResult r = new CreateArgs(ba.Id).call();
        Test.stopTest();

        Assert.areEqual('REQ-JN', r.requestId, 'A billing account linked through the junction row is accepted.');
    }

    // A billing account with no AccountId resolves its account through AccountBillingAccount;
    // with no junction row either, the create must refuse rather than send a null account.
    // The premises pin that it is that guard: the billing account is found (so not "not
    // found"), its AccountId is null and no junction row exists. The other inputs are the
    // defaults that pass every later guard (see createViaAPI_rejectsEachInvalidInput).
    @isTest
    static void createViaAPI_billingAccountWithoutAccount_throws() {
        BillingAccount orphan = new BillingAccount(Name = 'BSG Orphan BA');
        insert orphan;
        RLM_BillingScheduleGroupService.mockActionOutputs = new Map<String, Object>{ 'requestId' => 'REQ-NO' };

        List<BillingAccount> found = [
            SELECT Id, AccountId FROM BillingAccount WHERE Id = :orphan.Id WITH USER_MODE
        ];
        Integer junctionRows = [
            SELECT COUNT() FROM AccountBillingAccount WHERE BillingAccountId = :orphan.Id WITH USER_MODE
        ];
        Assert.areEqual(1, found.size(), 'PRECONDITION: the billing account is readable in USER_MODE.');
        Assert.isNull(found[0].AccountId, 'PRECONDITION: the billing account has no AccountId.');
        Assert.areEqual(0, junctionRows, 'PRECONDITION: no AccountBillingAccount row links it to an account.');

        Test.startTest();
        Boolean threw = throwsAura(new CreateArgs(orphan.Id));
        Test.stopTest();

        Assert.isTrue(threw, 'A billing account with no resolvable account must be rejected.');
    }

    // ---- payload builder ----

    @isTest
    static void buildTransactionDetailsJson_mapsInputsToStandardContextFields() {
        Id accId = fakeId(Account.SObjectType);
        Id baId = fakeId(BillingAccount.SObjectType);
        Id ttId = fakeId(TaxTreatment.SObjectType);
        Id prodId = fakeId(Product2.SObjectType);

        // Quantity, unit price and total are deliberately inconsistent: 3 x 12.5 x 12 months =
        // 450, so 451 cannot be derived. The builder passes each through as given.
        Map<String, Object> txn = onlyTransaction(RLM_BillingScheduleGroupService.buildTransactionDetailsJson(
            accId, baId, 'Month', 3, fakeId(LegalEntity.SObjectType), ttId,
            'EUR', 12.5, 451, 'Lisbon', prodId, 'Widget Pro',
            Date.newInstance(2026, 4, 7), 7, 4, 'Termed', Date.newInstance(2027, 4, 6)
        ));

        // Known gap, pinned by the exact key set: legalEntityId is accepted but not sent, the
        // public create method likewise accepts billingTerm and billingTypePicklistTiming and
        // drops them, and no bill-to contact, payment term or shipping address is sent (see the
        // class header). Any key added to or removed from the payload fails here.
        Set<String> expectedKeys = new Set<String>{
            'TransactionId__std', 'SellingModelType__std', 'ProductId__std', 'ProductName__std',
            'StartDate__std', 'EndDate__std', 'PeriodBoundary__std', 'BillingDayOfMonth__std',
            'BillingStartMonth__std', 'UnitPrice__std', 'Quantity__std', 'TotalPrice__std',
            'TaxTreatmentId__std', 'AccountId__std', 'BillingProfileId__std', 'BillingCity__std',
            'BillingTermUnit__std', 'BillingActionType__std', 'CurrencyIsoCode__std'
        };
        Set<String> added = new Set<String>(txn.keySet());
        added.removeAll(expectedKeys);
        Set<String> missing = new Set<String>(expectedKeys);
        missing.removeAll(txn.keySet());
        Assert.isTrue(added.isEmpty(),
            'Known gap: the payload omits legalEntityId, billingTerm and billing type timing, and sends no '
            + 'bill-to contact, payment term or shipping address (see class header). New keys ' + added
            + ': a fix to the known gap may have landed; update this test and the header.');
        Assert.isTrue(missing.isEmpty(),
            'A required payload key was removed (regression): ' + missing);

        Assert.isTrue(String.valueOf(txn.get('TransactionId__std')).startsWith('txn_'), 'Generated transaction id.');
        Assert.areEqual('TermDefined', txn.get('SellingModelType__std'), 'Termed maps to TermDefined.');
        Assert.areEqual(String.valueOf(prodId), txn.get('ProductId__std'));
        Assert.areEqual('Widget Pro', txn.get('ProductName__std'));
        Assert.areEqual('2026-04-07', txn.get('StartDate__std'));
        Assert.areEqual('2027-04-06', txn.get('EndDate__std'), 'A termed schedule carries its end date.');
        Assert.areEqual('Anniversary', txn.get('PeriodBoundary__std'));
        Assert.areEqual(7, txn.get('BillingDayOfMonth__std'));
        Assert.areEqual(4, txn.get('BillingStartMonth__std'));
        Assert.areEqual(Decimal.valueOf('12.5'), toDecimal(txn.get('UnitPrice__std')));
        Assert.areEqual(Decimal.valueOf('3'), toDecimal(txn.get('Quantity__std')));
        Assert.areEqual(Decimal.valueOf('451'), toDecimal(txn.get('TotalPrice__std')));
        Assert.areEqual(String.valueOf(ttId), txn.get('TaxTreatmentId__std'));
        Assert.areEqual(String.valueOf(accId), txn.get('AccountId__std'));
        Assert.areEqual(String.valueOf(baId), txn.get('BillingProfileId__std'),
            'The billing account is sent as the billing profile.');
        Assert.areEqual('Lisbon', txn.get('BillingCity__std'));
        Assert.areEqual('Month', txn.get('BillingTermUnit__std'));
        Assert.areEqual('Add', txn.get('BillingActionType__std'));
        Assert.areEqual('EUR', txn.get('CurrencyIsoCode__std'));
    }

    @isTest
    static void buildTransactionDetailsJson_sellingModelFollowsTermSetting() {
        Assert.areEqual('Evergreen', sellingModelFor('Evergreen'), 'Evergreen passes through.');
        Assert.areEqual('OneTime', sellingModelFor('OneTime'), 'Any other non-blank setting passes through.');
        Assert.areEqual('Evergreen', sellingModelFor(null), 'No term setting defaults to Evergreen.');
        Assert.areEqual('Evergreen', sellingModelFor('  '), 'A blank term setting defaults to Evergreen.');
    }

    @isTest
    static void buildTransactionDetailsJson_termedWithoutEndDate_omitsEndDate() {
        Map<String, Object> txn = onlyTransaction(RLM_BillingScheduleGroupService.buildTransactionDetailsJson(
            fakeId(Account.SObjectType), fakeId(BillingAccount.SObjectType), 'Month', 1,
            fakeId(LegalEntity.SObjectType), fakeId(TaxTreatment.SObjectType), 'USD', 10, 120,
            'Boston', fakeId(Product2.SObjectType), 'Widget', Date.newInstance(2026, 1, 1), 1, 1,
            'Termed', null
        ));
        Assert.areEqual('TermDefined', txn.get('SellingModelType__std'));
        Assert.isFalse(txn.containsKey('EndDate__std'), 'No end date supplied -> none sent.');
    }

    @isTest
    static void buildTransactionDetailsJson_nonTermedSendsTotalButNoEndDate() {
        // TotalPrice__std is required for every new-sale selling model; only TermDefined has an
        // end date, so a supplied one is ignored for the others.
        for (String termSetting : new List<String>{ 'Evergreen', 'OneTime' }) {
            Map<String, Object> txn = onlyTransaction(RLM_BillingScheduleGroupService.buildTransactionDetailsJson(
                fakeId(Account.SObjectType), fakeId(BillingAccount.SObjectType), 'Month', 1,
                fakeId(LegalEntity.SObjectType), fakeId(TaxTreatment.SObjectType), 'USD', 10, 75,
                'Boston', fakeId(Product2.SObjectType), 'Widget', Date.newInstance(2026, 1, 1), 1, 1,
                termSetting, Date.newInstance(2026, 12, 31)
            ));
            Assert.areEqual(Decimal.valueOf('75'), toDecimal(txn.get('TotalPrice__std')),
                termSetting + ' sends the total price.');
            Assert.isFalse(txn.containsKey('EndDate__std'), termSetting + ' sends no end date.');
        }
    }

    @isTest
    static void formatIsoDate_keepsTwoDigitMonthAndDay() {
        Assert.areEqual('2026-12-31', RLM_BillingScheduleGroupService.formatIsoDate(Date.newInstance(2026, 12, 31)));
        Assert.areEqual('2027-01-09', RLM_BillingScheduleGroupService.formatIsoDate(Date.newInstance(2027, 1, 9)));
    }

    // ---- result parser ----

    @isTest
    static void parseCreateResult_prefersSingleScheduleIdOverList() {
        Id single = fakeId(BillingSchedule.SObjectType);
        Id other = Id.valueOf(BillingSchedule.SObjectType.getDescribe().getKeyPrefix() + '000000000001');
        RLM_BillingScheduleGroupService.CreateResult r = RLM_BillingScheduleGroupService.parseCreateResult(
            new Map<String, Object>{
                'billingScheduleId' => single,
                'billingScheduleIds' => new List<Object>{ other }
            });
        Assert.areEqual(single, r.billingScheduleId, 'billingScheduleId wins when both are present.');
    }

    @isTest
    static void parseCreateResult_ignoresEmptyOrNonListScheduleIds() {
        RLM_BillingScheduleGroupService.CreateResult emptyList = RLM_BillingScheduleGroupService.parseCreateResult(
            new Map<String, Object>{ 'billingScheduleIds' => new List<Object>() });
        Assert.isNull(emptyList.billingScheduleId, 'An empty id list yields no schedule id.');

        RLM_BillingScheduleGroupService.CreateResult notAList = RLM_BillingScheduleGroupService.parseCreateResult(
            new Map<String, Object>{ 'billingScheduleIds' => 'not-a-list' });
        Assert.isNull(notAList.billingScheduleId, 'A non-list value yields no schedule id.');
    }

    @isTest
    static void parseCreateResult_emptyOutputs_leavesFieldsNullButEchoesResponse() {
        RLM_BillingScheduleGroupService.CreateResult r =
            RLM_BillingScheduleGroupService.parseCreateResult(new Map<String, Object>());
        Assert.isNull(r.requestId);
        Assert.isNull(r.statusUrl);
        Assert.isNull(r.billingScheduleGroupId);
        Assert.isNull(r.billingScheduleId);
        Assert.areEqual('{}', r.apiResponse, 'The (empty) action output is still echoed.');
    }

    // ---- helpers ----

    // Inputs for createBillingScheduleGroupAndScheduleViaAPI that pass every guard; a test
    // overrides one field to drive one guard.
    private class CreateArgs {
        public Id billingAccountId;
        public String billingTermUnit = 'Month';
        public Integer billingTerm = 12;
        public String billingType = 'Advance';
        public Decimal quantity = 2;
        public Id legalEntityId = fakeId(LegalEntity.SObjectType);
        public Id taxTreatmentId = fakeId(TaxTreatment.SObjectType);
        public String currencyIsoCode = 'USD';
        public Decimal unitPrice = 10;
        public Decimal totalPrice = 240;
        public String billingCity = 'San Francisco';
        public Id productId = fakeId(Product2.SObjectType);
        public String productName = 'Widget';
        public Date startDate = Date.newInstance(2026, 1, 1);
        public Integer billingDayOfMonth = 1;
        public Integer billingStartMonth = 1;
        public String termSetting = 'Termed';
        public Date endDate = Date.newInstance(2026, 12, 31);

        public CreateArgs(Id billingAccountId) {
            this.billingAccountId = billingAccountId;
        }

        public RLM_BillingScheduleGroupService.CreateResult call() {
            return RLM_BillingScheduleGroupService.createBillingScheduleGroupAndScheduleViaAPI(
                billingAccountId, billingTermUnit, billingTerm, billingType, quantity, legalEntityId,
                taxTreatmentId, currencyIsoCode, unitPrice, totalPrice, billingCity, productId,
                productName, startDate, billingDayOfMonth, billingStartMonth, termSetting, endDate
            );
        }
    }

    private static Boolean throwsAura(CreateArgs args) {
        try {
            args.call();
            return false;
        } catch (AuraHandledException e) {
            return true;
        }
    }

    private static Id insertBillingAccount(String name) {
        Account a = new Account(Name = name + ' Acct');
        insert a;
        BillingAccount ba = new BillingAccount(Name = name + ' BA', AccountId = a.Id);
        insert ba;
        return ba.Id;
    }

    private static Map<String, Object> onlyTransaction(String payload) {
        Map<String, Object> wrapper = (Map<String, Object>) System.JSON.deserializeUntyped(payload);
        List<Object> txns = (List<Object>) wrapper.get('Transaction');
        Assert.areEqual(1, txns.size(), 'The payload carries exactly one transaction.');
        return (Map<String, Object>) txns[0];
    }

    private static String sellingModelFor(String termSetting) {
        Map<String, Object> txn = onlyTransaction(RLM_BillingScheduleGroupService.buildTransactionDetailsJson(
            fakeId(Account.SObjectType), fakeId(BillingAccount.SObjectType), 'Month', 1,
            fakeId(LegalEntity.SObjectType), fakeId(TaxTreatment.SObjectType), 'USD', 10, 10,
            'Boston', fakeId(Product2.SObjectType), 'Widget', Date.newInstance(2026, 1, 1), 1, 1,
            termSetting, null
        ));
        return (String) txn.get('SellingModelType__std');
    }

    // deserializeUntyped returns whole numbers as Integer and fractions as Decimal.
    private static Decimal toDecimal(Object value) {
        return value == null ? null : Decimal.valueOf(String.valueOf(value));
    }

    // The BillingSchedule field's picklist entries as "label|value", in describe order. The
    // field and its values ship with the Billing license, so both are preconditions.
    private static List<String> picklistLabelsAndValues(String fieldApi) {
        Map<String, Schema.SObjectField> fields = BillingSchedule.SObjectType.getDescribe().fields.getMap();
        Assert.isTrue(fields.containsKey(fieldApi), 'PRECONDITION: BillingSchedule.' + fieldApi + ' exists.');
        List<String> entries = new List<String>();
        for (Schema.PicklistEntry pe : fields.get(fieldApi).getDescribe().getPicklistValues()) {
            entries.add(pe.getLabel() + '|' + pe.getValue());
        }
        Assert.isFalse(entries.isEmpty(), 'PRECONDITION: BillingSchedule.' + fieldApi + ' has picklist values.');
        return entries;
    }

    private static Set<String> optionValues(List<RLM_BillingScheduleGroupService.PicklistOption> options) {
        Set<String> values = new Set<String>();
        for (RLM_BillingScheduleGroupService.PicklistOption o : options) {
            values.add(o.value);
        }
        return values;
    }

    private static void assertOptions(List<String> expected,
            List<RLM_BillingScheduleGroupService.PicklistOption> actual) {
        List<String> actualEntries = new List<String>();
        for (RLM_BillingScheduleGroupService.PicklistOption o : actual) {
            actualEntries.add(o.label + '|' + o.value);
        }
        Assert.areEqual(expected, actualEntries, 'Option labels and values must match the picklist, in order.');
    }

    private static Boolean throwsViaApi(Id billingAccountId) {
        try {
            RLM_BillingScheduleGroupService.createBillingScheduleGroupAndScheduleViaAPI(
                billingAccountId, 'Month', 1, 'Advance', 1, fakeId(LegalEntity.SObjectType),
                fakeId(TaxTreatment.SObjectType), 'USD', 10, 10, 'San Francisco',
                fakeId(Product2.SObjectType), 'Widget', Date.today(), 1, 1, 'Evergreen', null
            );
            return false;
        } catch (AuraHandledException e) {
            return true;
        }
    }
}
