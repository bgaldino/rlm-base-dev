public class RLM_SetUpQuoteProductSets {
    public static final String PRODUCT_SET_QUANTUMBIT = 'QUANTUMBIT';
    public static final String PRODUCT_SET_SIEMENS = 'SIEMENS';

    public static final String SIEMENS_BUNDLE_IDENTIFIER = 'BE2:L-BF-1114';
    public static final Integer SIEMENS_BUNDLE_QLI_COST = 4;
    // Minimum requested QLI count before Siemens allocation introduces bundles.
    private static final Integer SIEMENS_BUNDLE_THRESHOLD = 50;
    public static final Integer QUANTUMBIT_BULK_BUNDLE_QLI_COST = 9;
    private static final Integer QUANTUMBIT_BULK_BUNDLE_THRESHOLD = 50;
    private static final Integer QUANTUMBIT_MAX_BULK_BUNDLES = 50;

    public class ProductRequest {
        public String productIdentifier;
        public Integer expectedQliCount;

        public ProductRequest(String productIdentifier, Integer expectedQliCount) {
            this.productIdentifier = productIdentifier;
            this.expectedQliCount = expectedQliCount;
        }
    }

    public static String normalizeProductSetMode(String productSetMode) {
        String normalized = String.isNotBlank(productSetMode) ? productSetMode.trim().toUpperCase() : PRODUCT_SET_QUANTUMBIT;
        return normalized == PRODUCT_SET_SIEMENS ? PRODUCT_SET_SIEMENS : PRODUCT_SET_QUANTUMBIT;
    }

    public static Boolean isSiemens(String productSetMode) {
        return normalizeProductSetMode(productSetMode) == PRODUCT_SET_SIEMENS;
    }

    public static List<String> identifiersForResolution(String productSetMode) {
        if (!isSiemens(productSetMode)) {
            List<String> out = new List<String>{ RLM_DemoProductCodes.BULK_BUNDLE_PRODUCT_IDENTIFIER };
            out.addAll(RLM_DemoProductCodes.orderedDemoProductIdentifiers());
            return out;
        }
        List<String> out = new List<String>();
        out.add(SIEMENS_BUNDLE_IDENTIFIER);
        out.addAll(siemensSimpleProductIdentifiers());
        return out;
    }

    public static List<String> siemensSimpleProductIdentifiers() {
        return new List<String>{
            'S54319-F1-A1',
            'A5Q00001603',
            'S54310-F18-A1',
            'S54329-F5-A1',
            'S54311-B7-A1',
            'S54372-F16-A1',
            'S54372-F17-A1',
            'S54372-B15-A1',
            'S54400-B91-A1',
            'S54400-B116-A1',
            'BPZ:SSB31',
            'BPZ:SSC31',
            'BPZ:SSB81.1'
        };
    }

    public static Set<String> siemensProductIdentifierSet() {
        Set<String> identifiers = new Set<String>(siemensSimpleProductIdentifiers());
        identifiers.add(SIEMENS_BUNDLE_IDENTIFIER);
        return identifiers;
    }

    public static List<ProductRequest> allocateRequests(String productSetMode, Integer requestedQliCount) {
        Integer target = requestedQliCount == null ? 0 : requestedQliCount;
        List<ProductRequest> out = new List<ProductRequest>();
        if (target <= 0) {
            return out;
        }
        if (!isSiemens(productSetMode)) {
            return allocateQuantumBitRequests(target);
        }

        Integer bundleCount = 0;
        if (target >= SIEMENS_BUNDLE_THRESHOLD) {
            bundleCount = target / SIEMENS_BUNDLE_THRESHOLD;
            Integer maxBundleCount = target / SIEMENS_BUNDLE_QLI_COST;
            if (bundleCount > maxBundleCount) {
                bundleCount = maxBundleCount;
            }
        }

        for (Integer i = 0; i < bundleCount; i++) {
            out.add(new ProductRequest(SIEMENS_BUNDLE_IDENTIFIER, SIEMENS_BUNDLE_QLI_COST));
        }

        Integer simpleCount = target - (bundleCount * SIEMENS_BUNDLE_QLI_COST);
        List<String> simpleIdentifiers = siemensSimpleProductIdentifiers();
        for (Integer i = 0; i < simpleCount; i++) {
            out.add(new ProductRequest(simpleIdentifiers[Math.mod(i, simpleIdentifiers.size())], 1));
        }
        return out;
    }

    private static List<ProductRequest> allocateQuantumBitRequests(Integer target) {
        List<ProductRequest> out = new List<ProductRequest>();
        Integer bundleCount = 0;
        if (target >= QUANTUMBIT_BULK_BUNDLE_THRESHOLD) {
            bundleCount = Math.min(target / QUANTUMBIT_BULK_BUNDLE_THRESHOLD, QUANTUMBIT_MAX_BULK_BUNDLES);
            while (bundleCount > 0 && bundleCount * QUANTUMBIT_BULK_BUNDLE_QLI_COST > target) {
                bundleCount--;
            }
        }

        for (Integer i = 0; i < bundleCount; i++) {
            out.add(new ProductRequest(RLM_DemoProductCodes.BULK_BUNDLE_PRODUCT_IDENTIFIER, QUANTUMBIT_BULK_BUNDLE_QLI_COST));
        }

        Integer simpleCount = target - (bundleCount * QUANTUMBIT_BULK_BUNDLE_QLI_COST);
        List<String> simpleIdentifiers = RLM_DemoProductCodes.orderedDemoProductIdentifiers();
        for (Integer i = 0; i < simpleCount; i++) {
            out.add(new ProductRequest(simpleIdentifiers[Math.mod(i, simpleIdentifiers.size())], 1));
        }
        return out;
    }

    public static Integer expectedQliCountForRequestedCount(String productSetMode, Integer requestedQliCount) {
        // allocateRequests is constructed so the sum of expectedQliCount always equals the
        // normalized requested count: bundles consume part of the target (bundleCount * cost)
        // and singles fill the exact remainder. Return that count directly so preview math
        // (sumExpectedQliCounts) avoids building O(n) ProductRequest lists per group.
        // productSetMode is retained for signature/caller compatibility.
        return (requestedQliCount != null && requestedQliCount > 0) ? requestedQliCount : 0;
    }

    public static Integer sumExpectedQliCounts(String productSetMode, String countsJson) {
        if (String.isBlank(countsJson)) {
            return 0;
        }
        Integer total = 0;
        try {
            Map<String, Object> counts = (Map<String, Object>) JSON.deserializeUntyped(countsJson);
            if (counts == null) {
                return 0;
            }
            for (String key : counts.keySet()) {
                total += expectedQliCountForRequestedCount(productSetMode, parseNonNegativeInteger(counts.get(key)));
            }
        } catch (Exception e) {
            return 0;
        }
        return total;
    }

    public static Integer parseNonNegativeInteger(Object value) {
        if (value == null) {
            return 0;
        }
        Integer parsed;
        if (value instanceof Integer) {
            parsed = (Integer) value;
        } else if (value instanceof Decimal) {
            parsed = ((Decimal) value).intValue();
        } else if (value instanceof Long) {
            parsed = ((Long) value).intValue();
        } else if (value instanceof Double) {
            parsed = ((Double) value).intValue();
        } else {
            try {
                parsed = Integer.valueOf(String.valueOf(value));
            } catch (Exception e) {
                parsed = 0;
            }
        }
        return parsed != null && parsed > 0 ? parsed : 0;
    }
}
