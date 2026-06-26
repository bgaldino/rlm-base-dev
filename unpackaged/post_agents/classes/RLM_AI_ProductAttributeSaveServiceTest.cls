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
        RLM_AI_ProductAttributeSaveService.SaveInput input =
            new RLM_AI_ProductAttributeSaveService.SaveInput();
        input.quoteId = '0Q0000000000000AAA';
        input.quoteLineItemId = '0QL000000000000AAA';
        input.attributeSelectionsJson = '{bad json';

        List<RLM_AI_ProductAttributeSaveService.SaveOutput> results =
            RLM_AI_ProductAttributeSaveService.saveAttributeSelections(
                new List<RLM_AI_ProductAttributeSaveService.SaveInput>{ input }
            );

        System.assertEquals(false, results[0].isSuccess);
        System.assertEquals(false, results[0].isValid);
        System.assertNotEquals(null, results[0].errorMessage);
    }
}
