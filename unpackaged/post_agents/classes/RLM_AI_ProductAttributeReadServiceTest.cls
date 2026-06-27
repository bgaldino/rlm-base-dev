@isTest
private class RLM_AI_ProductAttributeReadServiceTest {
    @isTest
    static void readReturnsEmptySummaryWhenNoAttributesExist() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('RLM Read Service Product');

        RLM_AI_ProductAttributeReadService.ReadInput input =
            new RLM_AI_ProductAttributeReadService.ReadInput();
        input.quoteLineItemId = String.valueOf(fixture.quoteLineItemId);

        Test.startTest();
        List<RLM_AI_ProductAttributeReadService.ReadOutput> results =
            RLM_AI_ProductAttributeReadService.getSavedAttributeValues(
                new List<RLM_AI_ProductAttributeReadService.ReadInput>{ input }
            );
        Test.stopTest();

        System.assertEquals(1, results.size());
        System.assertEquals('{}', results[0].savedAttributesJson);
        System.assertEquals('', results[0].configurationSummary);
        System.assertEquals(null, results[0].errorMessage);
        System.assertEquals(true, results[0].isSuccess);
    }

    @isTest
    static void readHandlesInvalidQuoteLineItemId() {
        RLM_AI_ProductAttributeReadService.ReadInput input =
            new RLM_AI_ProductAttributeReadService.ReadInput();
        input.quoteLineItemId = 'not-an-id';

        List<RLM_AI_ProductAttributeReadService.ReadOutput> results =
            RLM_AI_ProductAttributeReadService.getSavedAttributeValues(
                new List<RLM_AI_ProductAttributeReadService.ReadInput>{ input }
            );

        System.assertEquals(1, results.size());
        System.assertEquals('{}', results[0].savedAttributesJson);
        System.assertEquals('', results[0].configurationSummary);
        System.assertEquals(false, results[0].isSuccess);
        System.assertEquals('Select a valid quote line item before reading saved attribute values.', results[0].errorMessage);
    }
}
