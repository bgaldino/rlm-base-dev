@IsTest
private class RLM_SetUpQuoteInvocableTest {

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    /** Insert a minimal Quote directly (bypasses PST). */
    private static Quote insertTestQuote(String name) {
        Id pbId = Test.getStandardPricebookId();
        Quote q = new Quote(Name = name, Pricebook2Id = pbId);
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
        System.assertNotEquals(null, results[0], 'Output must not be null');
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
        System.assertNotEquals(null, results[0]);
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
    // loadDemoPricebookEntries()
    // -------------------------------------------------------------------------

    @IsTest
    static void testLoadDemoPricebookEntries_ReturnsListWithoutError() {
        Test.startTest();
        List<PricebookEntry> pbes = RLM_SetUpQuoteInvocable.loadDemoPricebookEntries();
        Test.stopTest();

        // In test context the Standard Pricebook exists but may have no PSM-linked PBEs;
        // assert the return is non-null and not more than the LIMIT.
        System.assertNotEquals(null, pbes, 'loadDemoPricebookEntries must not return null');
        System.assert(pbes.size() <= 20, 'loadDemoPricebookEntries must respect LIMIT 20');
    }

}
