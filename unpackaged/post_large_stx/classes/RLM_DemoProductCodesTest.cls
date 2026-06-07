@IsTest
private class RLM_DemoProductCodesTest {

    @IsTest
    static void testOrderedDemoProductIdentifiers() {
        List<String> ordered = RLM_DemoProductCodes.orderedDemoProductIdentifiers();
        System.assert(!ordered.isEmpty(), 'Ordered demo identifiers must be non-empty');
        System.assert(ordered.contains(RLM_DemoProductCodes.EVERGREEN_PRODUCT_IDENTIFIER), 'Includes evergreen');
        System.assert(ordered.contains(RLM_DemoProductCodes.TERMED_PRODUCT_IDENTIFIER), 'Includes termed');
        // Standalone-probe one-times are excluded from the PST rotation
        System.assert(
            !ordered.contains('PROD-2035320005'),
            'Rotation excludes the standalone line-probe one-time codes'
        );
    }

    @IsTest
    static void testIdentifierPredicates() {
        System.assertEquals(true, RLM_DemoProductCodes.isOneTimeIdentifier('QB-SRV-IMP'));
        System.assertEquals(false, RLM_DemoProductCodes.isOneTimeIdentifier(RLM_DemoProductCodes.EVERGREEN_PRODUCT_IDENTIFIER));
        System.assertEquals(false, RLM_DemoProductCodes.isOneTimeIdentifier(null));

        System.assertEquals(true, RLM_DemoProductCodes.isEvergreenIdentifier(RLM_DemoProductCodes.EVERGREEN_PRODUCT_IDENTIFIER));
        System.assertEquals(true, RLM_DemoProductCodes.isTermedIdentifier(RLM_DemoProductCodes.TERMED_PRODUCT_IDENTIFIER));

        System.assertEquals(true, RLM_DemoProductCodes.isStandaloneLineProbeOneTime('PROD-2035320005'));
        System.assertEquals(false, RLM_DemoProductCodes.isStandaloneLineProbeOneTime('QB-SRV-IMP'));
        System.assertEquals(false, RLM_DemoProductCodes.isStandaloneLineProbeOneTime(null));
    }

    @IsTest
    static void testBulkBundleBudget_FallbackWhenNoCatalog() {
        // No QB-BDL-SRVC product in a bare test org → catalog subtree unresolved → fallback budget
        System.assertEquals(null, RLM_DemoProductCodes.countBulkBundleCatalogSubtreeIncludingRoot(null));
        Integer budget = RLM_DemoProductCodes.bulkBundleLineBudgetPerUnitForAllocation(Test.getStandardPricebookId());
        // No QB-BDL-SRVC PBE in a bare test org → catalog count is null → exact fallback
        // value BULK_BUNDLE_LINE_BUDGET_FALLBACK_PER_UNIT (= 3, private constant in RLM_DemoProductCodes)
        System.assertEquals(3, budget, 'Budget falls back to BULK_BUNDLE_LINE_BUDGET_FALLBACK_PER_UNIT (3)');
    }
}
