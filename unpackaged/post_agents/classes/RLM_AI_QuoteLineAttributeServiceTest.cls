@isTest
private class RLM_AI_QuoteLineAttributeServiceTest {

    // A quote line with no materialized attributes returns hasAttributes=false
    // and a friendly "no attributes set" summary (not an error).
    @isTest
    static void returnsEmptyWhenLineHasNoAttributes() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('RLM Line Attr Product');

        RLM_AI_QuoteLineAttributeService.GetLineAttributesInput input =
            new RLM_AI_QuoteLineAttributeService.GetLineAttributesInput();
        input.quoteLineItemId = String.valueOf(fixture.quoteLineItemId);

        Test.startTest();
        List<RLM_AI_QuoteLineAttributeService.GetLineAttributesOutput> results =
            RLM_AI_QuoteLineAttributeService.getQuoteLineAttributes(
                new List<RLM_AI_QuoteLineAttributeService.GetLineAttributesInput>{ input }
            );
        Test.stopTest();

        System.assertEquals(1, results.size(), 'One result should be returned.');
        RLM_AI_QuoteLineAttributeService.GetLineAttributesOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'Read should run without a system error.');
        System.assertEquals(false, out.hasAttributes, 'No attributes are set on the line.');
        System.assertEquals('[]', out.attributesJson, 'Attributes JSON should be empty.');
        System.assertEquals(null, out.errorMessage);
        System.assert(out.attributeSummary.contains('no attributes set'),
            'Summary should state the line has no attributes set.');
    }

    // Main path: a line with a materialized picklist attribute returns the
    // current value AND the valid picklist options, both in JSON and summary.
    //
    // The "found" branch is exercised through the @TestVisible summarize seam
    // with in-memory ResolvedAttribute rows (the merged shape the resolver
    // returns), so the test does not depend on inserting-and-querying the
    // async-creatable QuoteLineItemAttribute within one transaction.
    @isTest
    static void returnsExistingAttributeWithValueAndOptions() {
        RLM_AI_AttributeResolver.ResolvedAttribute ra =
            new RLM_AI_AttributeResolver.ResolvedAttribute();
        ra.name = 'Type';
        ra.developerName = 'Type';
        ra.dataType = 'Picklist';
        ra.isRequired = false;
        ra.isPriceImpacting = true;
        ra.currentValue = 'Prod';
        ra.picklistValues = new List<String>{ 'Flex', 'Gov', 'Pre-Prod', 'Prod' };
        ra.isOnClassification = true;
        ra.isOnLine = true;

        RLM_AI_QuoteLineAttributeService.GetLineAttributesOutput out =
            new RLM_AI_QuoteLineAttributeService.GetLineAttributesOutput();
        out.isSuccess = true;
        out.productName = 'RLM Attr Value Product';

        Test.startTest();
        RLM_AI_QuoteLineAttributeService.summarize(
            out,
            new List<RLM_AI_AttributeResolver.ResolvedAttribute>{ ra }
        );
        Test.stopTest();

        System.assertEquals(true, out.hasAttributes, 'Line has a value set on one attribute.');
        // Current value present.
        System.assert(out.attributeSummary.contains('Prod'),
            'Summary should show the current value. Got: ' + out.attributeSummary);
        // Valid options enriched from the picklist.
        System.assert(out.attributeSummary.contains('Flex'),
            'Summary should list valid picklist options. Got: ' + out.attributeSummary);
        System.assert(out.attributesJson.contains('currentValue'),
            'JSON should carry the current value.');
        System.assert(out.attributesJson.contains('picklistValues'),
            'JSON should carry the valid picklist values.');
    }

    // A configurable attribute that is NOT yet set on the line: hasAttributes is
    // false (no value set), but the summary names it as configurable rather than
    // claiming the line has no attributes — the framing that prevents the
    // "no configurable attributes" false negative.
    @isTest
    static void configurableButUnsetAttributeIsNotReportedAsAbsent() {
        RLM_AI_AttributeResolver.ResolvedAttribute ra =
            new RLM_AI_AttributeResolver.ResolvedAttribute();
        ra.name = 'Type';
        ra.developerName = 'Type';
        ra.dataType = 'Picklist';
        ra.isRequired = false;
        ra.isPriceImpacting = true;
        ra.currentValue = null; // configurable but unset
        ra.picklistValues = new List<String>{ 'Flex', 'Prod' };
        ra.isOnClassification = true;
        ra.isOnLine = false;

        RLM_AI_QuoteLineAttributeService.GetLineAttributesOutput out =
            new RLM_AI_QuoteLineAttributeService.GetLineAttributesOutput();
        out.isSuccess = true;
        out.productName = 'RLM Unset Attr Product';

        RLM_AI_QuoteLineAttributeService.summarize(
            out,
            new List<RLM_AI_AttributeResolver.ResolvedAttribute>{ ra }
        );

        System.assertEquals(false, out.hasAttributes, 'No value is set yet.');
        System.assert(out.attributeSummary.contains('Type'),
            'Summary should still name the configurable attribute. Got: ' + out.attributeSummary);
        System.assert(!out.attributeSummary.contains('no attributes'),
            'Must not claim the line has no attributes. Got: ' + out.attributeSummary);
    }

    @isTest
    static void rejectsBlankQuoteLineItemId() {
        RLM_AI_QuoteLineAttributeService.GetLineAttributesInput input =
            new RLM_AI_QuoteLineAttributeService.GetLineAttributesInput();
        input.quoteLineItemId = '   ';

        List<RLM_AI_QuoteLineAttributeService.GetLineAttributesOutput> results =
            RLM_AI_QuoteLineAttributeService.getQuoteLineAttributes(
                new List<RLM_AI_QuoteLineAttributeService.GetLineAttributesInput>{ input }
            );

        System.assertEquals(1, results.size());
        System.assertEquals(false, results[0].isSuccess);
        System.assertEquals(false, results[0].hasAttributes);
        System.assertEquals('[]', results[0].attributesJson);
        System.assert(results[0].errorMessage.contains('valid quote line item'),
            'Blank id should be rejected with a clear message.');
    }

    // A well-formed id with the wrong prefix (a Quote id) must be rejected — the
    // service requires a QuoteLineItem (0QL) id, not a Quote (0Q0) id.
    @isTest
    static void rejectsNonQuoteLineItemId() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('RLM Wrong Prefix Product');

        RLM_AI_QuoteLineAttributeService.GetLineAttributesInput input =
            new RLM_AI_QuoteLineAttributeService.GetLineAttributesInput();
        input.quoteLineItemId = String.valueOf(fixture.quoteId); // 0Q0..., not 0QL...

        List<RLM_AI_QuoteLineAttributeService.GetLineAttributesOutput> results =
            RLM_AI_QuoteLineAttributeService.getQuoteLineAttributes(
                new List<RLM_AI_QuoteLineAttributeService.GetLineAttributesInput>{ input }
            );

        System.assertEquals(false, results[0].isSuccess,
            'A Quote id is not a valid QuoteLineItem id.');
        System.assertEquals(false, results[0].hasAttributes);
    }

    @isTest
    static void emptyInputListReturnsEmptyResults() {
        List<RLM_AI_QuoteLineAttributeService.GetLineAttributesOutput> results =
            RLM_AI_QuoteLineAttributeService.getQuoteLineAttributes(
                new List<RLM_AI_QuoteLineAttributeService.GetLineAttributesInput>()
            );
        System.assertEquals(0, results.size(), 'Empty input yields empty output.');
    }

    @isTest
    static void nullInputListReturnsEmptyResults() {
        List<RLM_AI_QuoteLineAttributeService.GetLineAttributesOutput> results =
            RLM_AI_QuoteLineAttributeService.getQuoteLineAttributes(null);
        System.assertEquals(0, results.size(), 'Null input yields empty output.');
    }
}
