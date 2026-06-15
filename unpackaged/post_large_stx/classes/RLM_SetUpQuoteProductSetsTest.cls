@IsTest
private class RLM_SetUpQuoteProductSetsTest {

    @IsTest
    static void testNormalizeProductSetMode() {
        System.assertEquals(
            RLM_SetUpQuoteProductSets.PRODUCT_SET_QUANTUMBIT,
            RLM_SetUpQuoteProductSets.normalizeProductSetMode(null),
            'Null defaults to QuantumBit'
        );
        System.assertEquals(
            RLM_SetUpQuoteProductSets.PRODUCT_SET_QUANTUMBIT,
            RLM_SetUpQuoteProductSets.normalizeProductSetMode('   '),
            'Blank defaults to QuantumBit'
        );
        System.assertEquals(
            RLM_SetUpQuoteProductSets.PRODUCT_SET_SIEMENS,
            RLM_SetUpQuoteProductSets.normalizeProductSetMode('siemens'),
            'Case-insensitive Siemens'
        );
        System.assertEquals(
            RLM_SetUpQuoteProductSets.PRODUCT_SET_QUANTUMBIT,
            RLM_SetUpQuoteProductSets.normalizeProductSetMode('something-else'),
            'Unknown defaults to QuantumBit'
        );
        System.assertEquals(true, RLM_SetUpQuoteProductSets.isSiemens('SIEMENS'));
        System.assertEquals(false, RLM_SetUpQuoteProductSets.isSiemens('QUANTUMBIT'));
    }

    @IsTest
    static void testIdentifiersForResolution() {
        List<String> qb = RLM_SetUpQuoteProductSets.identifiersForResolution(RLM_SetUpQuoteProductSets.PRODUCT_SET_QUANTUMBIT);
        System.assert(!qb.isEmpty(), 'QuantumBit identifiers must be non-empty');
        System.assert(qb.contains(RLM_DemoProductCodes.BULK_BUNDLE_PRODUCT_IDENTIFIER), 'Must include the bulk bundle');

        List<String> siemens = RLM_SetUpQuoteProductSets.identifiersForResolution(RLM_SetUpQuoteProductSets.PRODUCT_SET_SIEMENS);
        System.assert(siemens.contains(RLM_SetUpQuoteProductSets.SIEMENS_BUNDLE_IDENTIFIER), 'Must include the Siemens bundle');

        Set<String> siemensSet = RLM_SetUpQuoteProductSets.siemensProductIdentifierSet();
        System.assert(siemensSet.contains(RLM_SetUpQuoteProductSets.SIEMENS_BUNDLE_IDENTIFIER), 'Set includes bundle');
        System.assert(siemensSet.size() > 1, 'Set includes simple identifiers');
    }

    @IsTest
    static void testAllocateRequests_NonPositiveReturnsEmpty() {
        System.assertEquals(0, RLM_SetUpQuoteProductSets.allocateRequests('QUANTUMBIT', 0).size());
        System.assertEquals(0, RLM_SetUpQuoteProductSets.allocateRequests('QUANTUMBIT', -3).size());
        System.assertEquals(0, RLM_SetUpQuoteProductSets.allocateRequests('SIEMENS', null).size());
    }

    @IsTest
    static void testAllocateRequests_QuantumBit() {
        // Small count (< threshold) → all simple, no bundles
        List<RLM_SetUpQuoteProductSets.ProductRequest> small = RLM_SetUpQuoteProductSets.allocateRequests('QUANTUMBIT', 5);
        System.assertEquals(5, small.size(), 'Small QuantumBit count yields 5 simple requests');
        System.assertEquals(5, sumExpected(small), 'Expected QLI total equals requested');

        // Large count → some bundles + simples, total expected equals requested
        List<RLM_SetUpQuoteProductSets.ProductRequest> large = RLM_SetUpQuoteProductSets.allocateRequests('QUANTUMBIT', 100);
        Integer bundles = 0;
        for (RLM_SetUpQuoteProductSets.ProductRequest r : large) {
            if (r.productIdentifier == RLM_DemoProductCodes.BULK_BUNDLE_PRODUCT_IDENTIFIER) {
                bundles++;
            }
        }
        System.assertEquals(2, bundles, '100 / 50 = 2 bulk bundles');
        System.assertEquals(100, sumExpected(large), 'Expected QLI total equals requested');
    }

    @IsTest
    static void testAllocateRequests_Siemens() {
        List<RLM_SetUpQuoteProductSets.ProductRequest> small = RLM_SetUpQuoteProductSets.allocateRequests('SIEMENS', 5);
        System.assertEquals(5, small.size(), 'Small Siemens count yields 5 simple requests');
        System.assertEquals(5, sumExpected(small), 'Expected QLI total equals requested');

        List<RLM_SetUpQuoteProductSets.ProductRequest> large = RLM_SetUpQuoteProductSets.allocateRequests('SIEMENS', 100);
        System.assertEquals(100, sumExpected(large), 'Expected QLI total equals requested');
    }

    @IsTest
    static void testExpectedQliCountAndSum() {
        System.assertEquals(0, RLM_SetUpQuoteProductSets.expectedQliCountForRequestedCount('QUANTUMBIT', 0));
        System.assertEquals(7, RLM_SetUpQuoteProductSets.expectedQliCountForRequestedCount('QUANTUMBIT', 7));
        System.assertEquals(7, RLM_SetUpQuoteProductSets.expectedQliCountForRequestedCount('SIEMENS', 7));

        System.assertEquals(0, RLM_SetUpQuoteProductSets.sumExpectedQliCounts('QUANTUMBIT', null));
        System.assertEquals(0, RLM_SetUpQuoteProductSets.sumExpectedQliCounts('QUANTUMBIT', 'not-json'));
        System.assertEquals(7, RLM_SetUpQuoteProductSets.sumExpectedQliCounts('QUANTUMBIT', '{"0":2,"0-0":3,"0-1":2}'));
    }

    @IsTest
    static void testParseNonNegativeInteger() {
        System.assertEquals(0, RLM_SetUpQuoteProductSets.parseNonNegativeInteger(null));
        System.assertEquals(4, RLM_SetUpQuoteProductSets.parseNonNegativeInteger(4));
        System.assertEquals(4, RLM_SetUpQuoteProductSets.parseNonNegativeInteger(4.9));
        System.assertEquals(4, RLM_SetUpQuoteProductSets.parseNonNegativeInteger('4'));
        System.assertEquals(0, RLM_SetUpQuoteProductSets.parseNonNegativeInteger(-2));
        System.assertEquals(0, RLM_SetUpQuoteProductSets.parseNonNegativeInteger('abc'));
    }

    private static Integer sumExpected(List<RLM_SetUpQuoteProductSets.ProductRequest> requests) {
        Integer total = 0;
        for (RLM_SetUpQuoteProductSets.ProductRequest r : requests) {
            total += r.expectedQliCount != null ? r.expectedQliCount : 0;
        }
        return total;
    }
}
