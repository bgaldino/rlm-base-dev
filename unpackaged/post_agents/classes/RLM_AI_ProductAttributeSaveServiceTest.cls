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

    // ── The Place Sales Transaction path ────────────────────────────────────
    //
    // The PST path (and the post-save readback) needs QuoteLineItemAttribute
    // rows on the line. An Apex test cannot create them: ordinary DML is
    // refused ("use insertAsync() or insertImmediate()"), insertAsync is
    // refused for this object, and insertImmediate reports success but the row
    // is never queryable. So, past the input guards, saveAttributeSelections
    // only reaches the no-matching-attributes branch above, and what the
    // service does with the rows is tested through the seams that take them
    // (after "Seams over queried rows"), with rows built by JSON.deserialize
    // and fake ids.
    //
    // executePst is called directly: PST runs in a test and refuses a patch of
    // a row that does not exist, so its failure path runs against the
    // platform. Live-only: a successful PST call, the order of the two calls
    // in doSave (Number before Picklist, stopping at the first failure), the
    // picklist-value query (it runs only for Picklist rows with a picklist
    // id), and the readback query.

    // ── Input guards ─────────────────────────────────────────────────────────

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
    static void saveGuidesUserWhenAnInputEntryIsNull() {
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
        Account notAQuote = new Account(Name = 'RLM Save Not A Quote');
        insert notAQuote;

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

        Assert.areEqual(2, results.size(), 'One result per input.');
        for (RLM_AI_ProductAttributeSaveService.SaveOutput out : results) {
            Assert.isFalse(out.isSuccess);
            Assert.isFalse(out.isValid);
            Assert.areEqual(
                'Select a valid quote line item before saving product configuration.',
                out.errorMessage
            );
        }
    }

    // ── Seams over queried rows ─────────────────────────────────────────────

    @isTest
    static void indexAttributes_keysByDeveloperNameAndCollectsPicklistIds() {
        Id dutyPicklist = fakeId(AttributePicklist.SObjectType, 1);
        List<QuoteLineItemAttribute> rows = new List<QuoteLineItemAttribute>{
            attributeRow(1, 'requiredKW', 'Number', fakeId(AttributePicklist.SObjectType, 9), null),
            attributeRow(2, 'DutyRating', 'Picklist', dutyPicklist, null),
            attributeRow(3, 'Finish', 'Picklist', null, null),
            attributeRow(4, null, 'Text', null, null),
            (QuoteLineItemAttribute) JSON.deserialize(
                '{"attributes":{"type":"QuoteLineItemAttribute"},"Id":"'
                    + fakeId(QuoteLineItemAttribute.SObjectType, 5) + '"}',
                QuoteLineItemAttribute.class)
        };
        Map<String, QuoteLineItemAttribute> byDevName = new Map<String, QuoteLineItemAttribute>();
        Set<Id> picklistIds = new Set<Id>();

        RLM_AI_ProductAttributeSaveService.indexAttributes(rows, byDevName, picklistIds);

        Assert.areEqual(new Set<String>{ 'requiredKW', 'DutyRating', 'Finish' }, byDevName.keySet(),
            'Rows without a definition developer name are skipped');
        Assert.areEqual(rows[1].Id, byDevName.get('DutyRating').Id, 'Each name maps to its row');
        Assert.areEqual(new Set<Id>{ dutyPicklist }, picklistIds,
            'Only a Picklist attribute with a picklist id contributes one; a Number row\'s picklist id is ignored');
    }

    @isTest
    static void indexAttributes_aRepeatedNameKeepsTheLastRow() {
        List<QuoteLineItemAttribute> rows = new List<QuoteLineItemAttribute>{
            attributeRow(1, 'requiredKW', 'Number', null, null),
            attributeRow(2, 'requiredKW', 'Number', null, null)
        };
        Map<String, QuoteLineItemAttribute> byDevName = new Map<String, QuoteLineItemAttribute>();

        RLM_AI_ProductAttributeSaveService.indexAttributes(rows, byDevName, new Set<Id>());

        Assert.areEqual(rows[1].Id, byDevName.get('requiredKW').Id, 'The later row replaces the earlier one');
    }

    @isTest
    static void picklistValueIds_mapsValueNameAndCodePerPicklist() {
        Id duty = fakeId(AttributePicklist.SObjectType, 1);
        Id finish = fakeId(AttributePicklist.SObjectType, 2);
        AttributePicklistValue continuous = picklistValueRow(1, duty, 'DCC', 'Duty Continuous', 'DC');
        AttributePicklistValue standby = picklistValueRow(2, duty, 'STB', 'Stb', null);
        AttributePicklistValue matte = picklistValueRow(3, finish, 'Matte', null, 'MT');

        Map<Id, Map<String, Id>> result = RLM_AI_ProductAttributeSaveService.picklistValueIds(
            new List<AttributePicklistValue>{ continuous, standby, matte });

        Assert.areEqual(new Set<Id>{ duty, finish }, result.keySet(), 'One map per picklist');
        Assert.areEqual(new Map<String, Id>{
                'DCC' => continuous.Id, 'Duty Continuous' => continuous.Id, 'DC' => continuous.Id,
                'STB' => standby.Id
            }, result.get(duty), 'A value is found by its Value, Name and Code; a Name equal to the Value, ignoring case, adds nothing');
        Assert.areEqual(new Map<String, Id>{ 'Matte' => matte.Id, 'MT' => matte.Id }, result.get(finish),
            'A blank Name adds nothing');
    }

    @isTest
    static void picklistValueIds_valueWinsOverAnEarlierNameOrCode() {
        Id duty = fakeId(AttributePicklist.SObjectType, 1);
        AttributePicklistValue first = picklistValueRow(1, duty, 'DCC', 'Prime', 'PRP');
        AttributePicklistValue second = picklistValueRow(2, duty, 'Prime', 'DCC', 'DCC');

        Map<String, Id> result = RLM_AI_ProductAttributeSaveService.picklistValueIds(
            new List<AttributePicklistValue>{ first, second }).get(duty);

        Assert.areEqual(second.Id, result.get('Prime'), 'A later Value replaces an earlier Name');
        Assert.areEqual(first.Id, result.get('DCC'), 'A later Name or Code does not replace an earlier Value');
        Assert.areEqual(first.Id, result.get('PRP'), 'An unclaimed Code still maps to its value');
    }

    @isTest
    static void splitSelections_groupsPicklistsApartFromEveryOtherType() {
        Map<String, QuoteLineItemAttribute> byDevName = new Map<String, QuoteLineItemAttribute>{
            'requiredKW' => attributeRow(1, 'requiredKW', 'Number', null, null),
            'DutyRating' => attributeRow(2, 'DutyRating', 'Picklist', fakeId(AttributePicklist.SObjectType, 1), null),
            'SiteName' => attributeRow(3, 'SiteName', 'Text', null, null)
        };
        Map<String, Object> selections = new Map<String, Object>{
            'requiredKW' => 1500, 'DutyRating' => 'DCC', 'SiteName' => 'North', 'Unknown' => 'x'
        };
        Map<String, Object> numbers = new Map<String, Object>();
        Map<String, Object> picklists = new Map<String, Object>();

        RLM_AI_ProductAttributeSaveService.splitSelections(selections, byDevName, numbers, picklists);

        Assert.areEqual(new Map<String, Object>{ 'requiredKW' => 1500, 'SiteName' => 'North' }, numbers,
            'Every non-Picklist type is sent with the Number call');
        Assert.areEqual(new Map<String, Object>{ 'DutyRating' => 'DCC' }, picklists,
            'Picklist selections are sent in their own call');
    }

    @isTest
    static void pstGraphNodes_patchesTheQuoteThenEachSelectedAttribute() {
        Id quoteId = fakeId(Quote.SObjectType, 1);
        Id duty = fakeId(AttributePicklist.SObjectType, 1);
        AttributePicklistValue dcc = picklistValueRow(1, duty, 'DCC', null, null);
        QuoteLineItemAttribute kw = attributeRow(1, 'requiredKW', 'Number', null, null);
        QuoteLineItemAttribute rating = attributeRow(2, 'DutyRating', 'Picklist', duty, null);
        QuoteLineItemAttribute note = attributeRow(3, 'Note', 'Text', null, null);
        Map<String, QuoteLineItemAttribute> byDevName = new Map<String, QuoteLineItemAttribute>{
            'requiredKW' => kw, 'DutyRating' => rating, 'Note' => note
        };
        Map<Id, Map<String, Id>> pvByPicklist = new Map<Id, Map<String, Id>>{
            duty => new Map<String, Id>{ 'DCC' => dcc.Id }
        };
        // 'Unknown' (no attribute on the line) sits between kept selections, so a number
        // spent on it would leave a gap in the reference ids.
        Map<String, Object> selections = new Map<String, Object>{
            'requiredKW' => 1500, 'Unknown' => 'x', 'DutyRating' => 'DCC', 'Note' => null
        };

        List<RevSalesTrxn.RecordWithReferenceRequest> nodes = RLM_AI_ProductAttributeSaveService.pstGraphNodes(
            String.valueOf(quoteId), selections, byDevName, pvByPicklist);

        Assert.areEqual(4, nodes.size(), 'The quote and the three attributes the line has; Unknown adds no node');
        Assert.areEqual('refQuote', nodes[0].referenceId, 'The quote node comes first');
        Assert.areEqual(String.valueOf(quoteId), String.valueOf(nodes[0].record.id));
        Assert.areEqual('PATCH', nodes[0].record.method);
        Map<Id, RevSalesTrxn.RecordWithReferenceRequest> byRecord = new Map<Id, RevSalesTrxn.RecordWithReferenceRequest>();
        Set<String> referenceIds = new Set<String>();
        for (Integer i = 1; i < nodes.size(); i++) {
            byRecord.put(nodes[i].record.id, nodes[i]);
            referenceIds.add(nodes[i].referenceId);
            Assert.areEqual('PATCH', nodes[i].record.method, 'Each attribute is patched');
        }
        Assert.areEqual(new Set<String>{ 'refQlia0', 'refQlia1', 'refQlia2' }, referenceIds,
            'Attribute nodes are numbered from 0 with no gap for the skipped selection');
        Assert.areEqual(new Map<String, Object>{ 'AttributeValue' => '1500' }, byRecord.get(kw.Id).record.fieldValues,
            'A number is sent as text');
        Assert.areEqual(new Map<String, Object>{ 'AttributeValue' => 'DCC', 'AttributePicklistValueId' => dcc.Id },
            byRecord.get(rating.Id).record.fieldValues, 'A known picklist value also sends its id');
        Assert.areEqual(new Map<String, Object>{ 'AttributeValue' => '' }, byRecord.get(note.Id).record.fieldValues,
            'A null selection is sent as an empty AttributeValue');
    }

    @isTest
    static void pstGraphNodes_anUnknownPicklistValueSendsOnlyTheText() {
        Id duty = fakeId(AttributePicklist.SObjectType, 1);
        Id finish = fakeId(AttributePicklist.SObjectType, 2);
        QuoteLineItemAttribute rating = attributeRow(1, 'DutyRating', 'Picklist', duty, null);
        QuoteLineItemAttribute surface = attributeRow(2, 'Finish', 'Picklist', finish, null);
        Map<Id, Map<String, Id>> pvByPicklist = new Map<Id, Map<String, Id>>{
            duty => new Map<String, Id>{ 'DCC' => fakeId(AttributePicklistValue.SObjectType, 1) }
        };

        List<RevSalesTrxn.RecordWithReferenceRequest> nodes = RLM_AI_ProductAttributeSaveService.pstGraphNodes(
            String.valueOf(fakeId(Quote.SObjectType, 1)),
            new Map<String, Object>{ 'DutyRating' => 'Standby', 'Finish' => 'Matte' },
            new Map<String, QuoteLineItemAttribute>{ 'DutyRating' => rating, 'Finish' => surface },
            pvByPicklist);

        Assert.areEqual(3, nodes.size());
        for (Integer i = 1; i < nodes.size(); i++) {
            Assert.areEqual(new Set<String>{ 'AttributeValue' }, nodes[i].record.fieldValues.keySet(),
                'A value missing from its picklist, or a picklist with no values loaded, sends no value id');
        }
    }

    // PST runs in an Apex test: for an attribute row that does not exist it returns a
    // failure response (measured 2026-11-25: UNKNOWN_EXCEPTION "Delta count 0 does not
    // match with input size 1") rather than throwing, so the call and its error handling
    // run here against the platform.
    @isTest
    static void executePst_returnsThePlatformRefusal() {
        RLM_AI_ProductConfigTestDataFactory.QuoteFixture fixture =
            RLM_AI_ProductConfigTestDataFactory.createQuoteFixture('RLM Save PST Refusal');
        Map<String, QuoteLineItemAttribute> byDevName = new Map<String, QuoteLineItemAttribute>{
            'requiredKW' => attributeRow(1, 'requiredKW', 'Number', null, null)
        };

        Test.startTest();
        RLM_AI_ProductAttributeSaveService.SaveOutput out = RLM_AI_ProductAttributeSaveService.executePst(
            String.valueOf(fixture.quoteId), String.valueOf(fixture.quoteLineItemId),
            new Map<String, Object>{ 'requiredKW' => 1500 }, byDevName, new Map<Id, Map<String, Id>>());
        Test.stopTest();

        Assert.isFalse(out.isSuccess, 'PST refuses a patch of an attribute row that does not exist');
        Assert.isFalse(out.isValid);
        Assert.isTrue(String.isNotBlank(out.errorMessage) && out.errorMessage.contains('"errorCode"'),
            'The refusal carries the platform error responses: ' + out.errorMessage);
    }

    @isTest
    static void executePst_withNoAttributeToPatchReturnsTheSelectionsUnsent() {
        Map<String, Object> selections = new Map<String, Object>{ 'Unknown' => 'x' };

        RLM_AI_ProductAttributeSaveService.SaveOutput out = RLM_AI_ProductAttributeSaveService.executePst(
            String.valueOf(fakeId(Quote.SObjectType, 1)), String.valueOf(fakeId(QuoteLineItem.SObjectType, 1)),
            selections, new Map<String, QuoteLineItemAttribute>(), new Map<Id, Map<String, Id>>());

        Assert.isTrue(out.isSuccess, 'Only the quote node: nothing to place, so no call and no error');
        Assert.isTrue(out.isValid);
        Assert.areEqual(JSON.serialize(selections), out.savedAttributesJson, 'The selections are echoed back');
        Assert.areEqual('[]', out.validationErrorsJson);
    }

    @isTest
    static void pstResult_successAndJoinedErrors() {
        RLM_AI_ProductAttributeSaveService.SaveOutput ok =
            RLM_AI_ProductAttributeSaveService.pstResult(true, new List<Object>());
        Assert.isTrue(ok.isSuccess);
        Assert.isTrue(ok.isValid);
        Assert.isNull(ok.errorMessage, 'A success carries no error');

        RLM_AI_ProductAttributeSaveService.SaveOutput failed = RLM_AI_ProductAttributeSaveService.pstResult(
            false, new List<Object>{
                new Map<String, Object>{ 'errorCode' => 'INVALID' },
                'second'
            });
        Assert.isFalse(failed.isSuccess);
        Assert.isFalse(failed.isValid);
        Assert.areEqual('{"errorCode":"INVALID"}; "second"', failed.errorMessage,
            'Each error response is serialized and joined with "; "');

        RLM_AI_ProductAttributeSaveService.SaveOutput bare =
            RLM_AI_ProductAttributeSaveService.pstResult(false, new List<Object>());
        Assert.isFalse(bare.isSuccess);
        Assert.areEqual('', bare.errorMessage, 'A failure with no error responses has an empty message');
    }

    @isTest
    static void valuesByDevName_readsBackEachValue() {
        Map<String, String> result = RLM_AI_ProductAttributeSaveService.valuesByDevName(
            new List<QuoteLineItemAttribute>{
                attributeRow(1, 'requiredKW', 'Number', null, '1500'),
                attributeRow(2, 'Note', 'Text', null, null)
            });

        Assert.areEqual(new Map<String, String>{ 'requiredKW' => '1500', 'Note' => null }, result,
            'Each row gives its stored value, null included');
    }

    // A queried-shape attribute row; Apex tests cannot insert QuoteLineItemAttribute.
    private static QuoteLineItemAttribute attributeRow(
            Integer n, String devName, String dataType, Id picklistId, String value) {
        Map<String, Object> definition = new Map<String, Object>{
            'attributes' => new Map<String, Object>{ 'type' => 'AttributeDefinition' },
            'DeveloperName' => devName,
            'DataType' => dataType,
            'PicklistId' => picklistId
        };
        Map<String, Object> row = new Map<String, Object>{
            'attributes' => new Map<String, Object>{ 'type' => 'QuoteLineItemAttribute' },
            'Id' => fakeId(QuoteLineItemAttribute.SObjectType, n),
            'AttributeValue' => value,
            'AttributeDefinition' => definition
        };
        return (QuoteLineItemAttribute) JSON.deserialize(JSON.serialize(row), QuoteLineItemAttribute.class);
    }

    private static AttributePicklistValue picklistValueRow(
            Integer n, Id picklistId, String value, String name, String code) {
        Map<String, Object> row = new Map<String, Object>{
            'attributes' => new Map<String, Object>{ 'type' => 'AttributePicklistValue' },
            'Id' => fakeId(AttributePicklistValue.SObjectType, n),
            'PicklistId' => picklistId,
            'Value' => value,
            'Name' => name,
            'Code' => code
        };
        return (AttributePicklistValue) JSON.deserialize(JSON.serialize(row), AttributePicklistValue.class);
    }

    // A well-formed id of the given object that matches no record.
    private static Id fakeId(Schema.SObjectType type, Integer n) {
        String suffix = String.valueOf(n).leftPad(12, '0');
        return Id.valueOf(type.getDescribe().getKeyPrefix() + suffix);
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
