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
    // QuoteLineItemAttribute is an async-creatable entity: Database.insertImmediate()
    // commits it in a SEPARATE transaction, so a record created in a test cannot be
    // queried back within the same test transaction (a direct SOQL returns 0). The
    // "found" branch is therefore exercised through the @TestVisible summarizeAttributes
    // seam with in-memory rows — the picklist enrichment SOQL still runs against real,
    // queryable AttributePicklistValue records.
    @isTest
    static void returnsExistingAttributeWithValueAndOptions() {
        // A picklist attribute definition with a few valid values. The platform
        // requires the whole chain to be ACTIVE: the picklist (Status=Active), its
        // values (Status=Active, one IsDefault), and the definition (IsActive=true
        // with a unique Name/Code). Codes are globally unique, so salt them per run.
        String sfx = String.valueOf(System.now().getTime());
        AttributePicklist pl = new AttributePicklist(
            Name = 'RLM Test Type Picklist ' + sfx,
            Status = 'Active'
        );
        insert pl;
        AttributePicklistValue pvFlex = new AttributePicklistValue(
            Name = 'Flex', Code = 'Flex' + sfx, Value = 'Flex',
            PicklistId = pl.Id, Status = 'Active', IsDefault = true
        );
        AttributePicklistValue pvProd = new AttributePicklistValue(
            Name = 'Prod', Code = 'Prod' + sfx, Value = 'Prod',
            PicklistId = pl.Id, Status = 'Active'
        );
        insert new List<AttributePicklistValue>{ pvFlex, pvProd };
        AttributeDefinition ad = new AttributeDefinition(
            Name = 'RLM Test Type ' + sfx,
            Label = 'RLM Test Type',
            DeveloperName = 'RLM_Test_Type_' + sfx,
            Code = 'RLM_Test_Type_Code_' + sfx,
            DataType = 'Picklist',
            PicklistId = pl.Id,
            IsActive = true
        );
        insert ad;

        // The attribute as materialized on the line, currently set to "Prod".
        // Built in memory (not inserted) with its parent AttributeDefinition
        // populated so summarizeAttributes can read DataType/PicklistId.
        QuoteLineItemAttribute lineAttr = new QuoteLineItemAttribute(
            AttributeDefinitionId = ad.Id,
            AttributeValue = 'Prod'
        );
        lineAttr = (QuoteLineItemAttribute) attachParent(lineAttr, ad);

        RLM_AI_QuoteLineAttributeService.GetLineAttributesOutput out =
            new RLM_AI_QuoteLineAttributeService.GetLineAttributesOutput();
        out.isSuccess = true;
        out.productName = 'RLM Attr Value Product';

        Test.startTest();
        RLM_AI_QuoteLineAttributeService.summarizeAttributes(
            out,
            new List<QuoteLineItemAttribute>{ lineAttr }
        );
        Test.stopTest();

        System.assertEquals(true, out.hasAttributes, 'Line has one materialized attribute.');
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

    // Populates the read-only AttributeDefinition relationship on an in-memory
    // QuoteLineItemAttribute by round-tripping through JSON — the only way to set
    // a parent-relationship field that isn't writeable via the constructor.
    private static SObject attachParent(QuoteLineItemAttribute qlia, AttributeDefinition ad) {
        Map<String, Object> qliaMap =
            (Map<String, Object>) JSON.deserializeUntyped(JSON.serialize(qlia));
        // AttributeName / IsPriceImpacting are read-only via the constructor, so
        // inject them through the JSON layer alongside the parent relationship.
        qliaMap.put('AttributeName', 'RLM Test Type');
        qliaMap.put('IsPriceImpacting', true);
        qliaMap.put('AttributeDefinition', new Map<String, Object>{
            'Name'          => ad.Name,
            'DeveloperName' => ad.DeveloperName,
            'DataType'      => ad.DataType,
            'PicklistId'    => ad.PicklistId
        });
        return (SObject) JSON.deserialize(
            JSON.serialize(qliaMap), QuoteLineItemAttribute.class
        );
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
