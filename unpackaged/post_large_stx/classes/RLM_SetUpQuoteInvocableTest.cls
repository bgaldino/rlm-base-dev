@IsTest
private class RLM_SetUpQuoteInvocableTest {

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    /** Insert a minimal Quote with required related records (Account, Opportunity). */
    private static Quote insertTestQuote(String name) {
        Id pbId = Test.getStandardPricebookId();
        Account acct = new Account(Name = name + ' Account');
        insert acct;
        Opportunity opp = new Opportunity(
            Name = name + ' Opportunity',
            AccountId = acct.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;
        Quote q = new Quote(
            Name = name,
            Pricebook2Id = pbId,
            OpportunityId = opp.Id,
            Status = 'Draft'
        );
        insert q;
        return q;
    }

    /** Build a minimal create Input with hierarchyJson. */
    private static RLM_SetUpQuoteInvocable.Input makeCreateInput(String name, String hierarchyJson) {
        RLM_SetUpQuoteInvocable.Input i = new RLM_SetUpQuoteInvocable.Input();
        i.isCreate = true;
        i.newQuoteName = name;
        i.hierarchyJson = hierarchyJson;
        return i;
    }

    /** Build a minimal modify Input with hierarchyJson. */
    private static RLM_SetUpQuoteInvocable.Input makeModifyInput(String quoteId, String hierarchyJson) {
        RLM_SetUpQuoteInvocable.Input i = new RLM_SetUpQuoteInvocable.Input();
        i.isCreate = false;
        i.quoteId = quoteId;
        i.hierarchyJson = hierarchyJson;
        return i;
    }

    // -------------------------------------------------------------------------
    // execute() — input validation
    // -------------------------------------------------------------------------

    @IsTest
    static void testExecute_NullInputList_ReturnsFail() {
        Test.startTest();
        List<RLM_SetUpQuoteInvocable.Output> results = RLM_SetUpQuoteInvocable.execute(null);
        Test.stopTest();

        System.assertEquals(1, results.size(), 'Expected one output for null input');
        System.assertEquals(false, results[0].success, 'Expected failure for null input');
        System.assertNotEquals(null, results[0].errorMessage, 'Expected error message for null input');
    }

    @IsTest
    static void testExecute_EmptyInputList_ReturnsFail() {
        Test.startTest();
        List<RLM_SetUpQuoteInvocable.Output> results =
            RLM_SetUpQuoteInvocable.execute(new List<RLM_SetUpQuoteInvocable.Input>());
        Test.stopTest();

        System.assertEquals(1, results.size(), 'Expected one output for empty input list');
        System.assertEquals(false, results[0].success, 'Expected failure for empty input list');
    }

    @IsTest
    static void testExecute_ModifyMode_BlankQuoteId_ReturnsFail() {
        // isCreate=false + hierarchyJson with parents but no quoteId → throws before PST
        String hierarchyJson = '{"parents":[{"name":"Group A","path":"0","children":[]}]}';
        RLM_SetUpQuoteInvocable.Input inp = makeModifyInput(null, hierarchyJson);

        Test.startTest();
        List<RLM_SetUpQuoteInvocable.Output> results =
            RLM_SetUpQuoteInvocable.execute(new List<RLM_SetUpQuoteInvocable.Input>{ inp });
        Test.stopTest();

        System.assertEquals(1, results.size());
        System.assertEquals(false, results[0].success, 'Modify with blank quoteId must fail');
    }

    @IsTest
    static void testExecute_CreateMode_EmptyHierarchy_FailsGracefully() {
        // isCreate=true, name set, empty parents array → attempts PST which fails in test; must not throw
        RLM_SetUpQuoteInvocable.Input inp = makeCreateInput('Test Quote', '{"parents":[]}');

        Test.startTest();
        List<RLM_SetUpQuoteInvocable.Output> results =
            RLM_SetUpQuoteInvocable.execute(new List<RLM_SetUpQuoteInvocable.Input>{ inp });
        Test.stopTest();

        // PST may succeed or fail in test context; what matters is we get a result, not an exception
        System.assertEquals(1, results.size(), 'Should always return one output');
        // Same provable contract as the with-hierarchy case: execute() always decides
        // success and keeps errorMessage/quoteId consistent, in both reachable branches.
        RLM_SetUpQuoteInvocable.Output out0 = results[0];
        System.assertNotEquals(null, out0, 'Output must not be null');
        System.assertNotEquals(null, out0.success, 'execute() must always decide success (true or false), never leave it null');
        if (out0.success == true) {
            System.assertEquals(null, out0.errorMessage, 'Success output must have a null errorMessage');
        } else {
            System.assertNotEquals(null, out0.errorMessage, 'Failure output must carry an errorMessage');
            System.assert(out0.errorMessage.startsWith('Quote creation failed: '),
                'Create-mode failure must use the catch-path message prefix; got: ' + out0.errorMessage);
            System.assertEquals(null, out0.quoteId, 'Failure output must not carry a quoteId');
        }
    }

    @IsTest
    static void testExecute_CreateMode_WithHierarchy_FailsGracefully() {
        // PST will fail in test without full org config; execute() should catch and return fail output
        String hierarchyJson = '{"parents":[{"name":"Group A","path":"0","children":[]}]}';
        RLM_SetUpQuoteInvocable.Input inp = makeCreateInput('Test Quote', hierarchyJson);
        inp.productCountsJson = '{"0":0}';

        Test.startTest();
        List<RLM_SetUpQuoteInvocable.Output> results =
            RLM_SetUpQuoteInvocable.execute(new List<RLM_SetUpQuoteInvocable.Input>{ inp });
        Test.stopTest();

        System.assertEquals(1, results.size(), 'Should always return one output');
        // PST is non-deterministic in test context (success depends on full RLM/PST org
        // config), so we assert the contract that holds in BOTH branches of execute():
        // success is always decided (never left null), and errorMessage is consistent with it.
        // On success execute() sets success=true + errorMessage=null; on the only reachable
        // failure path it returns fail(null, 'Quote creation failed: ' + msg).
        RLM_SetUpQuoteInvocable.Output out0 = results[0];
        System.assertNotEquals(null, out0, 'Output must not be null');
        System.assertNotEquals(null, out0.success, 'execute() must always decide success (true or false), never leave it null');
        if (out0.success == true) {
            System.assertEquals(null, out0.errorMessage, 'Success output must have a null errorMessage');
        } else {
            System.assertNotEquals(null, out0.errorMessage, 'Failure output must carry an errorMessage');
            System.assert(out0.errorMessage.startsWith('Quote creation failed: '),
                'Create-mode failure must use the catch-path message prefix; got: ' + out0.errorMessage);
            System.assertEquals(null, out0.quoteId, 'Failure output must not carry a quoteId');
        }
    }

    // -------------------------------------------------------------------------
    // runSetUpQuoteFromLWC()
    // -------------------------------------------------------------------------

    @IsTest
    static void testRunSetUpQuoteFromLWC_BlankInput_ReturnsErrorJson() {
        Test.startTest();
        String result = RLM_SetUpQuoteInvocable.runSetUpQuoteFromLWC(null);
        Test.stopTest();

        Map<String, Object> out = (Map<String, Object>) JSON.deserializeUntyped(result);
        System.assertEquals(false, out.get('success'), 'Blank input must return success=false');
        System.assertNotEquals(null, out.get('errorMessage'), 'Blank input must return errorMessage');
    }

    @IsTest
    static void testRunSetUpQuoteFromLWC_ModifyBlankId_ReturnsErrorJson() {
        String inputJson = JSON.serialize(new Map<String, Object>{
            'isCreate' => false,
            'quoteId' => null,
            'hierarchyJson' => '{"parents":[{"name":"A","path":"0","children":[]}]}'
        });

        Test.startTest();
        String result = RLM_SetUpQuoteInvocable.runSetUpQuoteFromLWC(inputJson);
        Test.stopTest();

        Map<String, Object> out = (Map<String, Object>) JSON.deserializeUntyped(result);
        System.assertEquals(false, out.get('success'), 'Modify with blank quoteId must fail');
    }

    // -------------------------------------------------------------------------
    // getQuotesForModify()
    // -------------------------------------------------------------------------

    @IsTest
    static void testGetQuotesForModify_ReturnsListWithoutError() {
        Test.startTest();
        List<Map<String, String>> options = RLM_SetUpQuoteInvocable.getQuotesForModify();
        Test.stopTest();

        System.assertNotEquals(null, options, 'getQuotesForModify should return a non-null list');
    }

    @IsTest
    static void testGetQuotesForModify_IncludesInsertedQuote() {
        Quote q = insertTestQuote('My Test Quote');

        Test.startTest();
        List<Map<String, String>> options = RLM_SetUpQuoteInvocable.getQuotesForModify();
        Test.stopTest();

        Boolean found = false;
        for (Map<String, String> opt : options) {
            if (opt.get('value') == q.Id) { found = true; break; }
        }
        System.assert(found, 'getQuotesForModify should include the inserted quote');
    }

    // -------------------------------------------------------------------------
    // getQuoteHierarchy()
    // -------------------------------------------------------------------------

    @IsTest
    static void testGetQuoteHierarchy_BlankId_ReturnsEmptyParents() {
        Test.startTest();
        String result = RLM_SetUpQuoteInvocable.getQuoteHierarchy(null);
        Test.stopTest();

        Map<String, Object> out = (Map<String, Object>) JSON.deserializeUntyped(result);
        List<Object> parents = (List<Object>) out.get('parents');
        System.assertNotEquals(null, parents, 'parents must be present');
        System.assertEquals(0, parents.size(), 'parents must be empty for blank quoteId');
    }

    @IsTest
    static void testGetQuoteHierarchy_QuoteWithGroups_ReturnsHierarchy() {
        Quote q = insertTestQuote('Hierarchy Test Quote');
        QuoteLineGroup parent = new QuoteLineGroup(QuoteId = q.Id, Name = 'Parent Group', SortOrder = 1);
        insert parent;
        QuoteLineGroup child = new QuoteLineGroup(
            QuoteId = q.Id, Name = 'Child Group', ParentQuoteLineGroupId = parent.Id, SortOrder = 1);
        insert child;

        Test.startTest();
        String result = RLM_SetUpQuoteInvocable.getQuoteHierarchy(q.Id);
        Test.stopTest();

        Map<String, Object> out = (Map<String, Object>) JSON.deserializeUntyped(result);
        List<Object> parents = (List<Object>) out.get('parents');
        System.assertEquals(1, parents.size(), 'Should have one root group');
        Map<String, Object> parentNode = (Map<String, Object>) parents[0];
        List<Object> children = (List<Object>) parentNode.get('children');
        System.assertEquals(1, children.size(), 'Root should have one child');
    }

    // -------------------------------------------------------------------------
    // sumProductCountsJsonValues()
    // -------------------------------------------------------------------------

    @IsTest
    static void testSumProductCountsJsonValues_Blank_ReturnsZero() {
        System.assertEquals(0, RLM_SetUpQuoteInvocable.sumProductCountsJsonValues(null));
        System.assertEquals(0, RLM_SetUpQuoteInvocable.sumProductCountsJsonValues(''));
    }

    @IsTest
    static void testSumProductCountsJsonValues_ValidJson_ReturnsSum() {
        String json = '{"0":3,"0-0":2,"0-1":5}';
        System.assertEquals(10, RLM_SetUpQuoteInvocable.sumProductCountsJsonValues(json));
    }

    @IsTest
    static void testSumProductCountsJsonValues_InvalidJson_ReturnsZero() {
        System.assertEquals(0, RLM_SetUpQuoteInvocable.sumProductCountsJsonValues('not-json'));
    }

    @IsTest
    static void testSumProductCountsJsonValues_ZeroValues_ReturnsZero() {
        String json = '{"0":0,"1":0}';
        System.assertEquals(0, RLM_SetUpQuoteInvocable.sumProductCountsJsonValues(json));
    }

    // -------------------------------------------------------------------------
    // New public surface: UI config, product-set detection, status, repeat-buy,
    // CSV preview helpers
    // -------------------------------------------------------------------------

    @IsTest
    static void testGetSetUpQuoteUiConfig_ReturnsJsonWithFlag() {
        Test.startTest();
        String cfgJson = RLM_SetUpQuoteInvocable.getSetUpQuoteUiConfig();
        Test.stopTest();

        Map<String, Object> out = (Map<String, Object>) JSON.deserializeUntyped(cfgJson);
        System.assert(out.containsKey('showProductSetSelector'), 'UI config must expose showProductSetSelector');
    }

    @IsTest
    static void testDetectQuoteProductSetMode_BlankAndNoLines_DefaultsQuantumBit() {
        System.assertEquals(
            RLM_SetUpQuoteProductSets.PRODUCT_SET_QUANTUMBIT,
            RLM_SetUpQuoteInvocable.detectQuoteProductSetMode(null),
            'Blank quoteId defaults to QuantumBit'
        );

        Quote q = insertTestQuote('Detect Mode Quote');
        Test.startTest();
        String mode = RLM_SetUpQuoteInvocable.detectQuoteProductSetMode(q.Id);
        Test.stopTest();
        System.assertEquals(
            RLM_SetUpQuoteProductSets.PRODUCT_SET_QUANTUMBIT,
            mode,
            'Quote with no Siemens lines defaults to QuantumBit'
        );
    }

    @IsTest
    static void testGetSetUpQuoteStatus_BlankReturnsFailure() {
        Map<String, Object> blank = (Map<String, Object>) JSON.deserializeUntyped(
            RLM_SetUpQuoteInvocable.getSetUpQuoteStatus(null));
        System.assertEquals(false, blank.get('success'), 'Blank quoteId returns success=false');
    }

    @IsTest
    static void testGetSetUpQuoteStatus_ValidQuoteReturnsCounts() {
        Quote q = insertTestQuote('Status Quote');

        Test.startTest();
        Map<String, Object> out = (Map<String, Object>) JSON.deserializeUntyped(
            RLM_SetUpQuoteInvocable.getSetUpQuoteStatus(q.Id));
        Test.stopTest();

        System.assertEquals(true, out.get('success'), 'Valid quoteId returns success=true');
        System.assertEquals(0, Integer.valueOf(String.valueOf(out.get('qliCount'))), 'Fresh quote has 0 QLIs');
        System.assertEquals(0, Integer.valueOf(String.valueOf(out.get('groupCount'))), 'Fresh quote has 0 groups');
    }

    @IsTest
    static void testRepeatBuyHelpers_ReturnWithoutError() {
        Account acct = new Account(Name = 'Repeat Buy Account');
        insert acct;

        Test.startTest();
        List<Map<String, String>> accts = RLM_SetUpQuoteInvocable.getAccountsForRepeatBuy();
        List<Map<String, String>> recent = RLM_SetUpQuoteInvocable.getRecentQuotesForRepeatBuy(acct.Id);
        String lines = RLM_SetUpQuoteInvocable.getRepeatBuyLines('[]');
        Test.stopTest();

        System.assertNotEquals(null, accts, 'getAccountsForRepeatBuy returns a list');
        System.assertNotEquals(null, recent, 'getRecentQuotesForRepeatBuy returns a list');
        System.assertEquals('[]', lines, 'Empty quote-id array returns empty JSON array');
    }

    @IsTest
    static void testCsvImportPreviewHelpers_UnknownProductResolvesToZero() {
        String hierarchyJson = '{"parents":[{"name":"G","path":"0","children":[]}]}';
        Set<String> paths = new Set<String>();
        RLM_SetUpQuoteInvocable.collectHierarchyPathsIntoSet(hierarchyJson, paths);
        System.assert(paths.contains('0'), 'Should collect hierarchy path "0"');

        String csvJson = '[{"path":"0","productIdentifier":"DOES-NOT-EXIST","quantity":2}]';
        Test.startTest();
        Integer count = RLM_SetUpQuoteInvocable.countCsvImportLinesForPreview(hierarchyJson, csvJson);
        Test.stopTest();
        System.assertEquals(0, count, 'Unknown product resolves to 0 preview lines');
    }

    // -------------------------------------------------------------------------
    // buildCreateQuoteHeaderFields() — billing header parity with RLM_QuickQuote
    // -------------------------------------------------------------------------

    @IsTest
    static void testBuildCreateQuoteHeaderFields_CopiesBillingInfoFromAccount() {
        Account acct = new Account(
            Name = 'Header Billing Account',
            BillingStreet = '415 Mission Street',
            BillingCity = 'San Francisco',
            BillingState = 'CA',
            BillingPostalCode = '94105',
            BillingCountry = 'US',
            ShippingStreet = '1 Market St',
            ShippingCity = 'San Francisco',
            ShippingState = 'CA',
            ShippingPostalCode = '94105',
            ShippingCountry = 'US'
        );
        insert acct;
        Contact con = new Contact(
            LastName = 'Buyer', AccountId = acct.Id, Email = 'buyer@example.com', Phone = '415-555-0100');
        insert con;

        RLM_SetUpQuoteInvocable.Input inp = makeCreateInput('Builder Quote', '{"parents":[]}');
        inp.quoteAccountId = acct.Id;

        Test.startTest();
        Map<String, Object> hdr =
            RLM_SetUpQuoteInvocable.buildCreateQuoteHeaderFields(inp, Test.getStandardPricebookId());
        Test.stopTest();

        // Account linkage + billing/shipping address copied from the Account.
        System.assertEquals(acct.Id, hdr.get('QuoteAccountId'), 'QuoteAccountId set');
        System.assertEquals('415 Mission Street', hdr.get('BillingStreet'), 'Billing street copied');
        System.assertEquals('San Francisco', hdr.get('BillingCity'), 'Billing city copied');
        System.assertEquals('94105', hdr.get('BillingPostalCode'), 'Billing postal copied');
        System.assertEquals('US', hdr.get('BillingCountry'), 'Billing country copied');
        System.assertEquals('1 Market St', hdr.get('ShippingStreet'), 'Shipping street copied');
        // Bill-to + primary contact and contact channels copied.
        System.assertEquals(con.Id, hdr.get('BillToContactId'), 'BillToContactId set to account contact');
        System.assertEquals(con.Id, hdr.get('ContactId'), 'ContactId set to account contact');
        System.assertEquals('buyer@example.com', hdr.get('Email'), 'Email copied from contact');
        System.assertEquals('415-555-0100', hdr.get('Phone'), 'Phone copied from contact');
        // Service dates + term always stamped on create.
        System.assertNotEquals(null, hdr.get('StartDate'), 'StartDate stamped');
        System.assertNotEquals(null, hdr.get('ExpirationDate'), 'ExpirationDate stamped');
        System.assertEquals(12, hdr.get('RLM_TermMonths__c'), 'Default term months stamped');
    }

    @IsTest
    static void testBuildCreateQuoteHeaderFields_NoAccount_StampsDatesOnly() {
        RLM_SetUpQuoteInvocable.Input inp = makeCreateInput('No Account Quote', '{"parents":[]}');

        Test.startTest();
        Map<String, Object> hdr =
            RLM_SetUpQuoteInvocable.buildCreateQuoteHeaderFields(inp, Test.getStandardPricebookId());
        Test.stopTest();

        System.assertEquals('No Account Quote', hdr.get('Name'), 'Name set');
        System.assertEquals(false, hdr.containsKey('QuoteAccountId'), 'No account → no QuoteAccountId');
        System.assertEquals(false, hdr.containsKey('BillingStreet'), 'No account → no billing address');
        System.assertNotEquals(null, hdr.get('StartDate'), 'StartDate still stamped without account');
        System.assertEquals(12, hdr.get('RLM_TermMonths__c'), 'Term still stamped without account');
    }

    // -------------------------------------------------------------------------
    // TransactionProcessingType -> PST preference mapping
    // -------------------------------------------------------------------------

    @IsTest
    static void testToPricingEnum_MapsValues() {
        System.assertEquals(RevSalesTrxn.PricingPreferenceEnum.SKIP,
            RLM_SetUpQuoteInvocable.toPricingEnum('Skip'), 'Skip -> SKIP');
        System.assertEquals(RevSalesTrxn.PricingPreferenceEnum.SYSTEM,
            RLM_SetUpQuoteInvocable.toPricingEnum('System'), 'System -> SYSTEM');
        System.assertEquals(RevSalesTrxn.PricingPreferenceEnum.FORCE,
            RLM_SetUpQuoteInvocable.toPricingEnum('Force'), 'Force -> FORCE');
        System.assertEquals(RevSalesTrxn.PricingPreferenceEnum.FORCE,
            RLM_SetUpQuoteInvocable.toPricingEnum(null), 'null -> FORCE (default)');
        System.assertEquals(RevSalesTrxn.PricingPreferenceEnum.FORCE,
            RLM_SetUpQuoteInvocable.toPricingEnum('Bogus'), 'unknown -> FORCE (default)');
    }

    @IsTest
    static void testToTaxEnum_OnlySkipSkips() {
        System.assertEquals(RevSalesTrxn.TaxPreferenceEnum.SKIP,
            RLM_SetUpQuoteInvocable.toTaxEnum('Skip'), 'Skip -> SKIP');
        System.assertEquals(null, RLM_SetUpQuoteInvocable.toTaxEnum(null), 'null -> run tax');
        System.assertEquals(null, RLM_SetUpQuoteInvocable.toTaxEnum('Run'), 'other -> run tax');
    }

    @IsTest
    static void testToCatalogRatesEnum_OnlyFetchFetches() {
        System.assertEquals(RevSalesTrxn.CatalogRatesPreferenceEnum.FETCH,
            RLM_SetUpQuoteInvocable.toCatalogRatesEnum('Fetch'), 'Fetch -> FETCH');
        System.assertEquals(null, RLM_SetUpQuoteInvocable.toCatalogRatesEnum(null), 'null -> no fetch');
        System.assertEquals(null, RLM_SetUpQuoteInvocable.toCatalogRatesEnum('Skip'), 'Skip -> no fetch');
    }

    @IsTest
    static void testResolvePstPrefs_BlankType_DefaultsForceRunTax() {
        RLM_SetUpQuoteInvocable.Input inp = makeCreateInput('Default Prefs', '{"parents":[]}');
        // transactionType left null
        RLM_SetUpQuoteInvocable.PstPrefs prefs = RLM_SetUpQuoteInvocable.resolvePstPrefs(inp);
        System.assertEquals(RevSalesTrxn.PricingPreferenceEnum.FORCE, prefs.pricingPref, 'Default pricing FORCE');
        System.assertEquals(null, prefs.taxPref, 'Default runs tax (null)');
        System.assertEquals(null, prefs.catalogRatesPref, 'Default does not fetch rates');
        System.assertEquals(null, prefs.typeDeveloperName, 'No type stamped when blank');
    }

    @IsTest
    static void testResolvePstPrefs_UnknownType_FallsBackToDefaults() {
        RLM_SetUpQuoteInvocable.Input inp = makeCreateInput('Unknown Prefs', '{"parents":[]}');
        inp.transactionType = 'RLM_SUQ_DoesNotExist';
        RLM_SetUpQuoteInvocable.PstPrefs prefs = RLM_SetUpQuoteInvocable.resolvePstPrefs(inp);
        System.assertEquals(RevSalesTrxn.PricingPreferenceEnum.FORCE, prefs.pricingPref, 'Unknown -> FORCE');
        System.assertEquals(null, prefs.taxPref, 'Unknown -> run tax');
        System.assertEquals(null, prefs.typeDeveloperName, 'Unknown -> nothing stamped');
    }

    @IsTest
    static void testBuildCreateQuoteHeaderFields_BlankType_NoTransactionTypeStamped() {
        RLM_SetUpQuoteInvocable.Input inp = makeCreateInput('No TPT', '{"parents":[]}');
        Map<String, Object> hdr =
            RLM_SetUpQuoteInvocable.buildCreateQuoteHeaderFields(inp, Test.getStandardPricebookId());
        System.assertEquals(false, hdr.containsKey('TransactionType'),
            'No TransactionType stamped when none selected');
    }

    /**
     * When the deployed RLM_SUQ_* TransactionProcessingType records exist (scratch/dev org),
     * a selected type maps to the expected prefs and is stamped on the header. Tolerant of
     * orgs that do not have the records so the test stays deterministic everywhere.
     */
    @IsTest
    @SuppressWarnings('PMD.ApexUnitTestClassShouldHaveAsserts')
    static void testResolvePstPrefs_KnownSkipType_WhenRecordPresent() {
        Boolean present = ![SELECT Id FROM TransactionProcessingType WHERE DeveloperName = 'RLM_SUQ_SkipPriceAndTax'].isEmpty();
        if (!present) {
            return; // records not deployed in this org — covered by mapper unit tests above
        }
        RLM_SetUpQuoteInvocable.Input inp = makeCreateInput('Skip Both', '{"parents":[]}');
        inp.transactionType = 'RLM_SUQ_SkipPriceAndTax';
        RLM_SetUpQuoteInvocable.PstPrefs prefs = RLM_SetUpQuoteInvocable.resolvePstPrefs(inp);
        System.assertEquals(RevSalesTrxn.PricingPreferenceEnum.SKIP, prefs.pricingPref, 'Maps to SKIP pricing');
        System.assertEquals(RevSalesTrxn.TaxPreferenceEnum.SKIP, prefs.taxPref, 'Maps to SKIP tax');
        System.assertEquals('RLM_SUQ_SkipPriceAndTax', prefs.typeDeveloperName, 'Validated name retained');

        Map<String, Object> hdr =
            RLM_SetUpQuoteInvocable.buildCreateQuoteHeaderFields(inp, Test.getStandardPricebookId());
        System.assertEquals('RLM_SUQ_SkipPriceAndTax', hdr.get('TransactionType'),
            'Validated TransactionType stamped on header');
    }

}
