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

    // ── Input guards ─────────────────────────────────────────────────────────
    //
    // Everything past the input guards needs QuoteLineItemAttribute rows on the
    // line. An Apex test cannot create them: ordinary DML is refused ("use
    // insertAsync() or insertImmediate()"), insertAsync is refused for this
    // object, and insertImmediate reports success but the row is never
    // queryable. The Place Sales Transaction path is therefore not unit-tested.

    @isTest
    static void saveReturnsNoResultsForNullOrEmptyInput() {
        Test.startTest();
        List<RLM_AI_ProductAttributeSaveService.SaveOutput> fromNull =
            RLM_AI_ProductAttributeSaveService.saveAttributeSelections(null);
        List<RLM_AI_ProductAttributeSaveService.SaveOutput> fromEmpty =
            RLM_AI_ProductAttributeSaveService.saveAttributeSelections(
                new List<RLM_AI_ProductAttributeSaveService.SaveInput>()
            );
        Test.stopTest();

        Assert.areEqual(0, fromNull.size(), 'A null input list returns no results.');
        Assert.areEqual(0, fromEmpty.size(), 'An empty input list returns no results.');
    }

    @isTest
    static void saveGuidesUserWhenInputIsNull() {
        Test.startTest();
        List<RLM_AI_ProductAttributeSaveService.SaveOutput> results =
            RLM_AI_ProductAttributeSaveService.saveAttributeSelections(
                new List<RLM_AI_ProductAttributeSaveService.SaveInput>{ null }
            );
        Test.stopTest();

        Assert.areEqual(1, results.size(), 'A null entry still yields one result.');
        Assert.isFalse(results[0].isSuccess);
        Assert.isFalse(results[0].isValid);
        Assert.areEqual('[]', results[0].validationErrorsJson);
        Assert.areEqual(
            'Select a quote and quote line item before saving product configuration.',
            results[0].errorMessage
        );
    }

    @isTest
    static void saveGuidesUserWhenQuoteIdIsNotAQuote() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('RLM Save Wrong Quote Type');
        Account notAQuote = [SELECT Id FROM Account LIMIT 1];

        RLM_AI_ProductAttributeSaveService.SaveInput input =
            new RLM_AI_ProductAttributeSaveService.SaveInput();
        input.quoteId = String.valueOf(notAQuote.Id);
        input.quoteLineItemId = String.valueOf(fixture.quoteLineItemId);
        input.attributeSelectionsJson = '{}';

        Test.startTest();
        RLM_AI_ProductAttributeSaveService.SaveOutput out = saveOne(input);
        Test.stopTest();

        Assert.isFalse(out.isSuccess, 'A valid Id of another object is not a quote.');
        Assert.isFalse(out.isValid);
        Assert.areEqual('Select a valid quote before saving product configuration.', out.errorMessage);
    }

    @isTest
    static void saveGuidesUserWhenQuoteLineIdIsInvalid() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('RLM Save Bad Line Id');

        RLM_AI_ProductAttributeSaveService.SaveInput malformed =
            new RLM_AI_ProductAttributeSaveService.SaveInput();
        malformed.quoteId = String.valueOf(fixture.quoteId);
        malformed.quoteLineItemId = 'not-a-quote-line-id';
        malformed.attributeSelectionsJson = '{}';

        // A well-formed Id of the wrong object (the quote itself) is also rejected.
        RLM_AI_ProductAttributeSaveService.SaveInput wrongObject =
            new RLM_AI_ProductAttributeSaveService.SaveInput();
        wrongObject.quoteId = String.valueOf(fixture.quoteId);
        wrongObject.quoteLineItemId = String.valueOf(fixture.quoteId);
        wrongObject.attributeSelectionsJson = '{}';

        Test.startTest();
        List<RLM_AI_ProductAttributeSaveService.SaveOutput> results =
            RLM_AI_ProductAttributeSaveService.saveAttributeSelections(
                new List<RLM_AI_ProductAttributeSaveService.SaveInput>{ malformed, wrongObject }
            );
        Test.stopTest();

        Assert.areEqual(2, results.size(), 'One result per input, in order.');
        for (RLM_AI_ProductAttributeSaveService.SaveOutput out : results) {
            Assert.isFalse(out.isSuccess);
            Assert.isFalse(out.isValid);
            Assert.areEqual(
                'Select a valid quote line item before saving product configuration.',
                out.errorMessage
            );
        }
    }

    private static RLM_AI_ProductAttributeSaveService.SaveOutput saveOne(
            RLM_AI_ProductAttributeSaveService.SaveInput input) {
        List<RLM_AI_ProductAttributeSaveService.SaveOutput> results =
            RLM_AI_ProductAttributeSaveService.saveAttributeSelections(
                new List<RLM_AI_ProductAttributeSaveService.SaveInput>{ input }
            );
        Assert.areEqual(1, results.size(), 'One input yields one result.');
        return results[0];
    }
}
