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

        String serialized = RLM_AI_AttributeResolver.toJson(
            new List<RLM_AI_AttributeResolver.ResolvedAttribute>{ picklist, numeric }
        );

        List<Object> entries = (List<Object>) JSON.deserializeUntyped(serialized);
        Assert.areEqual(2, entries.size(), 'One entry per attribute, in order.');
        Map<String, Object> picklistEntry = (Map<String, Object>) entries[0];
        Map<String, Object> numericEntry = (Map<String, Object>) entries[1];
        Assert.areEqual('Flex', picklistEntry.get('currentValue'), 'Picklist current value present.');
        Assert.areEqual(new List<Object>{ 'Flex', 'Prod' }, picklistEntry.get('picklistValues'),
            'Picklist entry carries its valid values.');
        Assert.isTrue(numericEntry.containsKey('currentValue'),
            'Every entry carries currentValue, even when unset.');
        Assert.isNull(numericEntry.get('currentValue'), 'An unset value serializes as null.');
        Assert.isFalse(numericEntry.containsKey('picklistValues'),
            'Only picklist entries carry picklistValues.');
    }

    @isTest
    static void toJsonHandlesNull() {
        System.assertEquals('[]', RLM_AI_AttributeResolver.toJson(null),
            'Null attribute list serializes to an empty array.');
    }

    // The Id of a quote line that no longer exists resolves to lineFound=false.
    @isTest
    static void deletedLineIdReturnsNotFound() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('RLM Resolver Deleted Line');
        Id missingLineId = fixture.quoteLineItemId;
        Assert.isTrue(RLM_AI_AttributeResolver.resolve(missingLineId).lineFound,
            'PRECONDITION: the line resolves while it exists.');
        delete new QuoteLineItem(Id = missingLineId);

        Test.startTest();
        RLM_AI_AttributeResolver.Resolution res = RLM_AI_AttributeResolver.resolve(missingLineId);
        Test.stopTest();

        Assert.isFalse(res.lineFound, 'No quote line has this Id.');
        Assert.isNull(res.productId, 'No product without a line.');
        Assert.isFalse(res.hasAttributes(), 'No attributes without a line.');
    }

    // The definable set comes from the product's classification: hidden and
    // read-only attributes are dropped, the rest sorted by name, each carrying
    // its definition metadata, picklist values (sorted by name) and no current
    // value.
    @isTest
    static void classifiedLineReturnsDefinableAttributesInNameOrder() {
        Definitions defs = createDefinitions();
        Id classificationId = createClassification(defs);
        Id lineId = createLine('RLM Resolver Classified', classificationId);
        Assert.areEqual(2, [
            SELECT COUNT() FROM ProductClassificationAttr
            WHERE ProductClassificationId = :classificationId
              AND Status = 'Active'
              AND (IsHidden = true OR IsReadOnly = true)
        ], 'PRECONDITION: one hidden and one read-only Active attribute are on the classification, '
            + 'so only those flags can exclude them.');
        Assert.isFalse(
            [SELECT IsRequired FROM AttributeDefinition WHERE Id = :defs.tier.Id].IsRequired,
            'PRECONDITION: the tier definition itself is not required.');

        Test.startTest();
        RLM_AI_AttributeResolver.Resolution res = RLM_AI_AttributeResolver.resolve(lineId);
        Test.stopTest();

        Assert.isTrue(res.lineFound, 'Line should be found.');
        Assert.areEqual(
            [SELECT Product2Id FROM QuoteLineItem WHERE Id = :lineId].Product2Id,
            res.productId,
            'The line product is reported.');
        Assert.areEqual('RLM Resolver Classified', res.productName);
        Assert.isTrue(res.hasAttributes(), 'A classified product is configurable.');
        Assert.areEqual(2, res.attributes.size(),
            'Hidden and read-only classification attributes are excluded.');

        RLM_AI_AttributeResolver.ResolvedAttribute capacity = res.attributes[0];
        Assert.areEqual(CAPACITY_DEV_NAME, capacity.developerName, 'Capacity sorts before Tier.');
        Assert.areEqual(defs.capacity.Id, capacity.attributeDefinitionId);
        Assert.areEqual('RLMTest Res Capacity', capacity.name);
        Assert.areEqual('Number', capacity.dataType);
        Assert.isFalse(capacity.isRequired);
        Assert.isFalse(capacity.isPriceImpacting);
        Assert.isTrue(capacity.picklistValues.isEmpty(), 'A Number attribute has no picklist values.');
        Assert.isTrue(capacity.isOnClassification);
        Assert.isFalse(capacity.isOnLine, 'Nothing is materialized on the line yet.');
        Assert.isNull(capacity.currentValue);

        RLM_AI_AttributeResolver.ResolvedAttribute tier = res.attributes[1];
        Assert.areEqual(TIER_DEV_NAME, tier.developerName);
        Assert.areEqual(defs.tier.Id, tier.attributeDefinitionId);
        Assert.areEqual('Picklist', tier.dataType);
        Assert.isTrue(tier.isRequired,
            'Required comes from the classification attribute, not the definition.');
        Assert.isTrue(tier.isPriceImpacting, 'Price impact comes from the classification attribute.');
        Assert.areEqual(new List<String>{ 'Premium', 'Standard' }, tier.picklistValues,
            'Picklist values are listed by name, in name order.');
        Assert.isTrue(tier.isOnClassification);
        Assert.isFalse(tier.isOnLine);
        Assert.isNull(tier.currentValue);

        String json = RLM_AI_AttributeResolver.toJson(res.attributes);
        Assert.isTrue(json.contains(TIER_DEV_NAME) && json.contains(CAPACITY_DEV_NAME),
            'Both resolved attributes serialize: ' + json);
        Assert.isTrue(json.contains('"Premium"'), 'Picklist values serialize: ' + json);
    }

    // ── Fixture ──────────────────────────────────────────────────────────────

    private static final String TIER_DEV_NAME = 'RLMTest_Res_Tier';
    private static final String CAPACITY_DEV_NAME = 'RLMTest_Res_Capacity';

    private class Definitions {
        public AttributeDefinition tier;      // Picklist: Standard, Premium
        public AttributeDefinition capacity;  // Number
        public AttributeDefinition hidden;    // Text, hidden on the classification
        public AttributeDefinition readOnly;  // Text, read-only on the classification
    }

    private static Definitions createDefinitions() {
        AttributePicklist tierPicklist = new AttributePicklist(
            Name = 'RLMTest Res Tier Picklist',
            DataType = 'Text',
            Status = 'Active'
        );
        insert tierPicklist;
        insert new List<AttributePicklistValue>{
            new AttributePicklistValue(
                PicklistId = tierPicklist.Id,
                Name = 'Standard',
                Value = 'Standard',
                Code = 'RLMTEST_RES_STD',
                Status = 'Active'
            ),
            new AttributePicklistValue(
                PicklistId = tierPicklist.Id,
                Name = 'Premium',
                Value = 'PREM',
                Code = 'RLMTEST_RES_PREM',
                Status = 'Active'
            )
        };

        Definitions defs = new Definitions();
        defs.tier = definition('RLMTest Res Tier', TIER_DEV_NAME, 'Picklist', tierPicklist.Id);
        defs.capacity = definition('RLMTest Res Capacity', CAPACITY_DEV_NAME, 'Number', null);
        defs.hidden = definition('RLMTest Res Hidden', 'RLMTest_Res_Hidden', 'Text', null);
        defs.readOnly = definition('RLMTest Res Read Only', 'RLMTest_Res_Read_Only', 'Text', null);
        insert new List<AttributeDefinition>{ defs.tier, defs.capacity, defs.hidden, defs.readOnly };
        return defs;
    }

    private static AttributeDefinition definition(
            String name, String developerName, String dataType, Id picklistId) {
        return new AttributeDefinition(
            Name = name,
            Label = name,
            DeveloperName = developerName,
            Code = developerName.toUpperCase(),
            DataType = dataType,
            PicklistId = picklistId,
            IsActive = true
        );
    }

    // An Active classification exposing tier (price-impacting and required) and
    // capacity, plus one hidden and one read-only attribute the resolver
    // excludes. A visible read-only attribute needs a default value.
    private static Id createClassification(Definitions defs) {
        ProductClassification classification = new ProductClassification(
            Name = 'RLMTest Res Classification',
            Code = 'RLMTEST_RES_PC',
            Status = 'Active'
        );
        insert classification;
        List<ProductClassificationAttr> attrs = new List<ProductClassificationAttr>{
            classificationAttr(classification.Id, defs.tier, true, false, false),
            classificationAttr(classification.Id, defs.capacity, false, false, false),
            classificationAttr(classification.Id, defs.hidden, false, true, false),
            classificationAttr(classification.Id, defs.readOnly, false, false, true)
        };
        insert attrs;
        // On insert the platform copies IsRequired from the definition; an
        // update sets it on the classification attribute alone.
        update new ProductClassificationAttr(Id = attrs[0].Id, IsRequired = true);
        return classification.Id;
    }

    private static ProductClassificationAttr classificationAttr(
            Id classificationId, AttributeDefinition def,
            Boolean isPriceImpacting, Boolean isHidden, Boolean isReadOnly) {
        return new ProductClassificationAttr(
            Name = def.Name,
            ProductClassificationId = classificationId,
            AttributeDefinitionId = def.Id,
            Status = 'Active',
            IsPriceImpacting = isPriceImpacting,
            IsHidden = isHidden,
            IsReadOnly = isReadOnly,
            DefaultValue = isReadOnly ? 'Fixed' : null
        );
    }

    // A quote line (from the shared fixture) whose product is then based on the
    // given classification.
    private static Id createLine(String productName, Id classificationId) {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture(productName);
        Id productId = [
            SELECT Product2Id FROM QuoteLineItem WHERE Id = :fixture.quoteLineItemId
        ].Product2Id;
        update new Product2(Id = productId, BasedOnId = classificationId);
        return fixture.quoteLineItemId;
    }

}
