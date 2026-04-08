@IsTest
private class RLM_SetUpQuoteLinePreviewTest {

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    /** Inserts a minimal Quote with the Standard Pricebook (no PST). */
    private static Quote insertTestQuote(String name) {
        Id pbId = Test.getStandardPricebookId();
        Quote q = new Quote(Name = name, Pricebook2Id = pbId);
        insert q;
        return q;
    }

    /**
     * Calls previewQuoteLineCounts and deserializes the response JSON.
     * Asserts the result is valid JSON and returns the map.
     */
    private static Map<String, Object> preview(Map<String, Object> payload) {
        String json = RLM_SetUpQuoteLinePreview.previewQuoteLineCounts(JSON.serialize(payload));
        System.assertNotEquals(null, json, 'previewQuoteLineCounts must return non-null JSON');
        return (Map<String, Object>) JSON.deserializeUntyped(json);
    }

    // -------------------------------------------------------------------------
    // Blank / invalid inputs
    // -------------------------------------------------------------------------

    @IsTest
    static void testPreview_BlankJson_ReturnsZeroResponse() {
        Test.startTest();
        String result = RLM_SetUpQuoteLinePreview.previewQuoteLineCounts(null);
        Test.stopTest();

        Map<String, Object> out = (Map<String, Object>) JSON.deserializeUntyped(result);
        System.assertEquals(null, out.get('error'), 'Blank input should produce no error');
        System.assertEquals(0, Integer.valueOf(String.valueOf(out.get('projectedTotal'))));
    }

    @IsTest
    static void testPreview_EmptyString_ReturnsZeroResponse() {
        Test.startTest();
        String result = RLM_SetUpQuoteLinePreview.previewQuoteLineCounts('');
        Test.stopTest();

        Map<String, Object> out = (Map<String, Object>) JSON.deserializeUntyped(result);
        System.assertEquals(0, Integer.valueOf(String.valueOf(out.get('projectedTotal'))));
    }

    @IsTest
    static void testPreview_InvalidJson_ReturnsError() {
        Test.startTest();
        String result = RLM_SetUpQuoteLinePreview.previewQuoteLineCounts('not-valid-json');
        Test.stopTest();

        Map<String, Object> out = (Map<String, Object>) JSON.deserializeUntyped(result);
        System.assertNotEquals(null, out.get('error'), 'Invalid JSON must produce an error message');
    }

    // -------------------------------------------------------------------------
    // Create mode — no existing quote
    // -------------------------------------------------------------------------

    @IsTest
    static void testPreview_CreateMode_NoHierarchy_ReturnsZero() {
        Test.startTest();
        Map<String, Object> out = preview(new Map<String, Object>{
            'isCreate' => true,
            'hierarchyJson' => '{"parents":[]}'
        });
        Test.stopTest();

        System.assertEquals(0, Integer.valueOf(String.valueOf(out.get('currentTotal'))));
        System.assertEquals(0, Integer.valueOf(String.valueOf(out.get('projectedTotal'))));
    }

    @IsTest
    static void testPreview_CreateMode_WithProductCounts_SumsCorrectly() {
        // productCountsJson has paths 0, 0-0, 0-1 with total 7
        String hierarchyJson = '{"parents":[{"name":"G","path":"0","children":['
            + '{"name":"G-A","path":"0-0","children":[]},'
            + '{"name":"G-B","path":"0-1","children":[]}'
            + ']}]}';
        String productCountsJson = '{"0":2,"0-0":3,"0-1":2}';

        Test.startTest();
        Map<String, Object> out = preview(new Map<String, Object>{
            'isCreate' => true,
            'hierarchyJson' => hierarchyJson,
            'productCountsJson' => productCountsJson
        });
        Test.stopTest();

        System.assertEquals(0, Integer.valueOf(String.valueOf(out.get('currentTotal'))),
            'No existing quote, so currentTotal must be 0');
        System.assertEquals(7, Integer.valueOf(String.valueOf(out.get('newLinesFromHierarchy'))),
            'New lines should sum product counts: 2+3+2=7');
        System.assertEquals(7, Integer.valueOf(String.valueOf(out.get('projectedTotal'))));
    }

    // -------------------------------------------------------------------------
    // Modify mode — existing quote line items
    // -------------------------------------------------------------------------

    @IsTest
    static void testPreview_ModifyMode_InvalidQuoteId_ReturnsError() {
        Test.startTest();
        Map<String, Object> out = preview(new Map<String, Object>{
            'isCreate' => false,
            'quoteId' => 'NOT_AN_ID',
            'hierarchyJson' => '{"parents":[]}'
        });
        Test.stopTest();

        System.assertNotEquals(null, out.get('error'), 'Invalid Id should produce an error');
    }

    @IsTest
    static void testPreview_ModifyMode_ValidQuote_CurrentTotalReflectsExistingLines() {
        Quote q = insertTestQuote('Preview Modify Test');

        Test.startTest();
        Map<String, Object> out = preview(new Map<String, Object>{
            'isCreate' => false,
            'quoteId' => q.Id,
            'hierarchyJson' => '{"parents":[]}'
        });
        Test.stopTest();

        System.assertEquals(0, Integer.valueOf(String.valueOf(out.get('currentTotal'))),
            'Freshly created quote should have 0 line items');
        System.assertEquals(null, out.get('error'));
    }

    // -------------------------------------------------------------------------
    // expandDeletedGroupIds — frontier BFS via previewQuoteLineCounts
    // -------------------------------------------------------------------------

    @IsTest
    static void testDeletedGroupsBFS_ParentAndChildIncluded() {
        Quote q = insertTestQuote('BFS Delete Test');

        // Create a parent group → child group → line item in child
        QuoteLineGroup parent = new QuoteLineGroup(QuoteId = q.Id, Name = 'Parent', SortOrder = 1);
        insert parent;
        QuoteLineGroup child = new QuoteLineGroup(
            QuoteId = q.Id, Name = 'Child', ParentQuoteLineGroupId = parent.Id, SortOrder = 1);
        insert child;

        // Create a PBE so we can insert a QuoteLineItem in the child group
        Id pbId = Test.getStandardPricebookId();
        Product2 prod = new Product2(Name = 'BFS Test Product', IsActive = true);
        insert prod;
        PricebookEntry pbe = new PricebookEntry(
            Pricebook2Id = pbId, Product2Id = prod.Id, UnitPrice = 10.00, IsActive = true);
        insert pbe;
        QuoteLineItem li = new QuoteLineItem(
            QuoteId = q.Id, QuoteLineGroupId = child.Id,
            Product2Id = prod.Id, PricebookEntryId = pbe.Id,
            Quantity = 1, UnitPrice = 10.00);
        insert li;

        // groupsToDeleteJson references only the parent — BFS should expand to child too
        String groupsToDeleteJson = JSON.serialize(new List<Id>{ parent.Id });

        Test.startTest();
        Map<String, Object> out = preview(new Map<String, Object>{
            'isCreate' => false,
            'quoteId' => q.Id,
            'groupsToDeleteJson' => groupsToDeleteJson,
            'hierarchyJson' => '{"parents":[]}'
        });
        Test.stopTest();

        System.assertEquals(1, Integer.valueOf(String.valueOf(out.get('linesRemovedFromDeletes'))),
            'BFS should expand to child group and count its line item as removed');
        System.assertNotEquals(null, out);
    }

    @IsTest
    static void testDeletedGroupsBFS_EmptyGroupsJson_NoLinesRemoved() {
        Quote q = insertTestQuote('BFS Empty Delete Test');

        Test.startTest();
        Map<String, Object> out = preview(new Map<String, Object>{
            'isCreate' => false,
            'quoteId' => q.Id,
            'groupsToDeleteJson' => '[]',
            'hierarchyJson' => '{"parents":[]}'
        });
        Test.stopTest();

        System.assertEquals(0, Integer.valueOf(String.valueOf(out.get('linesRemovedFromDeletes'))));
    }

    @IsTest
    static void testDeletedGroupsBFS_DeepNesting_AllDescendantsExpanded() {
        Quote q = insertTestQuote('BFS Deep Nesting Test');

        // Build: root → level1 → level2 (3 levels of nesting)
        QuoteLineGroup root = new QuoteLineGroup(QuoteId = q.Id, Name = 'Root', SortOrder = 1);
        insert root;
        QuoteLineGroup level1 = new QuoteLineGroup(
            QuoteId = q.Id, Name = 'Level1', ParentQuoteLineGroupId = root.Id, SortOrder = 1);
        insert level1;
        QuoteLineGroup level2 = new QuoteLineGroup(
            QuoteId = q.Id, Name = 'Level2', ParentQuoteLineGroupId = level1.Id, SortOrder = 1);
        insert level2;

        Id pbId = Test.getStandardPricebookId();
        Product2 prod = new Product2(Name = 'Deep BFS Product', IsActive = true);
        insert prod;
        PricebookEntry pbe = new PricebookEntry(
            Pricebook2Id = pbId, Product2Id = prod.Id, UnitPrice = 5.00, IsActive = true);
        insert pbe;
        // Line item sits in the deepest group only
        insert new QuoteLineItem(
            QuoteId = q.Id, QuoteLineGroupId = level2.Id,
            Product2Id = prod.Id, PricebookEntryId = pbe.Id,
            Quantity = 1, UnitPrice = 5.00);

        String groupsToDeleteJson = JSON.serialize(new List<Id>{ root.Id });

        Test.startTest();
        Map<String, Object> out = preview(new Map<String, Object>{
            'isCreate' => false,
            'quoteId' => q.Id,
            'groupsToDeleteJson' => groupsToDeleteJson,
            'hierarchyJson' => '{"parents":[]}'
        });
        Test.stopTest();

        System.assertEquals(1, Integer.valueOf(String.valueOf(out.get('linesRemovedFromDeletes'))),
            'BFS should traverse all 3 levels and count the line item in level2');
    }

}
