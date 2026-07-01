@isTest
private class RLM_AI_AttributeResolverTest {

    // A null line id resolves to lineFound=false with no attributes (callers map
    // this to their own input-error message).
    @isTest
    static void nullLineIdReturnsNotFound() {
        RLM_AI_AttributeResolver.Resolution res = RLM_AI_AttributeResolver.resolve(null);
        System.assertEquals(false, res.lineFound, 'Null id should not resolve a line.');
        System.assertEquals(false, res.hasAttributes(), 'No attributes for a null id.');
    }

    // A real line on a product with no classification and no materialized
    // attributes resolves with lineFound=true but hasAttributes=false. This is
    // the shared "nothing configurable" signal both actions read.
    @isTest
    static void lineWithNoClassificationAndNoAttributesHasNoAttributes() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('RLM Resolver No Attr');

        Test.startTest();
        RLM_AI_AttributeResolver.Resolution res =
            RLM_AI_AttributeResolver.resolve(fixture.quoteLineItemId);
        Test.stopTest();

        System.assertEquals(true, res.lineFound, 'Line should be found.');
        System.assertEquals('RLM Resolver No Attr', res.productName);
        System.assertEquals(false, res.hasAttributes(),
            'No classification and no line attributes → nothing configurable.');
    }

    // toJson serializes the merged shape: every entry carries currentValue, and
    // picklist entries carry picklistValues.
    @isTest
    static void toJsonCarriesCurrentValueAndPicklistValues() {
        RLM_AI_AttributeResolver.ResolvedAttribute picklist =
            new RLM_AI_AttributeResolver.ResolvedAttribute();
        picklist.name = 'Type';
        picklist.developerName = 'Type';
        picklist.dataType = 'Picklist';
        picklist.isRequired = true;
        picklist.isPriceImpacting = true;
        picklist.currentValue = 'Flex';
        picklist.picklistValues = new List<String>{ 'Flex', 'Prod' };

        RLM_AI_AttributeResolver.ResolvedAttribute numeric =
            new RLM_AI_AttributeResolver.ResolvedAttribute();
        numeric.name = 'Quantity Tier';
        numeric.developerName = 'QuantityTier';
        numeric.dataType = 'Number';
        numeric.isRequired = false;
        numeric.isPriceImpacting = false;
        numeric.currentValue = null;
        numeric.picklistValues = new List<String>();

        String json = RLM_AI_AttributeResolver.toJson(
            new List<RLM_AI_AttributeResolver.ResolvedAttribute>{ picklist, numeric }
        );

        System.assert(json.contains('currentValue'), 'Every entry carries currentValue.');
        System.assert(json.contains('"Flex"'), 'Picklist current value present.');
        System.assert(json.contains('picklistValues'),
            'Picklist entry carries its valid values.');
    }

    @isTest
    static void toJsonHandlesNull() {
        System.assertEquals('[]', RLM_AI_AttributeResolver.toJson(null),
            'Null attribute list serializes to an empty array.');
    }
}
