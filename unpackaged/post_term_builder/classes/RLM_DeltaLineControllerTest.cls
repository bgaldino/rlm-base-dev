@IsTest
private class RLM_DeltaLineControllerTest {

    private static Quote insertTestQuote() {
        Id pbId = Test.getStandardPricebookId();
        Account acct = new Account(Name = 'Line Editor Account');
        insert acct;
        Opportunity opp = new Opportunity(
            Name = 'Line Editor Opp',
            AccountId = acct.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;
        Quote q = new Quote(Name = 'Line Editor Quote', Pricebook2Id = pbId, OpportunityId = opp.Id, Status = 'Draft');
        insert q;
        return q;
    }

    private static PricebookEntry insertPbe(String code) {
        Product2 p = new Product2(Name = 'Line Product ' + code, ProductCode = code, IsActive = true);
        insert p;
        PricebookEntry pbe = new PricebookEntry(Pricebook2Id = Test.getStandardPricebookId(), Product2Id = p.Id, UnitPrice = 0, IsActive = true);
        insert pbe;
        return pbe;
    }

    private static QuoteLineItem insertLine(Quote q, PricebookEntry pbe, Id groupId) {
        QuoteLineItem qli = new QuoteLineItem(
            QuoteId = q.Id,
            Product2Id = pbe.Product2Id,
            PricebookEntryId = pbe.Id,
            Quantity = 1,
            UnitPrice = 0
        );
        if (groupId != null) {
            qli.QuoteLineGroupId = groupId;
        }
        insert qli;
        return qli;
    }

    private static Map<String, Object> parse(String body) {
        return (Map<String, Object>) JSON.deserializeUntyped(body);
    }

    // ---------- getQuoteLines ----------

    @IsTest
    static void testGetQuoteLines_Empty() {
        Quote q = insertTestQuote();
        Map<String, Object> res = parse(RLM_DeltaLineController.getQuoteLines(q.Id));
        System.assertEquals(true, res.get('isSuccess'), 'Empty quote succeeds');
        System.assertEquals(0, ((List<Object>) res.get('groups')).size(), 'No groups');
        System.assertEquals(0, ((List<Object>) res.get('ungrouped')).size(), 'No ungrouped lines');
    }

    @IsTest
    static void testGetQuoteLines_InvalidId() {
        Map<String, Object> res = parse(RLM_DeltaLineController.getQuoteLines('bad'));
        System.assertEquals(false, res.get('isSuccess'), 'Invalid id fails gracefully');
    }

    @IsTest
    static void testGetQuoteLines_GroupedAndUngrouped() {
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertPbe('LE-1');
        QuoteLineGroup g = new QuoteLineGroup(QuoteId = q.Id, Name = 'Top', SortOrder = 1);
        insert g;
        insertLine(q, pbe, g.Id);
        insertLine(q, insertPbe('LE-2'), null);

        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaLineController.getQuoteLines(q.Id));
        Test.stopTest();

        List<Object> groups = (List<Object>) res.get('groups');
        System.assertEquals(1, groups.size(), 'One root group');
        Map<String, Object> root = (Map<String, Object>) groups[0];
        System.assertEquals(1, (Integer) root.get('lineCount'), 'Group has one line');
        System.assertEquals(1, ((List<Object>) res.get('ungrouped')).size(), 'One ungrouped line');
    }

    @IsTest
    static void testGetQuoteLines_NestedGroups() {
        Quote q = insertTestQuote();
        QuoteLineGroup parent = new QuoteLineGroup(QuoteId = q.Id, Name = 'Parent', SortOrder = 1);
        insert parent;
        QuoteLineGroup child = new QuoteLineGroup(QuoteId = q.Id, Name = 'Child', ParentQuoteLineGroupId = parent.Id, SortOrder = 1);
        insert child;
        insertLine(q, insertPbe('LE-N'), child.Id);

        Map<String, Object> res = parse(RLM_DeltaLineController.getQuoteLines(q.Id));
        List<Object> roots = (List<Object>) res.get('groups');
        System.assertEquals(1, roots.size(), 'One root');
        Map<String, Object> rootNode = (Map<String, Object>) roots[0];
        List<Object> children = (List<Object>) rootNode.get('children');
        System.assertEquals(1, children.size(), 'Root has one child group');
        Map<String, Object> childNode = (Map<String, Object>) children[0];
        System.assertEquals(1, (Integer) childNode.get('lineCount'), 'Child group has the line');
    }

    @IsTest
    static void testGetQuoteLines_LineDtoShape() {
        // The line DTO must carry parentLineId + hasEditableAttributes for the LWC's bundle
        // indentation and per-row Attributes-icon visibility. A plain product with no attributes has
        // hasEditableAttributes = false (icon hidden) and a null parentLineId (root).
        Quote q = insertTestQuote();
        insertLine(q, insertPbe('DTO-1'), null);

        Map<String, Object> res = parse(RLM_DeltaLineController.getQuoteLines(q.Id));
        List<Object> ungrouped = (List<Object>) res.get('ungrouped');
        System.assertEquals(1, ungrouped.size(), 'One ungrouped line');
        Map<String, Object> dto = (Map<String, Object>) ungrouped[0];
        System.assertEquals(true, dto.containsKey('parentLineId'), 'DTO exposes parentLineId');
        System.assertEquals(null, dto.get('parentLineId'), 'Root line has no parent');
        System.assertEquals(false, dto.get('hasEditableAttributes'),
            'A product with no attributes has no editable attributes');
    }

    @IsTest
    static void testGetQuoteLines_PriorDiscountInDto() {
        // The DTO surfaces DL_PriorDiscount__c as 'priorDiscount' so the grid can show the previous
        // contract's discount read-only. A line with no prior value reports null (hidden in the UI); a
        // line carrying a snapshot reports that value.
        Quote q = insertTestQuote();
        QuoteLineItem withPrior = insertLine(q, insertPbe('PRIOR-1'), null);
        QuoteLineItem noPrior = insertLine(q, insertPbe('PRIOR-2'), null);
        update new QuoteLineItem(Id = withPrior.Id, DL_PriorDiscount__c = 12.5);

        Map<String, Object> res = parse(RLM_DeltaLineController.getQuoteLines(q.Id));
        Map<Id, Object> priorById = new Map<Id, Object>();
        for (Object o : (List<Object>) res.get('ungrouped')) {
            Map<String, Object> dto = (Map<String, Object>) o;
            System.assertEquals(true, dto.containsKey('priorDiscount'), 'DTO exposes priorDiscount');
            priorById.put((Id) dto.get('id'), dto.get('priorDiscount'));
        }
        System.assertEquals(12.5, priorById.get(withPrior.Id), 'Line with a snapshot reports its prior discount');
        System.assertEquals(null, priorById.get(noPrior.Id), 'Line with no snapshot reports null');
    }

    @IsTest
    static void testGetQuoteLines_HasEditableAttributesFlag() {
        // A line whose product carries an informational attribute reports hasEditableAttributes = true
        // (icon shown); a sibling whose only attribute is price-impacting reports false (icon hidden).
        // This mirrors rlmLineAttributePicker's informational filter (non-hidden, non-price-impacting,
        // non-read-only, active definition) computed in bulk.
        Quote q = insertTestQuote();

        Product2 editable = insertClassifiedProduct('Editable Attr Prod', 'EDT-1');
        AttributeDefinition infoAttr = insertAttrDef('Notes', 'LE-NOTES', 'Text', null);
        linkClassificationAttr(editable, infoAttr.Id, 'Notes', false, false, false);
        QuoteLineItem editableLine = insertLineForProduct(q, editable);

        Product2 priceOnly = insertClassifiedProduct('Price Attr Prod', 'PRC-1');
        AttributeDefinition priceAttr = insertAttrDef('Tier', 'LE-TIER', 'Text', null);
        linkClassificationAttr(priceOnly, priceAttr.Id, 'Tier', false, true, false); // price-impacting
        QuoteLineItem priceLine = insertLineForProduct(q, priceOnly);

        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaLineController.getQuoteLines(q.Id));
        Test.stopTest();

        Map<Id, Boolean> editableById = new Map<Id, Boolean>();
        for (Object o : (List<Object>) res.get('ungrouped')) {
            Map<String, Object> dto = (Map<String, Object>) o;
            editableById.put((Id) dto.get('id'), (Boolean) dto.get('hasEditableAttributes'));
        }
        System.assertEquals(true, editableById.get(editableLine.Id),
            'Line with an informational attribute exposes the editable flag');
        System.assertEquals(false, editableById.get(priceLine.Id),
            'Line whose only attribute is price-impacting is not editable');
    }

    // ---------- attribute-flag test helpers ----------
    // Mirrors the verified attribute-test-data shapes from RLM_DeltaCatalogControllerTest: a
    // product BasedOn a fresh ProductClassification, with attributes attached via ProductClassificationAttr
    // (ProductAttributeDefinition requires a parent classification attr in this org).

    private static Map<Id, Id> classificationByProduct = new Map<Id, Id>();

    private static Product2 insertClassifiedProduct(String name, String code) {
        ProductClassification pc = new ProductClassification(Name = name + ' Class', Code = code + '-CLS', Status = 'Active');
        insert pc;
        Product2 p = new Product2(Name = name, ProductCode = code, IsActive = true, BasedOnId = pc.Id);
        insert p;
        insert new PricebookEntry(Pricebook2Id = Test.getStandardPricebookId(), Product2Id = p.Id, UnitPrice = 0, IsActive = true);
        classificationByProduct.put(p.Id, pc.Id);
        return p;
    }

    private static AttributeDefinition insertAttrDef(String name, String code, String dataType, Id picklistId) {
        AttributeDefinition ad = new AttributeDefinition(
            Name = name,
            DeveloperName = code.replaceAll('[^a-zA-Z0-9]', '_'),
            Label = name,
            Code = code,
            DataType = dataType,
            PicklistId = picklistId,
            IsActive = true
        );
        insert ad;
        return ad;
    }

    private static void linkClassificationAttr(Product2 product, Id attrDefId, String name, Boolean hidden, Boolean priceImpacting, Boolean readOnly) {
        insert new ProductClassificationAttr(
            ProductClassificationId = classificationByProduct.get(product.Id),
            AttributeDefinitionId = attrDefId,
            Name = name,
            IsHidden = hidden,
            IsPriceImpacting = priceImpacting,
            IsReadOnly = readOnly,
            // A visible read-only attribute requires a DefaultValue in this org.
            DefaultValue = (readOnly && !hidden) ? 'default' : null,
            Sequence = 1,
            Status = 'Active'
        );
    }

    private static QuoteLineItem insertLineForProduct(Quote q, Product2 p) {
        PricebookEntry pbe = [SELECT Id FROM PricebookEntry WHERE Product2Id = :p.Id LIMIT 1];
        QuoteLineItem qli = new QuoteLineItem(
            QuoteId = q.Id, Product2Id = p.Id, PricebookEntryId = pbe.Id, Quantity = 1, UnitPrice = 0
        );
        insert qli;
        return qli;
    }

    // ---------- updateLineDiscountAndDates ----------

    @IsTest
    static void testUpdate_Valid() {
        Quote q = insertTestQuote();
        QuoteLineItem qli = insertLine(q, insertPbe('UP-1'), null);
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{
                new Map<String, Object>{ 'id' => qli.Id, 'discount' => 15, 'startDate' => '2026-01-01', 'endDate' => '2026-12-31' }
            }
        };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaLineController.updateLineDiscountAndDates(JSON.serialize(in0)));
        Test.stopTest();
        System.assertEquals(true, res.get('isSuccess'), 'Valid update succeeds');
        System.assertEquals(1, (Integer) res.get('updatedCount'), 'One line updated');
        QuoteLineItem after = [SELECT Discount, StartDate, EndDate FROM QuoteLineItem WHERE Id = :qli.Id];
        System.assertEquals(15, after.Discount, 'Discount persisted');
        System.assertEquals(Date.newInstance(2026, 1, 1), after.StartDate, 'Start date persisted');
    }

    @IsTest
    static void testUpdate_BoundaryDiscounts() {
        Quote q = insertTestQuote();
        QuoteLineItem zero = insertLine(q, insertPbe('UP-0'), null);
        QuoteLineItem hundred = insertLine(q, insertPbe('UP-100'), null);
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{
                new Map<String, Object>{ 'id' => zero.Id, 'discount' => 0 },
                new Map<String, Object>{ 'id' => hundred.Id, 'discount' => 100 }
            }
        };
        Map<String, Object> res = parse(RLM_DeltaLineController.updateLineDiscountAndDates(JSON.serialize(in0)));
        System.assertEquals(true, res.get('isSuccess'), 'Boundary discounts 0 and 100 accepted');
    }

    @IsTest
    static void testUpdate_DiscountTooHigh() {
        Quote q = insertTestQuote();
        QuoteLineItem qli = insertLine(q, insertPbe('UP-HI'), null);
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{ new Map<String, Object>{ 'id' => qli.Id, 'discount' => 150 } }
        };
        Map<String, Object> res = parse(RLM_DeltaLineController.updateLineDiscountAndDates(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Discount > 100 rejected');
    }

    @IsTest
    static void testUpdate_EndBeforeStart() {
        Quote q = insertTestQuote();
        QuoteLineItem qli = insertLine(q, insertPbe('UP-DT'), null);
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{
                new Map<String, Object>{ 'id' => qli.Id, 'startDate' => '2026-12-31', 'endDate' => '2026-01-01' }
            }
        };
        Map<String, Object> res = parse(RLM_DeltaLineController.updateLineDiscountAndDates(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'End before start rejected');
    }

    @IsTest
    static void testUpdate_ForeignLineRejectsWholeRequest() {
        Quote q = insertTestQuote();
        QuoteLineItem mine = insertLine(q, insertPbe('UP-MINE'), null);
        Quote other = insertTestQuote();
        QuoteLineItem foreign = insertLine(other, insertPbe('UP-FOR'), null);
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{
                new Map<String, Object>{ 'id' => mine.Id, 'discount' => 10 },
                new Map<String, Object>{ 'id' => foreign.Id, 'discount' => 10 }
            }
        };
        Map<String, Object> res = parse(RLM_DeltaLineController.updateLineDiscountAndDates(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'A foreign line rejects the entire request');
        // Fail-closed: the valid line must NOT have been updated to the attempted discount.
        QuoteLineItem after = [SELECT Discount FROM QuoteLineItem WHERE Id = :mine.Id];
        System.assertNotEquals(10, after.Discount, 'No partial update when any id is foreign');
    }

    @IsTest
    static void testUpdate_EmptyLines() {
        Quote q = insertTestQuote();
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id, 'lines' => new List<Object>() };
        Map<String, Object> res = parse(RLM_DeltaLineController.updateLineDiscountAndDates(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Empty line list rejected');
    }

    @IsTest
    static void testUpdate_MalformedJson() {
        Map<String, Object> res = parse(RLM_DeltaLineController.updateLineDiscountAndDates('{bad'));
        System.assertEquals(false, res.get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    @IsTest
    static void testUpdate_BulkNoDmlInLoop() {
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertPbe('UP-BULK');
        List<QuoteLineItem> lines = new List<QuoteLineItem>();
        for (Integer i = 0; i < 200; i++) {
            lines.add(new QuoteLineItem(QuoteId = q.Id, Product2Id = pbe.Product2Id, PricebookEntryId = pbe.Id, Quantity = 1, UnitPrice = 0));
        }
        insert lines;
        List<Object> edits = new List<Object>();
        for (QuoteLineItem qli : lines) {
            edits.add(new Map<String, Object>{ 'id' => qli.Id, 'discount' => 5 });
        }
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id, 'lines' => edits };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaLineController.updateLineDiscountAndDates(JSON.serialize(in0)));
        Test.stopTest();
        System.assertEquals(true, res.get('isSuccess'), 'Bulk 200-line update succeeds in one DML');
        System.assertEquals(200, (Integer) res.get('updatedCount'), 'All 200 lines updated');
    }

    // Save fare codes on a line through the controller (the proven `update as user` path — a raw
    // system-mode DML of DL_FareCodes__c hits FLS in this org's test context).
    private static Map<String, Object> saveFareCodes(Quote q, Id lineId, List<Object> codes) {
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{ new Map<String, Object>{ 'id' => lineId, 'fareCodes' => codes } }
        };
        return parse(RLM_DeltaLineController.updateLineDiscountAndDates(JSON.serialize(in0)));
    }

    @IsTest
    static void testUpdate_FareCodesAutoNameFare() {
        // Saving fare codes on a (non-Term) fare line stamps CustomProductName = "<Base> (codes)".
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertPbe('FARE-1'); // Product2.Name = 'Line Product FARE-1'
        QuoteLineItem fare = insertLine(q, pbe, null);

        Test.startTest();
        Map<String, Object> res = saveFareCodes(q, fare.Id, new List<Object>{ 'W', 'S', 'J' });
        Test.stopTest();

        System.assertEquals(true, res.get('isSuccess'), 'Fare-code save succeeds');
        QuoteLineItem after = [SELECT DL_FareCodes__c, CustomProductName FROM QuoteLineItem WHERE Id = :fare.Id];
        // The multipicklist re-sorts to picklist-definition order, so assert the SET of codes, not order.
        System.assertEquals(
            new Set<String>{ 'W', 'S', 'J' },
            new Set<String>(after.DL_FareCodes__c.split(';')),
            'All three codes persisted'
        );
        // The auto-name preserves the rep's selection order (built from the client-supplied list).
        System.assertEquals('Line Product FARE-1 (W S J)', after.CustomProductName, 'Fare auto-named from codes');
    }

    @IsTest
    static void testUpdate_FareCodesClearedRevertsName() {
        // Clearing all fare codes clears the auto-name (reverting the grid to the catalog product name).
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertPbe('FARE-2');
        QuoteLineItem fare = insertLine(q, pbe, null);

        // Seed codes (+ auto-name) via the controller, then clear them via a second call.
        saveFareCodes(q, fare.Id, new List<Object>{ 'W', 'S' });
        QuoteLineItem seeded = [SELECT CustomProductName FROM QuoteLineItem WHERE Id = :fare.Id];
        System.assertNotEquals(null, seeded.CustomProductName, 'Precondition: fare is auto-named after seeding');

        Map<String, Object> res = saveFareCodes(q, fare.Id, new List<Object>());
        System.assertEquals(true, res.get('isSuccess'), 'Clearing codes succeeds');
        QuoteLineItem after = [SELECT DL_FareCodes__c, CustomProductName FROM QuoteLineItem WHERE Id = :fare.Id];
        System.assertEquals(null, after.DL_FareCodes__c, 'Codes cleared');
        System.assertEquals(null, after.CustomProductName, 'Auto-name cleared with the codes');
    }

    // Save alliance partners on a line through the controller (same `update as user` path fare codes
    // use; a raw system-mode DML of a multipicklist hits FLS in this org's test context).
    private static Map<String, Object> saveAlliancePartners(Quote q, Id lineId, List<Object> partners) {
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lines' => new List<Object>{ new Map<String, Object>{ 'id' => lineId, 'alliancePartners' => partners } }
        };
        return parse(RLM_DeltaLineController.updateLineDiscountAndDates(JSON.serialize(in0)));
    }

    @IsTest
    static void testUpdate_AlliancePartnersPersistIndependently() {
        // Saving alliance partners stores the ';'-delimited multipicklist and — unlike fare codes —
        // leaves CustomProductName untouched (no auto-name side effect).
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertPbe('FARE-AP');
        QuoteLineItem fare = insertLine(q, pbe, null);

        Test.startTest();
        Map<String, Object> res = saveAlliancePartners(
            q,
            fare.Id,
            new List<Object>{ 'Air France', 'Virgin Atlantic' }
        );
        Test.stopTest();

        System.assertEquals(true, res.get('isSuccess'), 'Alliance-partner save succeeds');
        QuoteLineItem after = [
            SELECT DL_AlliancePartners__c, CustomProductName FROM QuoteLineItem WHERE Id = :fare.Id
        ];
        System.assertEquals(
            new Set<String>{ 'Air France', 'Virgin Atlantic' },
            new Set<String>(after.DL_AlliancePartners__c.split(';')),
            'Both partners persisted'
        );
        System.assertEquals(null, after.CustomProductName, 'Alliance-partner save must NOT auto-name the line');
    }

    @IsTest
    static void testUpdate_AlliancePartnersClearedToNull() {
        // An empty list clears the field to null (mirrors the fare-code clear behavior).
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertPbe('FARE-AP2');
        QuoteLineItem fare = insertLine(q, pbe, null);

        saveAlliancePartners(q, fare.Id, new List<Object>{ 'Korean Air' });
        QuoteLineItem seeded = [SELECT DL_AlliancePartners__c FROM QuoteLineItem WHERE Id = :fare.Id];
        System.assertNotEquals(null, seeded.DL_AlliancePartners__c, 'Precondition: partners seeded');

        Map<String, Object> res = saveAlliancePartners(q, fare.Id, new List<Object>());
        System.assertEquals(true, res.get('isSuccess'), 'Clearing partners succeeds');
        QuoteLineItem after = [SELECT DL_AlliancePartners__c FROM QuoteLineItem WHERE Id = :fare.Id];
        System.assertEquals(null, after.DL_AlliancePartners__c, 'Partners cleared to null');
    }

    @IsTest
    static void testGetQuoteLines_ExposesAlliancePartners() {
        // The read DTO surfaces alliance partners as a list so the modeling grid can seed its editor.
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertPbe('FARE-AP3');
        QuoteLineItem fare = insertLine(q, pbe, null);
        saveAlliancePartners(q, fare.Id, new List<Object>{ 'Aeromexico', 'WestJet' });

        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaLineController.getQuoteLines(q.Id));
        Test.stopTest();

        System.assertEquals(true, res.get('isSuccess'), 'getQuoteLines succeeds');
        List<Object> ungrouped = (List<Object>) res.get('ungrouped');
        Map<String, Object> dto = null;
        for (Object o : ungrouped) {
            Map<String, Object> line = (Map<String, Object>) o;
            if (fare.Id == (Id) line.get('id')) {
                dto = line;
            }
        }
        System.assertNotEquals(null, dto, 'Fare line present in the DTO');
        System.assertEquals(
            new Set<Object>{ 'Aeromexico', 'WestJet' },
            new Set<Object>((List<Object>) dto.get('alliancePartners')),
            'DTO exposes both alliance partners'
        );
    }

    @IsTest
    static void testUpdate_FareCodesOnTermLeavesNameUntouched() {
        // A DL-TERM line is not a fare; a fare-code save must not clobber its separately-managed name.
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertPbe('DL-TERM'); // ProductCode = 'DL-TERM' → recognized as a Term
        QuoteLineItem term = insertLine(q, pbe, null);

        // Name the Term via its dedicated rename path (the only sanctioned way to set a Term name).
        Map<String, Object> renameIn = new Map<String, Object>{
            'quoteId' => q.Id, 'lineId' => term.Id, 'customProductName' => 'ATL to LHR'
        };
        parse(RLM_DeltaLineController.updateTermName(JSON.serialize(renameIn)));

        Map<String, Object> res = saveFareCodes(q, term.Id, new List<Object>{ 'W' });
        System.assertEquals(true, res.get('isSuccess'), 'Save succeeds');
        QuoteLineItem after = [SELECT CustomProductName FROM QuoteLineItem WHERE Id = :term.Id];
        System.assertEquals('ATL to LHR', after.CustomProductName, 'Term name is left untouched by a fare-code edit');
    }

    // ---------- deleteLines ----------

    @IsTest
    static void testDelete_Valid() {
        Quote q = insertTestQuote();
        QuoteLineItem qli = insertLine(q, insertPbe('DEL-1'), null);
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id, 'lineIds' => new List<Object>{ qli.Id } };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaLineController.deleteLines(JSON.serialize(in0)));
        Test.stopTest();
        System.assertEquals(true, res.get('isSuccess'), 'Valid delete succeeds');
        System.assertEquals(1, (Integer) res.get('deletedCount'), 'One line deleted');
        System.assertEquals(0, [SELECT COUNT() FROM QuoteLineItem WHERE Id = :qli.Id], 'Line is gone');
    }

    @IsTest
    static void testDelete_ForeignLineRejectsWholeRequest() {
        Quote q = insertTestQuote();
        QuoteLineItem mine = insertLine(q, insertPbe('DEL-MINE'), null);
        Quote other = insertTestQuote();
        QuoteLineItem foreign = insertLine(other, insertPbe('DEL-FOR'), null);
        Map<String, Object> in0 = new Map<String, Object>{
            'quoteId' => q.Id,
            'lineIds' => new List<Object>{ mine.Id, foreign.Id }
        };
        Map<String, Object> res = parse(RLM_DeltaLineController.deleteLines(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'A foreign line rejects the entire request');
        System.assertEquals(1, [SELECT COUNT() FROM QuoteLineItem WHERE Id = :mine.Id], 'No partial delete when any id is foreign');
    }

    @IsTest
    static void testDelete_EmptyLineIds() {
        Quote q = insertTestQuote();
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id, 'lineIds' => new List<Object>() };
        Map<String, Object> res = parse(RLM_DeltaLineController.deleteLines(JSON.serialize(in0)));
        System.assertEquals(false, res.get('isSuccess'), 'Empty lineIds list rejected');
    }

    @IsTest
    static void testDelete_MalformedJson() {
        Map<String, Object> res = parse(RLM_DeltaLineController.deleteLines('{bad'));
        System.assertEquals(false, res.get('isSuccess'), 'Malformed JSON fails gracefully');
    }

    @IsTest
    static void testDelete_BulkNoDmlInLoop() {
        Quote q = insertTestQuote();
        PricebookEntry pbe = insertPbe('DEL-BULK');
        List<QuoteLineItem> lines = new List<QuoteLineItem>();
        for (Integer i = 0; i < 200; i++) {
            lines.add(new QuoteLineItem(QuoteId = q.Id, Product2Id = pbe.Product2Id, PricebookEntryId = pbe.Id, Quantity = 1, UnitPrice = 0));
        }
        insert lines;
        List<Object> ids = new List<Object>();
        for (QuoteLineItem qli : lines) {
            ids.add(qli.Id);
        }
        Map<String, Object> in0 = new Map<String, Object>{ 'quoteId' => q.Id, 'lineIds' => ids };
        Test.startTest();
        Map<String, Object> res = parse(RLM_DeltaLineController.deleteLines(JSON.serialize(in0)));
        Test.stopTest();
        System.assertEquals(true, res.get('isSuccess'), 'Bulk 200-line delete succeeds in one DML');
        System.assertEquals(200, (Integer) res.get('deletedCount'), 'All 200 lines deleted');
    }
}
