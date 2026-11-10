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
        System.assertEquals(true, results[0].isSuccess, 'Lookup ran correctly even with no configurable attributes.');
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
        System.assertEquals(false, results[0].isSuccess);
        System.assertEquals('Select a valid quote line item before looking up configurable attributes.', results[0].errorMessage);
    }

    @isTest
    static void returnsNoResultsForNullOrEmptyInput() {
        Test.startTest();
        List<RLM_AI_ProductAttributeService.GetAttributeOptionsOutput> fromNull =
            RLM_AI_ProductAttributeService.getProductAttributeOptions(null);
        List<RLM_AI_ProductAttributeService.GetAttributeOptionsOutput> fromEmpty =
            RLM_AI_ProductAttributeService.getProductAttributeOptions(
                new List<RLM_AI_ProductAttributeService.GetAttributeOptionsInput>()
            );
        Test.stopTest();

        Assert.areEqual(0, fromNull.size(), 'A null input list returns no results.');
        Assert.areEqual(0, fromEmpty.size(), 'An empty input list returns no results.');
    }

    @isTest
    static void guidesUserWhenInputIsNull() {
        Test.startTest();
        List<RLM_AI_ProductAttributeService.GetAttributeOptionsOutput> results =
            RLM_AI_ProductAttributeService.getProductAttributeOptions(
                new List<RLM_AI_ProductAttributeService.GetAttributeOptionsInput>{ null }
            );
        Test.stopTest();

        Assert.areEqual(1, results.size(), 'A null entry still yields one result.');
        Assert.isFalse(results[0].isSuccess);
        Assert.isFalse(results[0].hasConfigurableAttributes);
        Assert.areEqual('[]', results[0].attributesJson);
        Assert.areEqual(
            'Select a quote line item before looking up configurable attributes.',
            results[0].errorMessage
        );
    }

    // A well-formed quote line Id with no record behind it is reported as not
    // found (a domain result, so isSuccess stays true).
    @isTest
    static void reportsAQuoteLineThatDoesNotExist() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('RLM Deleted Line Product');
        Id deletedLineId = fixture.quoteLineItemId;
        delete new QuoteLineItem(Id = deletedLineId);

        RLM_AI_ProductAttributeService.GetAttributeOptionsInput input =
            new RLM_AI_ProductAttributeService.GetAttributeOptionsInput();
        input.quoteLineItemId = String.valueOf(deletedLineId);

        Test.startTest();
        List<RLM_AI_ProductAttributeService.GetAttributeOptionsOutput> results =
            RLM_AI_ProductAttributeService.getProductAttributeOptions(
                new List<RLM_AI_ProductAttributeService.GetAttributeOptionsInput>{ input }
            );
        Test.stopTest();

        Assert.isTrue(results[0].isSuccess, 'A missing line is a domain result, not a system error.');
        Assert.areEqual('QuoteLineItem not found: ' + deletedLineId, results[0].errorMessage);
        Assert.isFalse(results[0].hasConfigurableAttributes);
        Assert.areEqual('[]', results[0].attributesJson);
        Assert.isNull(results[0].productName);
    }

    // A product based on a classification lists every definable attribute, in
    // name order, with the prompt for its data type, the required marker, and
    // the picklist options.
    @isTest
    static void summarizesEachAttributeTypeOnAClassifiedProduct() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('RLM Attr Summary Product');
        Id classificationId = createClassification();
        Id productId = [
            SELECT Product2Id FROM QuoteLineItem WHERE Id = :fixture.quoteLineItemId
        ].Product2Id;
        update new Product2(Id = productId, BasedOnId = classificationId);

        RLM_AI_ProductAttributeService.GetAttributeOptionsInput input =
            new RLM_AI_ProductAttributeService.GetAttributeOptionsInput();
        input.quoteLineItemId = String.valueOf(fixture.quoteLineItemId);

        Test.startTest();
        List<RLM_AI_ProductAttributeService.GetAttributeOptionsOutput> results =
            RLM_AI_ProductAttributeService.getProductAttributeOptions(
                new List<RLM_AI_ProductAttributeService.GetAttributeOptionsInput>{ input }
            );
        Test.stopTest();

        RLM_AI_ProductAttributeService.GetAttributeOptionsOutput out = results[0];
        Assert.isTrue(out.isSuccess, 'Lookup ran without a system error: ' + out.errorMessage);
        Assert.isNull(out.errorMessage);
        Assert.isTrue(out.hasConfigurableAttributes, 'A classified product is configurable.');
        Assert.areEqual('RLM Attr Summary Product', out.productName);

        String expectedSummary = String.join(new List<String>{
            'Here are the configurable attributes for RLM Attr Summary Product:',
            '',
            '1. RLMTest Attr Capacity — enter a number',
            '2. RLMTest Attr Enabled — yes or no',
            '3. RLMTest Attr Notes — enter a value',
            '4. RLMTest Attr Tier (required)',
            '   Options: Premium, Standard',
            '',
            'Please provide a value for each attribute you want to configure.'
        }, '\n');
        Assert.areEqual(expectedSummary, out.attributeSummary);

        List<Object> attributes = (List<Object>) JSON.deserializeUntyped(out.attributesJson);
        Assert.areEqual(4, attributes.size(), 'One JSON entry per definable attribute.');
        Map<String, Object> tier = (Map<String, Object>) attributes[3];
        Assert.areEqual('RLMTest_Attr_Tier', tier.get('developerName'));
        Assert.areEqual(true, tier.get('isRequired'));
        Assert.areEqual(new List<Object>{ 'Premium', 'Standard' }, tier.get('picklistValues'));
    }

    // One attribute of each data type the summary formats differently. The tier
    // is required through its definition: the platform copies IsRequired from
    // the definition onto each new ProductClassificationAttr.
    private static Id createClassification() {
        AttributePicklist tierPicklist = new AttributePicklist(
            Name = 'RLMTest Attr Tier Picklist',
            DataType = 'Text',
            Status = 'Active'
        );
        insert tierPicklist;
        insert new List<AttributePicklistValue>{
            new AttributePicklistValue(PicklistId = tierPicklist.Id, Name = 'Standard',
                Value = 'Standard', Code = 'RLMTEST_ATTR_STD', Status = 'Active'),
            new AttributePicklistValue(PicklistId = tierPicklist.Id, Name = 'Premium',
                Value = 'PREM', Code = 'RLMTEST_ATTR_PREM', Status = 'Active')
        };

        List<AttributeDefinition> defs = new List<AttributeDefinition>{
            definition('RLMTest Attr Capacity', 'RLMTest_Attr_Capacity', 'Number', null, false),
            definition('RLMTest Attr Enabled', 'RLMTest_Attr_Enabled', 'Checkbox', null, false),
            definition('RLMTest Attr Notes', 'RLMTest_Attr_Notes', 'Text', null, false),
            definition('RLMTest Attr Tier', 'RLMTest_Attr_Tier', 'Picklist', tierPicklist.Id, true)
        };
        insert defs;

        ProductClassification classification = new ProductClassification(
            Name = 'RLMTest Attr Classification',
            Code = 'RLMTEST_ATTR_PC',
            Status = 'Active'
        );
        insert classification;
        List<ProductClassificationAttr> attrs = new List<ProductClassificationAttr>();
        for (AttributeDefinition def : defs) {
            attrs.add(new ProductClassificationAttr(
                Name = def.Name,
                ProductClassificationId = classification.Id,
                AttributeDefinitionId = def.Id,
                Status = 'Active'
            ));
        }
        insert attrs;
        return classification.Id;
    }

    private static AttributeDefinition definition(
            String name, String developerName, String dataType, Id picklistId, Boolean isRequired) {
        return new AttributeDefinition(
            Name = name,
            Label = name,
            DeveloperName = developerName,
            Code = developerName.toUpperCase(),
            DataType = dataType,
            PicklistId = picklistId,
            IsRequired = isRequired,
            IsActive = true
        );
    }
}
