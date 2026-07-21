@IsTest
private class RLM_DeltaCatalogServiceTest {

    @IsTest
    static void testResolveStandardPricebook2Id() {
        Test.startTest();
        Id pbId = RLM_DeltaCatalogService.resolveStandardPricebook2Id();
        Test.stopTest();
        System.assertNotEquals(null, pbId, 'Standard price book Id must resolve in test context');
    }

    @IsTest
    static void testResolveProductsToPBEMap_EmptyInputs() {
        System.assertEquals(0, RLM_DeltaCatalogService.resolveProductsToPBEMap(null, Test.getStandardPricebookId()).size());
        System.assertEquals(0, RLM_DeltaCatalogService.resolveProductsToPBEMap(new List<String>{ 'X' }, null).size());
        System.assertEquals(
            0,
            RLM_DeltaCatalogService.resolveProductsToPBEMap(new List<String>{ 'NO-SUCH-CODE' }, Test.getStandardPricebookId()).size(),
            'Unknown identifiers resolve to empty map'
        );
    }

    @IsTest
    static void testResolveProductsToPBEMap_MatchesByCode() {
        Id pbId = Test.getStandardPricebookId();
        Product2 prod = new Product2(Name = 'Catalog Test Product', ProductCode = 'TESTCODE', IsActive = true);
        insert prod;
        PricebookEntry pbe = new PricebookEntry(Pricebook2Id = pbId, Product2Id = prod.Id, UnitPrice = 12.00, IsActive = true);
        insert pbe;

        Test.startTest();
        Map<String, PricebookEntry> byCode = RLM_DeltaCatalogService.resolveProductsToPBEMap(new List<String>{ 'TESTCODE' }, pbId);
        PricebookEntry single = RLM_DeltaCatalogService.resolveProductToPBE('TESTCODE', pbId);
        PricebookEntry missing = RLM_DeltaCatalogService.resolveProductToPBE('NOPE', pbId);
        PricebookEntry blank = RLM_DeltaCatalogService.resolveProductToPBE(null, pbId);
        Test.stopTest();

        System.assert(byCode.containsKey('TESTCODE'), 'Map resolves the seeded product code');
        System.assertEquals(prod.Id, byCode.get('TESTCODE').Product2Id, 'Resolved PBE points at the seeded product');
        System.assertNotEquals(null, single, 'Single resolve returns the PBE');
        System.assertEquals(null, missing, 'Unknown code resolves to null');
        System.assertEquals(null, blank, 'Blank identifier resolves to null');
    }

    @IsTest
    static void testResolveProductToPBE_CommaPrefixFallback() {
        Id pbId = Test.getStandardPricebookId();
        Product2 prod = new Product2(Name = 'Prefix Product', ProductCode = 'PREFIXCODE', IsActive = true);
        insert prod;
        insert new PricebookEntry(Pricebook2Id = pbId, Product2Id = prod.Id, UnitPrice = 1, IsActive = true);

        Test.startTest();
        // Identifier with a trailing comma segment should fall back to the prefix before the last comma.
        PricebookEntry pbe = RLM_DeltaCatalogService.resolveProductToPBE('PREFIXCODE, extra', pbId);
        Test.stopTest();

        System.assertNotEquals(null, pbe, 'Comma-prefix fallback resolves the PBE');
        System.assertEquals(prod.Id, pbe.Product2Id, 'Fallback resolves to the seeded product');
    }

    @IsTest
    static void testTranslateRuntimeRelationshipType_PassThroughAndNull() {
        // A non-classification type is returned unchanged. ProductRelationshipType is a setup object not
        // visible in the default (SeeAllData=false) context, so the classification-id set is empty here;
        // any real Id that isn't a classification type therefore passes through. Use a Product2 Id as a
        // guaranteed non-classification sentinel (distinct key prefix, can never be a PRT id).
        Product2 prod = new Product2(Name = 'PRT Sentinel', ProductCode = 'PRTSENTINEL', IsActive = true);
        insert prod;

        Test.startTest();
        Id passThrough = RLM_DeltaCatalogService.translateRuntimeRelationshipTypeId(prod.Id);
        // A null source maps to the bundle-component type; none is visible in this context, so null.
        Id fromNull = RLM_DeltaCatalogService.translateRuntimeRelationshipTypeId(null);
        Test.stopTest();

        System.assertEquals(prod.Id, passThrough, 'A non-classification relationship type passes through unchanged');
        System.assertEquals(null, fromNull, 'A null source resolves to the bundle-component type (absent in this context)');
    }

    @IsTest
    static void testTranslateRuntimeRelationshipType_ClassificationToBundleComponent() {
        // The real translation depends on org-configured ProductRelationshipType rows (a setup object),
        // so this assertion is conditional: when both a classification-component and a bundle-component
        // type exist (as on the Delta org), a classification type must translate to the bundle-component
        // type — never staying a classification type, which would block quote→order conversion.
        List<ProductRelationshipType> classif = [
            SELECT Id FROM ProductRelationshipType WHERE AssociatedProductRoleCat = 'ClassificationComponent' LIMIT 1
        ];
        Id bundleComponentId = RLM_DeltaCatalogService.resolveBundleComponentRelationshipTypeId();
        if (classif.isEmpty() || bundleComponentId == null) {
            return; // Types not visible in this context; the deterministic branches are covered above.
        }
        Test.startTest();
        Id translated = RLM_DeltaCatalogService.translateRuntimeRelationshipTypeId(classif[0].Id);
        Test.stopTest();
        System.assertEquals(bundleComponentId, translated, 'A classification type translates to the bundle-component type');
        System.assertNotEquals(classif[0].Id, translated, 'The classification type is never stamped on a runtime relationship');
    }

    @IsTest
    static void testQueryPBEsByProductIds() {
        Id pbId = Test.getStandardPricebookId();
        Product2 prod = new Product2(Name = 'Query PBE Product', ProductCode = 'QPBE', IsActive = true);
        insert prod;
        insert new PricebookEntry(Pricebook2Id = pbId, Product2Id = prod.Id, UnitPrice = 5, IsActive = true);

        Test.startTest();
        List<PricebookEntry> pbes = RLM_DeltaCatalogService.queryPBEsByProductIds(new Set<Id>{ prod.Id }, pbId);
        List<PricebookEntry> none = RLM_DeltaCatalogService.queryPBEsByProductIds(null, pbId);
        Test.stopTest();

        System.assertEquals(1, pbes.size(), 'Returns the active PBE for the product');
        System.assertEquals(0, none.size(), 'Null product set returns empty');
    }
}
