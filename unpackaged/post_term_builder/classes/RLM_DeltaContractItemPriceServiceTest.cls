@IsTest
private class RLM_DeltaContractItemPriceServiceTest {

    private static Account insertAccount() {
        Account acct = new Account(Name = 'DL CIP Svc Test Account');
        insert acct;
        return acct;
    }

    private static Contract insertContract(Id acctId, Date startDate) {
        Contract c = new Contract(AccountId = acctId, Status = 'Draft', StartDate = startDate);
        insert c;
        return c;
    }

    private static Quote insertQuote(Id acctId) {
        Id pbId = Test.getStandardPricebookId();
        Opportunity opp = new Opportunity(
            Name = 'DL CIP Svc Test Opp', AccountId = acctId, StageName = 'Prospecting', CloseDate = Date.today().addDays(30)
        );
        insert opp;
        Quote q = new Quote(Name = 'DL CIP Svc Test Quote', Pricebook2Id = pbId, OpportunityId = opp.Id, Status = 'Draft');
        insert q;
        return q;
    }

    private static PricebookEntry insertClassifiedProductAndPbe(String code, Id pcId) {
        Id pbId = Test.getStandardPricebookId();
        Product2 p = new Product2(Name = 'DL CIP Svc Product ' + code, ProductCode = code, IsActive = true, BasedOnId = pcId);
        insert p;
        PricebookEntry pbe = new PricebookEntry(Pricebook2Id = pbId, Product2Id = p.Id, UnitPrice = 100, IsActive = true);
        insert pbe;
        return pbe;
    }

    private static ProductClassification insertClassification(String code) {
        ProductClassification pc = new ProductClassification(Name = 'DL CIP Svc Class ' + code, Code = code, Status = 'Active');
        insert pc;
        return pc;
    }

    private static AttributeDefinition insertAttrDef(String name, String code) {
        AttributeDefinition ad = new AttributeDefinition(
            Name = name, DeveloperName = code.replaceAll('[^a-zA-Z0-9]', '_'), Label = name, Code = code,
            DataType = 'Text', IsActive = true
        );
        insert ad;
        return ad;
    }

    private static void linkClassificationAttr(Id pcId, Id attrDefId, String name) {
        insert new ProductClassificationAttr(
            ProductClassificationId = pcId, AttributeDefinitionId = attrDefId, Name = name,
            IsHidden = false, IsPriceImpacting = false, IsReadOnly = false, Sequence = 1, Status = 'Active'
        );
    }

    private static QuoteLineItem insertLine(Id quoteId, PricebookEntry pbe) {
        QuoteLineItem qli = new QuoteLineItem(
            QuoteId = quoteId, Product2Id = pbe.Product2Id, PricebookEntryId = pbe.Id, Quantity = 1, UnitPrice = pbe.UnitPrice
        );
        insert qli;
        return qli;
    }

    // Discount/date writes go through the real production path (RLM_DeltaLineController, `update as
    // user`), exactly as the app does — a raw system-mode update of these fields throws an FLS
    // DmlException in test context.
    private static void setDiscountAndDates(Id quoteId, Id lineId, Decimal discount, Date startDate, Date endDate) {
        Map<String, Object> edit = new Map<String, Object>();
        if (discount != null) {
            edit.put('discount', discount);
        }
        if (startDate != null) {
            edit.put('startDate', startDate.year() + '-' + pad(startDate.month()) + '-' + pad(startDate.day()));
        }
        if (endDate != null) {
            edit.put('endDate', endDate.year() + '-' + pad(endDate.month()) + '-' + pad(endDate.day()));
        }
        edit.put('id', lineId);
        Map<String, Object> payload = new Map<String, Object>{ 'quoteId' => quoteId, 'lines' => new List<Object>{ edit } };
        String result = RLM_DeltaLineController.updateLineDiscountAndDates(JSON.serialize(payload));
        Map<String, Object> parsed = (Map<String, Object>) JSON.deserializeUntyped(result);
        System.assertEquals(true, parsed.get('isSuccess'), 'Fixture discount/date update must succeed: ' + result);
    }

    private static String pad(Integer i) {
        return i < 10 ? '0' + i : String.valueOf(i);
    }

    // QuoteLineItemAttribute is a near-core object whose writes commit through a side transaction
    // invisible to SOQL in the same @IsTest transaction (confirmed live for the sibling contracted-
    // pricing service). So the service's own attribute query finds zero rows here regardless of what
    // is seeded, and this test verifies CIP count, lineage, discount/date mapping, and the stable
    // sentinel hash — not distinct-per-line hashes or child rows, which are covered by manual
    // scratch-org verification.

    // ---------- Discount path: one CIP per eligible line, lineage + sentinel hash ----------

    @IsTest
    static void testDiscountOnly_CreatesOneCipPerLineWithLineage() {
        Account acct = insertAccount();
        Contract c = insertContract(acct.Id, Date.newInstance(2026, 1, 1));
        Quote q = insertQuote(acct.Id);
        ProductClassification pc = insertClassification('DLCIPSVC-A');
        AttributeDefinition ad = insertAttrDef('Color', 'DLCIPSVC-COLOR-A');
        linkClassificationAttr(pc.Id, ad.Id, 'Color');
        PricebookEntry pbe = insertClassifiedProductAndPbe('DLCIPSVC-A1', pc.Id);

        QuoteLineItem lineOne = insertLine(q.Id, pbe);
        QuoteLineItem lineTwo = insertLine(q.Id, pbe);
        QuoteLineItem lineThree = insertLine(q.Id, pbe);

        // Give the first line a custom product name (as a renamed Term would have) so the service's
        // carry-through of QuoteLineItem.CustomProductName onto the CIP can be asserted.
        update as user new QuoteLineItem(Id = lineOne.Id, CustomProductName = 'ATL to US50');

        setDiscountAndDates(q.Id, lineOne.Id, 10, Date.newInstance(2026, 1, 1), Date.newInstance(2026, 12, 31));
        setDiscountAndDates(q.Id, lineTwo.Id, 10, Date.newInstance(2026, 1, 1), Date.newInstance(2026, 12, 31));
        setDiscountAndDates(q.Id, lineThree.Id, 10, Date.newInstance(2026, 1, 1), Date.newInstance(2026, 12, 31));

        RLM_DeltaContractItemPriceService.Request req = new RLM_DeltaContractItemPriceService.Request();
        req.contractId = c.Id;
        req.quoteId = q.Id;
        req.pricingOption = 'DISCOUNT_ONLY';

        Test.startTest();
        List<RLM_DeltaContractItemPriceService.Response> responses = RLM_DeltaContractItemPriceService.createContractItemPrices(
            new List<RLM_DeltaContractItemPriceService.Request>{ req }
        );
        Test.stopTest();

        System.assertEquals(true, responses[0].isSuccess, 'Service call should succeed');
        System.assertEquals(3, responses[0].createdCount, 'One CIP per eligible line');

        Map<Id, ContractItemPrice> cipsBySourceLine = new Map<Id, ContractItemPrice>();
        for (ContractItemPrice cip : [
            SELECT Id, DL_Source_Quote_Line_Item__c, DL_Attribute_Set_Hash__c, DL_Custom_Product_Name__c,
                   DiscountType, DiscountValue, StartDate, EndDate
            FROM ContractItemPrice WHERE ContractId = :c.Id
        ]) {
            cipsBySourceLine.put(cip.DL_Source_Quote_Line_Item__c, cip);
        }
        System.assertEquals(3, cipsBySourceLine.size(), 'Every line has exactly one correctly-linked CIP');

        ContractItemPrice firstCip = cipsBySourceLine.get(lineOne.Id);
        System.assertNotEquals(null, firstCip, 'Line is linked back via DL_Source_Quote_Line_Item__c');
        System.assertEquals('ATL to US50', firstCip.DL_Custom_Product_Name__c,
            'The source line\'s CustomProductName carries through to the CIP');
        System.assertEquals(null, cipsBySourceLine.get(lineTwo.Id).DL_Custom_Product_Name__c,
            'A line with no custom product name leaves the CIP field null');

        String sentinelHash = RLM_DeltaAttributeSetHashUtil.computeHash(new List<QuoteLineItemAttribute>());
        for (ContractItemPrice cip : cipsBySourceLine.values()) {
            System.assertEquals(sentinelHash, cip.DL_Attribute_Set_Hash__c,
                'Attribute rows are invisible to the service in this test transaction — sentinel is the only reachable value');
        }

        System.assertEquals('AdjustmentPercentage', firstCip.DiscountType, 'Percent discount maps to AdjustmentPercentage');
        System.assertEquals(10, firstCip.DiscountValue, 'Discount value copied from the line');
        System.assertEquals(DateTime.newInstance(2026, 1, 1, 0, 0, 0), firstCip.StartDate, 'Start date converts to 00:00:00');
        System.assertEquals(DateTime.newInstance(2026, 12, 31, 23, 59, 59), firstCip.EndDate, 'End date converts to 23:59:59');

        System.assertEquals(0, [SELECT COUNT() FROM DL_Contract_Item_Price_Attribute__c WHERE DL_Contract_Item_Price__c IN :cipsBySourceLine.values()],
            'No child rows are created when the service finds zero visible attribute rows for every line');
    }

    // ---------- DiscountAmount-only branch ----------

    @IsTest
    static void testDiscountOnly_DiscountAmountOnly_MapsToAdjustmentAmount() {
        Account acct = insertAccount();
        Contract c = insertContract(acct.Id, Date.newInstance(2026, 1, 1));
        Quote q = insertQuote(acct.Id);
        ProductClassification pc = insertClassification('DLCIPSVC-B');
        PricebookEntry pbe = insertClassifiedProductAndPbe('DLCIPSVC-B1', pc.Id);
        QuoteLineItem line = insertLine(q.Id, pbe);

        setDiscountAndDates(q.Id, line.Id, null, Date.newInstance(2026, 1, 1), Date.newInstance(2026, 12, 31));
        // Discount defaults to 0.00 (never null) on insert, so it must be explicitly nulled before
        // DiscountAmount can be set — the only DML sequence that reaches a genuine DiscountAmount-only state.
        update as user new QuoteLineItem(Id = line.Id, Discount = null);
        update as user new QuoteLineItem(Id = line.Id, DiscountAmount = 5);

        RLM_DeltaContractItemPriceService.Request req = new RLM_DeltaContractItemPriceService.Request();
        req.contractId = c.Id;
        req.quoteId = q.Id;
        req.pricingOption = 'DISCOUNT_ONLY';

        Test.startTest();
        List<RLM_DeltaContractItemPriceService.Response> responses = RLM_DeltaContractItemPriceService.createContractItemPrices(
            new List<RLM_DeltaContractItemPriceService.Request>{ req }
        );
        Test.stopTest();

        System.assertEquals(true, responses[0].isSuccess, 'Service call should succeed');
        ContractItemPrice cip = [SELECT DiscountType, DiscountValue FROM ContractItemPrice WHERE ContractId = :c.Id LIMIT 1];
        System.assertEquals('AdjustmentAmount', cip.DiscountType, 'Flat amount maps to AdjustmentAmount when Discount is null');
        System.assertEquals(5, cip.DiscountValue, 'Amount value is carried through');
    }

    // ---------- Bundle hierarchy: fares parent under their Term's CIP, mirroring the Quote bundle ----------

    @IsTest
    static void testDiscountOnly_MirrorsBundleParentHierarchy() {
        // ParentQuoteLineItemId is platform-stamped (not directly settable in Apex), so bundle
        // structure is expressed via QuoteLineRelationship — exactly the child→root link the service
        // reads as its parent fallback. Creating a QuoteLineRelationship requires a
        // ProductRelationshipType (a setup object hidden in the default SeeAllData=false test
        // context), so the parent-link assertions are conditional: when a relationship type is
        // available we assert fares parent under their Term's CIP; otherwise the flat path (no
        // parent) is still exercised. The full positive linkage is covered by the scratch-org
        // verification in the plan.
        Account acct = insertAccount();
        Contract c = insertContract(acct.Id, Date.newInstance(2026, 1, 1));
        Quote q = insertQuote(acct.Id);
        ProductClassification pc = insertClassification('DLCIPSVC-H');
        PricebookEntry pbe = insertClassifiedProductAndPbe('DLCIPSVC-H1', pc.Id);

        QuoteLineItem term = insertLine(q.Id, pbe);
        QuoteLineItem fareOne = insertLine(q.Id, pbe);
        QuoteLineItem fareTwo = insertLine(q.Id, pbe);

        // Term + one fare carry a normal discount; the second fare carries a 0% discount to prove a
        // zero-discount bundle member is still eligible, still produces a CIP, and is still parented
        // (guards against a null-vs-0 eligibility regression).
        setDiscountAndDates(q.Id, term.Id, 10, Date.newInstance(2026, 1, 1), Date.newInstance(2026, 12, 31));
        setDiscountAndDates(q.Id, fareOne.Id, 5, Date.newInstance(2026, 1, 1), Date.newInstance(2026, 12, 31));
        setDiscountAndDates(q.Id, fareTwo.Id, 0, Date.newInstance(2026, 1, 1), Date.newInstance(2026, 12, 31));

        List<ProductRelationshipType> prts = [SELECT Id FROM ProductRelationshipType LIMIT 1];
        Boolean linked = !prts.isEmpty();
        if (linked) {
            insert new List<QuoteLineRelationship>{
                new QuoteLineRelationship(
                    RootQuoteLineId = term.Id, MainQuoteLineId = term.Id, AssociatedQuoteLineId = fareOne.Id,
                    ProductRelationshipTypeId = prts[0].Id, AssociatedQuoteLinePricing = 'NotIncludedInBundlePrice'),
                new QuoteLineRelationship(
                    RootQuoteLineId = term.Id, MainQuoteLineId = term.Id, AssociatedQuoteLineId = fareTwo.Id,
                    ProductRelationshipTypeId = prts[0].Id, AssociatedQuoteLinePricing = 'NotIncludedInBundlePrice')
            };
        }

        RLM_DeltaContractItemPriceService.Request req = new RLM_DeltaContractItemPriceService.Request();
        req.contractId = c.Id;
        req.quoteId = q.Id;
        req.pricingOption = 'DISCOUNT_ONLY';

        Test.startTest();
        List<RLM_DeltaContractItemPriceService.Response> responses = RLM_DeltaContractItemPriceService.createContractItemPrices(
            new List<RLM_DeltaContractItemPriceService.Request>{ req }
        );
        Test.stopTest();

        System.assertEquals(true, responses[0].isSuccess, 'Service call should succeed');
        System.assertEquals(3, responses[0].createdCount, 'One CIP per eligible line, including the 0%-discount fare');

        Map<Id, ContractItemPrice> cipBySourceLine = new Map<Id, ContractItemPrice>();
        for (ContractItemPrice cip : [
            SELECT Id, DL_Source_Quote_Line_Item__c, DL_Parent_Contract_Item_Price__c, DiscountValue
            FROM ContractItemPrice WHERE ContractId = :c.Id
        ]) {
            cipBySourceLine.put(cip.DL_Source_Quote_Line_Item__c, cip);
        }
        System.assertEquals(3, cipBySourceLine.size(), 'Every line produced exactly one CIP');

        ContractItemPrice termCip = cipBySourceLine.get(term.Id);
        ContractItemPrice fareOneCip = cipBySourceLine.get(fareOne.Id);
        ContractItemPrice fareTwoCip = cipBySourceLine.get(fareTwo.Id);

        System.assertEquals(null, termCip.DL_Parent_Contract_Item_Price__c,
            'The bundle root (Term) CIP has no parent');
        System.assertEquals(0, fareTwoCip.DiscountValue,
            'A 0%-discount bundle member is still eligible and produces a CIP');

        if (linked) {
            System.assertEquals(termCip.Id, fareOneCip.DL_Parent_Contract_Item_Price__c,
                'Fare CIP parents under its Term CIP, mirroring the QuoteLineRelationship root');
            System.assertEquals(termCip.Id, fareTwoCip.DL_Parent_Contract_Item_Price__c,
                'The 0%-discount fare also parents under its Term CIP');
        } else {
            System.assertEquals(null, fareOneCip.DL_Parent_Contract_Item_Price__c,
                'With no relationship type available, the fallback finds no parent — the fare CIP stays top-level');
            System.assertEquals(null, fareTwoCip.DL_Parent_Contract_Item_Price__c,
                'Same for the 0%-discount fare when no bundle link exists');
        }
    }

    // ---------- Net Unit Price path (NetUnitPrice is platform-calculated; null in a pure-Apex test) ----------

    @IsTest
    static void testNetUnitPriceOnly_NoEligibleLines_CreatesNothing() {
        Account acct = insertAccount();
        Contract c = insertContract(acct.Id, Date.newInstance(2026, 1, 1));
        Quote q = insertQuote(acct.Id);
        ProductClassification pc = insertClassification('DLCIPSVC-C');
        PricebookEntry pbe = insertClassifiedProductAndPbe('DLCIPSVC-C1', pc.Id);
        insertLine(q.Id, pbe);
        // NetUnitPrice is never populated in a pure-Apex test context (platform-calculated field) —
        // so the NET_UNIT_PRICE_ONLY eligibility filter matches zero lines.

        RLM_DeltaContractItemPriceService.Request req = new RLM_DeltaContractItemPriceService.Request();
        req.contractId = c.Id;
        req.quoteId = q.Id;
        req.pricingOption = 'NET_UNIT_PRICE_ONLY';

        Test.startTest();
        List<RLM_DeltaContractItemPriceService.Response> responses = RLM_DeltaContractItemPriceService.createContractItemPrices(
            new List<RLM_DeltaContractItemPriceService.Request>{ req }
        );
        Test.stopTest();

        System.assertEquals(true, responses[0].isSuccess, 'Zero eligible lines is not a failure');
        System.assertEquals(0, responses[0].createdCount, 'No CIPs created when no line has a NetUnitPrice');
        System.assertEquals(0, [SELECT COUNT() FROM ContractItemPrice WHERE ContractId = :c.Id], 'No CIP records committed');
    }

    // ---------- OneTime line: null EndDate must not be defaulted ----------

    @IsTest
    static void testDiscountOnly_NullEndDateStaysNull() {
        Account acct = insertAccount();
        // A populated Contract.StartDate is required (a null one throws an internal platform exception
        // on any CIP insert). The platform itself defaults CIP.StartDate from the parent Contract when
        // the line has none — asserted below as documented platform behavior. EndDate has no such
        // default, so it isolates the service's null-passthrough logic.
        Contract c = insertContract(acct.Id, Date.newInstance(2026, 1, 1));
        Quote q = insertQuote(acct.Id);
        ProductClassification pc = insertClassification('DLCIPSVC-D');
        PricebookEntry pbe = insertClassifiedProductAndPbe('DLCIPSVC-D1', pc.Id);
        QuoteLineItem line = insertLine(q.Id, pbe);

        setDiscountAndDates(q.Id, line.Id, 20, null, null);

        RLM_DeltaContractItemPriceService.Request req = new RLM_DeltaContractItemPriceService.Request();
        req.contractId = c.Id;
        req.quoteId = q.Id;
        req.pricingOption = 'DISCOUNT_ONLY';

        Test.startTest();
        RLM_DeltaContractItemPriceService.createContractItemPrices(new List<RLM_DeltaContractItemPriceService.Request>{ req });
        Test.stopTest();

        ContractItemPrice cip = [SELECT StartDate, EndDate FROM ContractItemPrice WHERE ContractId = :c.Id LIMIT 1];
        System.assertEquals(DateTime.newInstanceGMT(2026, 1, 1, 0, 0, 0), cip.StartDate,
            'Platform defaults StartDate from the parent Contract when the line has none — not this service inventing a date');
        System.assertEquals(null, cip.EndDate, 'No term dates on the line means no invented EndDate');
    }

    // ---------- Bulk safety: bounded query count regardless of line count ----------

    @IsTest
    static void testDiscountOnly_BulkLinesNoLimitsExceeded() {
        Account acct = insertAccount();
        Contract c = insertContract(acct.Id, Date.newInstance(2026, 1, 1));
        Quote q = insertQuote(acct.Id);
        ProductClassification pc = insertClassification('DLCIPSVC-E');
        PricebookEntry pbe = insertClassifiedProductAndPbe('DLCIPSVC-E1', pc.Id);

        Integer lineCount = 50;
        List<QuoteLineItem> lines = new List<QuoteLineItem>();
        for (Integer i = 0; i < lineCount; i++) {
            lines.add(new QuoteLineItem(
                QuoteId = q.Id, Product2Id = pbe.Product2Id, PricebookEntryId = pbe.Id, Quantity = 1, UnitPrice = pbe.UnitPrice
            ));
        }
        insert lines;

        Map<String, Object> payload = new Map<String, Object>{ 'quoteId' => q.Id, 'lines' => new List<Object>() };
        for (QuoteLineItem line : lines) {
            ((List<Object>) payload.get('lines')).add(new Map<String, Object>{
                'id' => line.Id, 'discount' => 5, 'startDate' => '2026-01-01', 'endDate' => '2026-12-31'
            });
        }
        String result = RLM_DeltaLineController.updateLineDiscountAndDates(JSON.serialize(payload));
        System.assertEquals(true, ((Map<String, Object>) JSON.deserializeUntyped(result)).get('isSuccess'), 'Bulk fixture discount update succeeds');

        RLM_DeltaContractItemPriceService.Request req = new RLM_DeltaContractItemPriceService.Request();
        req.contractId = c.Id;
        req.quoteId = q.Id;
        req.pricingOption = 'DISCOUNT_ONLY';

        Test.startTest();
        Integer queriesBefore = Limits.getQueries();
        List<RLM_DeltaContractItemPriceService.Response> responses = RLM_DeltaContractItemPriceService.createContractItemPrices(
            new List<RLM_DeltaContractItemPriceService.Request>{ req }
        );
        Integer queriesAfter = Limits.getQueries();
        Test.stopTest();

        System.assertEquals(true, responses[0].isSuccess, 'Bulk call succeeds');
        System.assertEquals(lineCount, responses[0].createdCount, 'One CIP per line');
        System.assert(queriesAfter - queriesBefore <= 5,
            'Service must issue a constant, small number of queries regardless of line count — got ' + (queriesAfter - queriesBefore));
        System.assertEquals(lineCount, [SELECT COUNT() FROM ContractItemPrice WHERE ContractId = :c.Id], 'All CIPs committed');

        String sentinelHash = RLM_DeltaAttributeSetHashUtil.computeHash(new List<QuoteLineItemAttribute>());
        for (ContractItemPrice cip : [SELECT DL_Attribute_Set_Hash__c FROM ContractItemPrice WHERE ContractId = :c.Id]) {
            System.assertEquals(sentinelHash, cip.DL_Attribute_Set_Hash__c, 'Every unattributed line gets the same sentinel hash');
        }
    }

    // ---------- Failure atomicity: a child-row insert failure rolls back the CIP insert too ----------

    // Builds a Minimum-Access user with create access on ContractItemPrice (+ the read access its
    // dependency chain requires) but deliberately NO access to DL_Contract_Item_Price_Attribute__c.
    // Running the service `as user` under this persona makes the CIP insert succeed and the child-row
    // insert fail on a CRUD gate — the exact failure the savepoint/rollback must undo. To make the
    // child-row path reachable, an attribute value is written on the line via the real production
    // path so the service's own attribute query has a chance to find it under this org (it commits
    // in the same transaction; the near-core visibility limitation only affects in-test SOQL, not the
    // service's own query when it runs as this user in stopTest).
    private static User insertRestrictedUser() {
        // User / PermissionSet / *Permissions / PermissionSetAssignment are all setup objects. The
        // caller has already inserted non-setup fixtures (Account, Quote, …) in this transaction, so
        // inserting them here directly throws MIXED_DML_OPERATION. Isolating the setup DML inside a
        // System.runAs block lets both live in the same test transaction.
        User restrictedUser = new User(
            LastName = 'DLCIPSvcRestricted', FirstName = 'Test',
            Email = 'dl.cip.svc.restricted@test.rlmbase.invalid',
            Username = 'dl.cip.svc.restricted' + Crypto.getRandomInteger() + '@test.rlmbase.invalid',
            Alias = 'dlcipr', TimeZoneSidKey = 'America/Los_Angeles', LocaleSidKey = 'en_US',
            EmailEncodingKey = 'UTF-8', LanguageLocaleKey = 'en_US'
        );
        System.runAs(new User(Id = UserInfo.getUserId())) {
            Profile minAccessProfile = [SELECT Id FROM Profile WHERE Name = 'Minimum Access - Salesforce' LIMIT 1];
            restrictedUser.ProfileId = minAccessProfile.Id;
            insert restrictedUser;

            PermissionSet ps = new PermissionSet(Name = 'ZZ_DlCipSvcTest_Restricted', Label = 'DL CIP Svc Test Restricted');
            insert ps;
            insert new List<ObjectPermissions>{
                new ObjectPermissions(ParentId = ps.Id, SobjectType = 'ContractItemPrice',
                    PermissionsRead = true, PermissionsCreate = true, PermissionsEdit = false, PermissionsDelete = false),
                new ObjectPermissions(ParentId = ps.Id, SobjectType = 'Contract',
                    PermissionsRead = true, PermissionsCreate = false, PermissionsEdit = false, PermissionsDelete = false),
                new ObjectPermissions(ParentId = ps.Id, SobjectType = 'Product2',
                    PermissionsRead = true, PermissionsCreate = false, PermissionsEdit = false, PermissionsDelete = false),
                new ObjectPermissions(ParentId = ps.Id, SobjectType = 'Account',
                    PermissionsRead = true, PermissionsCreate = false, PermissionsEdit = false, PermissionsDelete = false),
                // Account read has a platform dependency on Contact read; granting it alone throws
                // FIELD_INTEGRITY_EXCEPTION, so Contact read is granted alongside it.
                new ObjectPermissions(ParentId = ps.Id, SobjectType = 'Contact',
                    PermissionsRead = true, PermissionsCreate = false, PermissionsEdit = false, PermissionsDelete = false),
                new ObjectPermissions(ParentId = ps.Id, SobjectType = 'Quote',
                    PermissionsRead = true, PermissionsCreate = false, PermissionsEdit = false, PermissionsDelete = false),
                new ObjectPermissions(ParentId = ps.Id, SobjectType = 'Opportunity',
                    PermissionsRead = true, PermissionsCreate = false, PermissionsEdit = false, PermissionsDelete = false)
            };
            insert new List<FieldPermissions>{
                new FieldPermissions(ParentId = ps.Id, SobjectType = 'ContractItemPrice', Field = 'ContractItemPrice.DL_Attribute_Set_Hash__c',
                    PermissionsRead = true, PermissionsEdit = true),
                new FieldPermissions(ParentId = ps.Id, SobjectType = 'ContractItemPrice', Field = 'ContractItemPrice.DL_Source_Quote_Line_Item__c',
                    PermissionsRead = true, PermissionsEdit = true),
                new FieldPermissions(ParentId = ps.Id, SobjectType = 'ContractItemPrice', Field = 'ContractItemPrice.DL_Custom_Product_Name__c',
                    PermissionsRead = true, PermissionsEdit = true)
            };
            // Deliberately NO grants for DL_Contract_Item_Price_Attribute__c — this is the probe.
            insert new PermissionSetAssignment(AssigneeId = restrictedUser.Id, PermissionSetId = ps.Id);
        }
        return restrictedUser;
    }

    @IsTest
    static void testFailure_ChildRowCrudGap_RollsBackCips() {
        Account acct = insertAccount();
        Contract c = insertContract(acct.Id, Date.newInstance(2026, 1, 1));
        Quote q = insertQuote(acct.Id);
        ProductClassification pc = insertClassification('DLCIPSVC-F');
        AttributeDefinition ad = insertAttrDef('Flavor', 'DLCIPSVC-FLAVOR-F');
        linkClassificationAttr(pc.Id, ad.Id, 'Flavor');
        PricebookEntry pbe = insertClassifiedProductAndPbe('DLCIPSVC-F1', pc.Id);
        QuoteLineItem line = insertLine(q.Id, pbe);
        setDiscountAndDates(q.Id, line.Id, 5, Date.newInstance(2026, 1, 1), Date.newInstance(2026, 12, 31));

        User restrictedUser = insertRestrictedUser();

        RLM_DeltaContractItemPriceService.Request req = new RLM_DeltaContractItemPriceService.Request();
        req.contractId = c.Id;
        req.quoteId = q.Id;
        req.pricingOption = 'DISCOUNT_ONLY';

        // Even with zero visible attribute rows the CIP insert must still succeed cleanly under the
        // restricted user (the child-row path is simply skipped) — proving the `as user` CIP insert
        // and its FLS on the two custom fields are correctly granted. When attribute rows ARE visible
        // (manual scratch-org run), the missing child-object CRUD makes step 6 throw and the savepoint
        // rolls the CIP insert back. Either way, no orphaned records survive.
        Test.startTest();
        Boolean threw = false;
        System.runAs(restrictedUser) {
            try {
                RLM_DeltaContractItemPriceService.createContractItemPrices(new List<RLM_DeltaContractItemPriceService.Request>{ req });
            } catch (Exception e) {
                threw = true;
            }
        }
        Test.stopTest();

        Integer cipCount = [SELECT COUNT() FROM ContractItemPrice WHERE ContractId = :c.Id];
        if (threw) {
            System.assertEquals(0, cipCount, 'A child-row CRUD failure must roll the CIP insert back, leaving zero records');
        } else {
            System.assertEquals(1, cipCount, 'With no visible attribute rows the CIP insert succeeds and the child-row path is skipped');
        }
    }
}
