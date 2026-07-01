@isTest
private class RLM_AI_ProductAttributeSaveServiceTest {
    @isTest
    static void saveReturnsSuccessWhenSubmittedAttributesAreUnknown() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('RLM Save Service Product');

        RLM_AI_ProductAttributeSaveService.SaveInput input =
            new RLM_AI_ProductAttributeSaveService.SaveInput();
        input.quoteId = String.valueOf(fixture.quoteId);
        input.quoteLineItemId = String.valueOf(fixture.quoteLineItemId);
        input.attributeSelectionsJson = '{"UnknownAttribute":"SomeValue"}';

        Test.startTest();
        List<RLM_AI_ProductAttributeSaveService.SaveOutput> results =
            RLM_AI_ProductAttributeSaveService.saveAttributeSelections(
                new List<RLM_AI_ProductAttributeSaveService.SaveInput>{ input }
            );
        Test.stopTest();

        System.assertEquals(1, results.size());
        System.assertEquals(true, results[0].isSuccess);
        System.assertEquals(true, results[0].isValid);
        System.assertEquals('[]', results[0].validationErrorsJson);
        System.assert(results[0].savedAttributesJson.contains('UnknownAttribute'));
    }

    @isTest
    static void saveHandlesMalformedJson() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('RLM Malformed JSON Product');

        RLM_AI_ProductAttributeSaveService.SaveInput input =
            new RLM_AI_ProductAttributeSaveService.SaveInput();
        input.quoteId = String.valueOf(fixture.quoteId);
        input.quoteLineItemId = String.valueOf(fixture.quoteLineItemId);
        input.attributeSelectionsJson = '{bad json';

        List<RLM_AI_ProductAttributeSaveService.SaveOutput> results =
            RLM_AI_ProductAttributeSaveService.saveAttributeSelections(
                new List<RLM_AI_ProductAttributeSaveService.SaveInput>{ input }
            );

        System.assertEquals(false, results[0].isSuccess);
        System.assertEquals(false, results[0].isValid);
        System.assertNotEquals(null, results[0].errorMessage);
    }

    @isTest
    static void saveGuidesUserWhenIdsAreInvalid() {
        RLM_AI_ProductAttributeSaveService.SaveInput input =
            new RLM_AI_ProductAttributeSaveService.SaveInput();
        input.quoteId = 'not-a-quote-id';
        input.quoteLineItemId = 'not-a-quote-line-id';
        input.attributeSelectionsJson = '{}';

        List<RLM_AI_ProductAttributeSaveService.SaveOutput> results =
            RLM_AI_ProductAttributeSaveService.saveAttributeSelections(
                new List<RLM_AI_ProductAttributeSaveService.SaveInput>{ input }
            );

        System.assertEquals(false, results[0].isSuccess);
        System.assertEquals(false, results[0].isValid);
        System.assertEquals('Select a valid quote before saving product configuration.', results[0].errorMessage);
    }

    @isTest
    static void saveGuidesUserWhenQuoteLineBelongsToDifferentQuote() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture firstFixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('RLM First Quote Product');
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture secondFixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('RLM Second Quote Product');

        RLM_AI_ProductAttributeSaveService.SaveInput input =
            new RLM_AI_ProductAttributeSaveService.SaveInput();
        input.quoteId = String.valueOf(firstFixture.quoteId);
        input.quoteLineItemId = String.valueOf(secondFixture.quoteLineItemId);
        input.attributeSelectionsJson = '{}';

        List<RLM_AI_ProductAttributeSaveService.SaveOutput> results =
            RLM_AI_ProductAttributeSaveService.saveAttributeSelections(
                new List<RLM_AI_ProductAttributeSaveService.SaveInput>{ input }
            );

        System.assertEquals(false, results[0].isSuccess);
        System.assertEquals(false, results[0].isValid);
        System.assertEquals(
            'Select a quote line item that belongs to the current quote before saving product configuration.',
            results[0].errorMessage
        );
    }
}
