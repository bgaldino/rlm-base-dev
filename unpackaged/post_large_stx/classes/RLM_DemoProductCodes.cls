/**
 * Product identifiers (ProductCode) for demo quote setup and PST bulk add-products.
 * Aligns with Siemens Example CSV / SetUpQuoteCsvImportTest SIEMENS_CSV_PRODUCT_IDENTIFIERS subset.
 */
public class RLM_DemoProductCodes {
    public static final List<String> ONE_TIME_PRODUCT_IDENTIFIERS = new List<String>{
        'PROD-2035320005',
        'PROD-1768772247',
        'PROD-77740090',
        'PROD-617615202',
        'PROD-1776230868',
        'QB-SRV-IMP',
        'PROD-1795624702',
        'QB-SRV-ISE',
        'QB-NET X710',
        'QB-BET X710SFP'
    };
    public static final String EVERGREEN_PRODUCT_IDENTIFIER = 'TEST-SUB';
    public static final String TERMED_PRODUCT_IDENTIFIER = 'QB-TRN-ESSNTLS';
    /** OmniRack bundle (large line expansion) — requires PCM bundle in org. */
    public static final String OMNIRACK_PRODUCT_IDENTIFIER = 'PROD-455868158';
    /** Bulk bundle product for PST add-products heuristics. */
    public static final String BULK_BUNDLE_PRODUCT_IDENTIFIER = 'QB-BDL-SRVC';

    /**
     * Three one-time SKUs used for isolation PST checks on a new org: verify each persists as a QLI
     * before trusting Add Products rotation.
     *
     * Known issue observed during Storm validation: these three products silently drop in `PSTConfig` on the source
     * org (CPQ catalog index does not recognize them even with correct `ProductSellingModelOption`/`PricebookEntry.ProductSellingModelId`/
     * field parity with working OneTime products; a brand-new DML-inserted Product2 reproduces the same
     * `PSTConfig` failure). They are therefore excluded from {@link #ONE_TIME_ROTATION_IDENTIFIERS} so
     * Add Products targets persist deterministically; they remain in {@link #ONE_TIME_PRODUCT_IDENTIFIERS}
     * for catalog/resolution diagnostics.
     */
    public static final List<String> STANDALONE_LINE_PROBE_ONE_TIME_IDENTIFIERS = new List<String>{
        'PROD-2035320005',
        'PROD-77740090',
        'PROD-1776230868'
    };

    /**
     * One-time identifiers used in the Add Products **rotation** (PST) — excludes
     * {@link #STANDALONE_LINE_PROBE_ONE_TIME_IDENTIFIERS} because those fail `PSTConfig`
     * on the source validation org and zero out QLIs. Use this list (not {@link #ONE_TIME_PRODUCT_IDENTIFIERS})
     * wherever we enqueue one-times into a PST Add Products request; the full list remains
     * available for catalog resolution / diagnostics.
     */
    private static final Set<String> ONE_TIME_ROTATION_EXCLUDES = new Set<String>(STANDALONE_LINE_PROBE_ONE_TIME_IDENTIFIERS);
    public static final List<String> ONE_TIME_ROTATION_IDENTIFIERS = buildOneTimeRotationIdentifiers();

    private static List<String> buildOneTimeRotationIdentifiers() {
        List<String> out = new List<String>();
        for (String ident : ONE_TIME_PRODUCT_IDENTIFIERS) {
            if (!ONE_TIME_ROTATION_EXCLUDES.contains(ident)) {
                out.add(ident);
            }
        }
        return out;
    }

    /**
     * Fallback lines per {@link #BULK_BUNDLE_PRODUCT_IDENTIFIER} unit when catalog BFS is unavailable.
     * Storm validation: 4x bundle produced 12 bundle-cluster QLIs, or 3 per unit.
     */
    private static final Integer BULK_BUNDLE_LINE_BUDGET_FALLBACK_PER_UNIT = 3;

    /** Upper cap so a mis-sized BOM does not zero out the singles loop. */
    private static final Integer BULK_BUNDLE_LINE_BUDGET_MAX_CAP = 80;

    private static final Set<String> ONE_TIME_SET = new Set<String>(ONE_TIME_PRODUCT_IDENTIFIERS);

    /**
     * Ordered rotation for PST Add Products: one-time **rotation** list (PST-safe; excludes probe codes
     * that fail `PSTConfig` on the source validation org), then evergreen, then termed. Use this anywhere we push
     * singles into a PST request; for full catalog enumeration use {@link #ONE_TIME_PRODUCT_IDENTIFIERS}
     * directly.
     */
    public static List<String> orderedDemoProductIdentifiers() {
        List<String> o = new List<String>();
        o.addAll(ONE_TIME_ROTATION_IDENTIFIERS);
        o.add(EVERGREEN_PRODUCT_IDENTIFIER);
        o.add(TERMED_PRODUCT_IDENTIFIER);
        return o;
    }

    public static Boolean isOneTimeIdentifier(String ident) {
        return String.isNotBlank(ident) && ONE_TIME_SET.contains(ident);
    }

    public static Boolean isEvergreenIdentifier(String ident) {
        return ident == EVERGREEN_PRODUCT_IDENTIFIER;
    }

    public static Boolean isTermedIdentifier(String ident) {
        return ident == TERMED_PRODUCT_IDENTIFIER;
    }

    /** Mini-bundle one-times that must not drive top-up-only PST (flat batch fails); see {@link #STANDALONE_LINE_PROBE_ONE_TIME_IDENTIFIERS}. */
    public static Boolean isStandaloneLineProbeOneTime(String ident) {
        return String.isNotBlank(ident) && STANDALONE_LINE_PROBE_ONE_TIME_IDENTIFIERS.contains(ident);
    }

    /**
     * {@link ProductRelatedComponent} BFS under the bulk bundle root (including root). Drives
     * {@link #bulkBundleLineBudgetPerUnitForAllocation}; compare to **actual** {@code COUNT(QuoteLineItem)}
     * after adding one bundle via PST on a new org. If CPQ collapses lines, prefer the quote measurement and adjust fallback.
     */
    public static Integer countBulkBundleCatalogSubtreeIncludingRoot(Id pricebook2Id) {
        if (pricebook2Id == null) {
            return null;
        }
        Map<String, PricebookEntry> m = RLM_ProductCatalogPbeService.resolveProductsToPBEMap(
            new List<String>{ BULK_BUNDLE_PRODUCT_IDENTIFIER },
            pricebook2Id
        );
        PricebookEntry pe = m.get(BULK_BUNDLE_PRODUCT_IDENTIFIER);
        if (pe == null || pe.Product2Id == null) {
            return null;
        }
        Id root = pe.Product2Id;
        Set<Id> seen = new Set<Id>{ root };
        Set<Id> frontier = new Set<Id>{ root };
        Integer depth = 0;
        while (!frontier.isEmpty() && depth < 50) {
            Set<Id> next = new Set<Id>();
            for (ProductRelatedComponent prc : [
                SELECT ChildProductId FROM ProductRelatedComponent WHERE ParentProductId IN :frontier
            ]) {
                if (!seen.contains(prc.ChildProductId)) {
                    next.add(prc.ChildProductId);
                }
            }
            frontier.clear();
            for (Id c : next) {
                seen.add(c);
                frontier.add(c);
            }
            depth++;
        }
        return seen.size();
    }

    /**
     * Lines to budget per bulk-bundle **unit** toward {@code targetCount} (replaces legacy fixed {@code 5}).
     * Uses catalog BOM size from {@link #countBulkBundleCatalogSubtreeIncludingRoot}, capped; falls back when unresolved.
     */
    public static Integer bulkBundleLineBudgetPerUnitForAllocation(Id pricebook2Id) {
        Integer n = countBulkBundleCatalogSubtreeIncludingRoot(pricebook2Id);
        if (n == null || n < 1) {
            return BULK_BUNDLE_LINE_BUDGET_FALLBACK_PER_UNIT;
        }
        if (n > BULK_BUNDLE_LINE_BUDGET_MAX_CAP) {
            return BULK_BUNDLE_LINE_BUDGET_MAX_CAP;
        }
        return n;
    }
}
