@IsTest
private class RLM_ProductCatalogPbeServiceTest {

    @IsTest
    static void testResolveStandardPricebook2Id() {
        Test.startTest();
        Id pbId = RLM_ProductCatalogPbeService.resolveStandardPricebook2Id();
        Test.stopTest();
        System.assertNotEquals(null, pbId, 'Standard price book Id must resolve in test context');
    }

    @IsTest
    static void testResolveProductsToPBEMap_EmptyInputs() {
        System.assertEquals(0, RLM_ProductCatalogPbeService.resolveProductsToPBEMap(null, Test.getStandardPricebookId()).size());
        System.assertEquals(0, RLM_ProductCatalogPbeService.resolveProductsToPBEMap(new List<String>{ 'X' }, null).size());
        System.assertEquals(
            0,
            RLM_ProductCatalogPbeService.resolveProductsToPBEMap(new List<String>{ 'NO-SUCH-CODE' }, Test.getStandardPricebookId()).size(),
            'Unknown identifiers resolve to empty map'
        );
    }

    @IsTest
    static void testResolveProductsToPBEMap_MatchesByCode() {
        Id pbId = Test.getStandardPricebookId();
        Product2 prod = new Product2(Name = 'Catalog Test Product', ProductCode = 'TESTCODE', IsActive = true);
        insert prod;
        PricebookEntry pbe = new PricebookEntry(
            Pricebook2Id = pbId,
            Product2Id = prod.Id,
            UnitPrice = 12.00,
            IsActive = true
        );
        insert pbe;

        Test.startTest();
        Map<String, PricebookEntry> byCode = RLM_ProductCatalogPbeService.resolveProductsToPBEMap(new List<String>{ 'TESTCODE' }, pbId);
        PricebookEntry single = RLM_ProductCatalogPbeService.resolveProductToPBE('TESTCODE', pbId);
        PricebookEntry missing = RLM_ProductCatalogPbeService.resolveProductToPBE('NOPE', pbId);
        PricebookEntry blank = RLM_ProductCatalogPbeService.resolveProductToPBE(null, pbId);
        Test.stopTest();

        System.assert(byCode.containsKey('TESTCODE'), 'Map resolves the seeded product code');
        System.assertEquals(prod.Id, byCode.get('TESTCODE').Product2Id, 'Resolved PBE points at the seeded product');
        System.assertNotEquals(null, single, 'Single resolve returns the PBE');
        System.assertEquals(null, missing, 'Unknown code resolves to null');
        System.assertEquals(null, blank, 'Blank identifier resolves to null');
    }
}
