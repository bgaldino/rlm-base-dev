@isTest
private class RLM_AI_QuoteLineItemLookupServiceTest {
    @isTest
    static void lookupReturnsMatchWhenProductExists() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('FESBA Generator Set');

        RLM_AI_QuoteLineItemLookupService.LookupInput input =
            new RLM_AI_QuoteLineItemLookupService.LookupInput();
        input.quoteId = String.valueOf(fixture.quoteId);
        input.productName = 'Generator';

        Test.startTest();
        List<RLM_AI_QuoteLineItemLookupService.LookupOutput> results =
            RLM_AI_QuoteLineItemLookupService.lookup(
                new List<RLM_AI_QuoteLineItemLookupService.LookupInput>{ input }
            );
        Test.stopTest();

        System.assertEquals(1, results.size(), 'One result should be returned.');
        System.assertEquals(true, results[0].isFound, 'Expected product match.');
        System.assertEquals(String.valueOf(fixture.quoteLineItemId), results[0].quoteLineItemId);
        System.assertEquals('FESBA Generator Set', results[0].productNameFound);
    }

    @isTest
    static void lookupReturnsNotFoundWhenNoMatch() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('FESBA Generator Set');

        RLM_AI_QuoteLineItemLookupService.LookupInput input =
            new RLM_AI_QuoteLineItemLookupService.LookupInput();
        input.quoteId = String.valueOf(fixture.quoteId);
        input.productName = 'NoSuchProduct';

        List<RLM_AI_QuoteLineItemLookupService.LookupOutput> results =
            RLM_AI_QuoteLineItemLookupService.lookup(
                new List<RLM_AI_QuoteLineItemLookupService.LookupInput>{ input }
            );

        System.assertEquals(false, results[0].isFound);
        System.assertNotEquals(null, results[0].errorMessage);
        System.assert(results[0].errorMessage.contains('No QuoteLineItem found'));
    }

    @isTest
    static void lookupHandlesInvalidQuoteId() {
        RLM_AI_QuoteLineItemLookupService.LookupInput input =
            new RLM_AI_QuoteLineItemLookupService.LookupInput();
        input.quoteId = 'not-an-id';
        input.productName = 'Generator';

        List<RLM_AI_QuoteLineItemLookupService.LookupOutput> results =
            RLM_AI_QuoteLineItemLookupService.lookup(
                new List<RLM_AI_QuoteLineItemLookupService.LookupInput>{ input }
            );

        System.assertEquals(false, results[0].isFound);
        System.assertNotEquals(null, results[0].errorMessage);
    }
}
