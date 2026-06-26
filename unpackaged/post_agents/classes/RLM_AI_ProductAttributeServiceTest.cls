@isTest
private class RLM_AI_ProductAttributeServiceTest {
    @isTest
    static void returnsNoConfigurableAttributesWhenProductHasNoClassification() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('RLM No Classification Product');

        RLM_AI_ProductAttributeService.GetAttributeOptionsInput input =
            new RLM_AI_ProductAttributeService.GetAttributeOptionsInput();
        input.quoteLineItemId = String.valueOf(fixture.quoteLineItemId);

        Test.startTest();
        List<RLM_AI_ProductAttributeService.GetAttributeOptionsOutput> results =
            RLM_AI_ProductAttributeService.getProductAttributeOptions(
                new List<RLM_AI_ProductAttributeService.GetAttributeOptionsInput>{ input }
            );
        Test.stopTest();

        System.assertEquals(1, results.size());
        System.assertEquals('RLM No Classification Product', results[0].productName);
        System.assertEquals(false, results[0].hasConfigurableAttributes);
        System.assertEquals('[]', results[0].attributesJson);
    }

    @isTest
    static void handlesInvalidQuoteLineItemId() {
        RLM_AI_ProductAttributeService.GetAttributeOptionsInput input =
            new RLM_AI_ProductAttributeService.GetAttributeOptionsInput();
        input.quoteLineItemId = 'not-an-id';

        List<RLM_AI_ProductAttributeService.GetAttributeOptionsOutput> results =
            RLM_AI_ProductAttributeService.getProductAttributeOptions(
                new List<RLM_AI_ProductAttributeService.GetAttributeOptionsInput>{ input }
            );

        System.assertEquals(false, results[0].hasConfigurableAttributes);
        System.assertNotEquals(null, results[0].errorMessage);
    }
}
