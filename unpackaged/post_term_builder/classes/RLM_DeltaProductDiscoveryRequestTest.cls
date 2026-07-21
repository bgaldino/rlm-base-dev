/**
 * Unit tests for the RLM_DeltaProductDiscoveryRequest builder. Pure assembly logic — no live action.
 * Asserts the assembled parameter maps via the @TestVisible accessors, the limit clamp, the
 * product-vs-recommendation paging-name mapping, the distinct getCategories vocabulary, and that
 * withDisplayFields produces a well-formed runtime_industries_cpq.AdditionalFields object.
 */
@IsTest
private class RLM_DeltaProductDiscoveryRequestTest {

    @IsTest
    static void testProductParamsOnlyNonNull() {
        RLM_DeltaProductDiscoveryRequest req = new RLM_DeltaProductDiscoveryRequest()
            .withSearchTerm('widget')
            .withCurrency('USD');
        Map<String, Object> params = req.buildProductParameterMap(false);
        System.assertEquals('widget', params.get('searchTerm'), 'searchTerm applied');
        System.assertEquals('USD', params.get('currencyCode'), 'currencyCode applied');
        System.assertEquals(false, params.containsKey('catalogId'), 'null catalogId not applied');
        System.assertEquals(false, params.containsKey('contextDefinition'), 'null contextDefinition not applied');
        System.assertEquals(false, params.containsKey('additionalFields'), 'no display fields → no additionalFields param');
    }

    @IsTest
    static void testLimitClampsTo100() {
        RLM_DeltaProductDiscoveryRequest req = new RLM_DeltaProductDiscoveryRequest().withPaging(500, 'CUR');
        Map<String, Object> params = req.buildProductParameterMap(false);
        System.assertEquals(100, params.get('limit'), 'limit clamps to PD_MAX_LIMIT');
        System.assertEquals('CUR', params.get('cursor'), 'cursor passed through under the search/browse name');
    }

    @IsTest
    static void testLimitClampsToAtLeastOne() {
        RLM_DeltaProductDiscoveryRequest req = new RLM_DeltaProductDiscoveryRequest().withPaging(0, null);
        Map<String, Object> params = req.buildProductParameterMap(false);
        System.assertEquals(1, params.get('limit'), 'limit clamps up to 1');
        System.assertEquals(false, params.containsKey('cursor'), 'blank cursor not applied');
    }

    @IsTest
    static void testRecommendationPagingNames() {
        RLM_DeltaProductDiscoveryRequest req = new RLM_DeltaProductDiscoveryRequest().withPaging(25, 'NEXT');
        Map<String, Object> params = req.buildProductParameterMap(true);
        System.assertEquals(25, params.get('pageSize'), 'recommendation uses pageSize');
        System.assertEquals('NEXT', params.get('nextCursor'), 'recommendation uses nextCursor');
        System.assertEquals(false, params.containsKey('limit'), 'recommendation does not use limit');
        System.assertEquals(false, params.containsKey('cursor'), 'recommendation does not use cursor');
    }

    @IsTest
    static void testTransactionIdFromQuote() {
        Id quoteId = '0Q0000000000001AAA';
        RLM_DeltaProductDiscoveryRequest req = new RLM_DeltaProductDiscoveryRequest().forQuote(quoteId);
        Map<String, Object> params = req.buildProductParameterMap(false);
        System.assertEquals(String.valueOf(quoteId), params.get('transactionId'), 'quote → transactionId');
    }

    @IsTest
    static void testCategoryParamsUseDistinctVocabulary() {
        Id catalogId = '0ZS000000000001AAA';
        Id parentId = '0ZG000000000001AAA';
        RLM_DeltaProductDiscoveryRequest req = new RLM_DeltaProductDiscoveryRequest()
            .withCatalog(catalogId)
            .withParentCategory(parentId)
            .withCategoryNestLevel(2)
            .withContextDefinition('MyContext')
            .withContextMapping('MyMapping')
            .withQualification(true)
            // These must be IGNORED by the category path:
            .withPaging(50, 'CUR')
            .withDisplayFields(new Map<String, List<String>>{ 'Product2' => new List<String>{ 'Family' } });
        Map<String, Object> params = req.buildCategoryParameterMap();
        System.assertEquals(String.valueOf(catalogId), params.get('catalogId'), 'catalogId applied');
        System.assertEquals(String.valueOf(parentId), params.get('parentCategoryId'), 'parentCategoryId applied');
        System.assertEquals(2, params.get('categoryNestLevel'), 'categoryNestLevel applied');
        System.assertEquals('MyContext', params.get('contextDefinitionName'), 'uses *Name context param');
        System.assertEquals('MyMapping', params.get('contextMappingName'), 'uses *Name mapping param');
        System.assertEquals(true, params.get('enableQualificationProcedure'), 'uses *Procedure qualification flag');
        System.assertEquals(false, params.containsKey('contextDefinition'), 'bare contextDefinition NOT applied to categories');
        System.assertEquals(false, params.containsKey('limit'), 'paging NOT applied to categories');
        System.assertEquals(false, params.containsKey('cursor'), 'paging NOT applied to categories');
        System.assertEquals(false, params.containsKey('additionalFields'), 'additionalFields NOT applied to categories');
    }

    @IsTest
    static void testDisplayFieldsBuildAdditionalFields() {
        RLM_DeltaProductDiscoveryRequest req = new RLM_DeltaProductDiscoveryRequest()
            .withDisplayFields(new Map<String, List<String>>{
                'Product2' => new List<String>{ 'Family', 'Description' }
            });
        runtime_industries_cpq.AdditionalFields af = req.buildAdditionalFields();
        System.assertNotEquals(null, af, 'AdditionalFields object built');
        System.assertEquals(true, af.additionalFields.containsKey('Product2'), 'Product2 key present');
        System.assertEquals(
            new List<String>{ 'Family', 'Description' },
            af.additionalFields.get('Product2').fields,
            'fields populated on the AdditionalFieldsInput'
        );

        // And it lands in the product parameter map.
        Map<String, Object> params = req.buildProductParameterMap(false);
        System.assert(params.get('additionalFields') instanceof runtime_industries_cpq.AdditionalFields,
            'additionalFields param is the typed object');
    }

    @IsTest
    static void testDisplayFieldsEmptyYieldsNull() {
        RLM_DeltaProductDiscoveryRequest req = new RLM_DeltaProductDiscoveryRequest()
            .withDisplayFields(new Map<String, List<String>>{ 'Product2' => new List<String>() });
        System.assertEquals(null, req.buildAdditionalFields(), 'empty field list → no AdditionalFields object');
    }

    @IsTest
    static void testContextDefinitionBlankOmitted() {
        RLM_DeltaProductDiscoveryRequest req = new RLM_DeltaProductDiscoveryRequest().withContextDefinition('   ');
        Map<String, Object> params = req.buildProductParameterMap(false);
        System.assertEquals(false, params.containsKey('contextDefinition'),
            'blank context definition omitted → Settings default used');
    }
}
