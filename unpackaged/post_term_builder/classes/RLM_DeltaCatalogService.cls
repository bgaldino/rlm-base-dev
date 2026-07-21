/**
 * Resolves Product2 identifiers (ProductCode or Name) to active PricebookEntry rows for a price book.
 * Self-contained helper for the Contracted Pricing negotiation UI (rlmContractedPricingCatalog).
 *
 * Logic mirrors unpackaged/post_large_stx RLM_ProductCatalogPbeService, re-created under a
 * distinct, clearly-scoped name so this feature owns its own deployable copy (no duplicate
 * class name across tiers). The PBE query selects ProductSellingModel.SellingModelType /
 * PricingTermUnit because the catalog controller's add-to-quote path needs them when building
 * selling-model-aware QuoteLineItem fields.
 */
public with sharing class RLM_DeltaCatalogService {
    public class ContractedPricingCatalogException extends Exception {}

    // PBE preference order when a product has multiple selling models and no explicit PBE chosen.
    private static final Map<String, Integer> SELLING_MODEL_ORDER = new Map<String, Integer>{
        'OneTime' => 1,
        'Evergreen' => 2,
        'TermDefined' => 3
    };

    /**
     * Standard Price Book Id. In tests uses Test.getStandardPricebookId(); otherwise queries IsStandard = true.
     * @throws ContractedPricingCatalogException when no standard price book exists (non-test).
     */
    public static Id resolveStandardPricebook2Id() {
        if (Test.isRunningTest()) {
            return Test.getStandardPricebookId();
        }
        List<Pricebook2> pbs = [SELECT Id FROM Pricebook2 WHERE IsStandard = true WITH USER_MODE LIMIT 1];
        if (pbs.isEmpty()) {
            throw new ContractedPricingCatalogException('Standard Price Book not found.');
        }
        return pbs[0].Id;
    }

    // --- Product relationship type resolution (runtime vs design-time) ---
    // A RUNTIME QuoteLineRelationship / OrderItemRelationship between a bundle and a concrete component
    // product must use a bundle-component relationship type. The design-time "Bundle to Product
    // Classification Component Relationship" (AssociatedProductRoleCat = ClassificationComponent) has no
    // OrderItemRelationship role counterpart, so a quote carrying it can't be converted to an order
    // ("The Product Relationship Type isn't valid"). These helpers resolve the correct runtime type and
    // translate a design-time classification type to it. Caches (incl. nulls) so a bundle graph doesn't
    // re-query per relationship.
    private static Boolean bundleComponentPrtResolved = false;
    private static Id bundleComponentPrtIdCache;
    private static Set<Id> classificationComponentPrtIds;

    /** The bundle-component ProductRelationshipType id (Main=Bundle, Assoc=BundleComponent), or null. */
    public static Id resolveBundleComponentRelationshipTypeId() {
        if (!bundleComponentPrtResolved) {
            bundleComponentPrtResolved = true;
            for (ProductRelationshipType prt : [
                SELECT Id FROM ProductRelationshipType
                WHERE MainProductRoleCat = 'Bundle' AND AssociatedProductRoleCat = 'BundleComponent'
                WITH USER_MODE
                LIMIT 1
            ]) {
                bundleComponentPrtIdCache = prt.Id;
            }
        }
        return bundleComponentPrtIdCache;
    }

    /** Ids of all classification-component relationship types (design-time only; invalid on orders). */
    private static Set<Id> classificationComponentRelationshipTypeIds() {
        if (classificationComponentPrtIds == null) {
            classificationComponentPrtIds = new Set<Id>();
            for (ProductRelationshipType prt : [
                SELECT Id FROM ProductRelationshipType
                WHERE AssociatedProductRoleCat = 'ClassificationComponent'
                WITH USER_MODE
            ]) {
                classificationComponentPrtIds.add(prt.Id);
            }
        }
        return classificationComponentPrtIds;
    }

    /**
     * Translate a relationship type from a configurator/design-time source into the type valid for a
     * runtime relationship. A ClassificationComponent type (or a null input) becomes the bundle-component
     * type; any other type (e.g. Set) is returned unchanged. Returns null only when the input wasn't a
     * usable runtime type AND the org has no bundle-component type (create then fails on the required
     * ProductRelationshipTypeId, surfacing the misconfiguration).
     */
    public static Id translateRuntimeRelationshipTypeId(Id sourcePrtId) {
        if (sourcePrtId == null || classificationComponentRelationshipTypeIds().contains(sourcePrtId)) {
            return resolveBundleComponentRelationshipTypeId();
        }
        return sourcePrtId;
    }

    /** Resolve a single product identifier (code or name) to a PricebookEntry for the given price book. */
    public static PricebookEntry resolveProductToPBE(String productIdentifier, Id pricebook2Id) {
        if (String.isBlank(productIdentifier) || pricebook2Id == null) {
            return null;
        }
        String trimmed = productIdentifier.trim();
        Map<String, PricebookEntry> m = resolveProductsToPBEMap(new List<String>{ trimmed }, pricebook2Id);
        PricebookEntry pbe = m.get(trimmed);
        if (pbe != null) {
            return pbe;
        }
        if (trimmed.contains(',')) {
            String prefix = trimmed.substring(0, trimmed.lastIndexOf(',')).trim();
            if (String.isNotBlank(prefix)) {
                pbe = m.get(prefix);
            }
        }
        return pbe;
    }

    /** Bulk resolve identifiers -> PBE (ProductCode wins over Name; PBE order OneTime → Evergreen → TermDefined). */
    public static Map<String, PricebookEntry> resolveProductsToPBEMap(List<String> identifiers, Id pricebook2Id) {
        Map<String, PricebookEntry> result = new Map<String, PricebookEntry>();
        if (identifiers == null || identifiers.isEmpty() || pricebook2Id == null) {
            return result;
        }
        Set<String> idSet = new Set<String>();
        for (String s : identifiers) {
            if (String.isNotBlank(s)) {
                idSet.add(s.trim());
                if (s.contains(',')) {
                    String prefix = s.substring(0, s.lastIndexOf(',')).trim();
                    if (String.isNotBlank(prefix)) {
                        idSet.add(prefix);
                    }
                }
            }
        }
        if (idSet.isEmpty()) {
            return result;
        }
        // Resolve each requested identifier to a single Product2 Id, applying precedence ONCE here
        // (ProductCode wins over Name; first match wins among duplicate codes/names). One query
        // matches on either field; everything downstream works on Ids, not strings.
        Map<String, Id> productIdByIdentifier = new Map<String, Id>();
        Set<String> claimedByCode = new Set<String>();
        for (Product2 p : [
            SELECT Id, ProductCode, Name
            FROM Product2
            WHERE (ProductCode IN :idSet OR Name IN :idSet) AND IsActive = true
            WITH USER_MODE
        ]) {
            // A code match always wins its slot and locks it, so a later/earlier name can't override.
            if (String.isNotBlank(p.ProductCode) && idSet.contains(p.ProductCode) && !claimedByCode.contains(p.ProductCode)) {
                productIdByIdentifier.put(p.ProductCode, p.Id);
                claimedByCode.add(p.ProductCode);
            }
            // A name only fills a slot no code has claimed, and the first name wins.
            if (String.isNotBlank(p.Name) && idSet.contains(p.Name) && !productIdByIdentifier.containsKey(p.Name)) {
                productIdByIdentifier.put(p.Name, p.Id);
            }
        }
        Set<Id> product2Ids = new Set<Id>(productIdByIdentifier.values());
        if (product2Ids.isEmpty()) {
            return result;
        }
        Map<Id, List<PricebookEntry>> pbeByProduct = new Map<Id, List<PricebookEntry>>();
        for (PricebookEntry pe : queryPBEsByProductIds(product2Ids, pricebook2Id)) {
            if (!pbeByProduct.containsKey(pe.Product2Id)) {
                pbeByProduct.put(pe.Product2Id, new List<PricebookEntry>());
            }
            pbeByProduct.get(pe.Product2Id).add(pe);
        }
        for (String iden : productIdByIdentifier.keySet()) {
            List<PricebookEntry> listPbe = pbeByProduct.get(productIdByIdentifier.get(iden));
            if (listPbe == null || listPbe.isEmpty()) {
                continue;
            }
            result.put(iden, choosePreferredPbe(listPbe));
        }
        return result;
    }

    /**
     * Active PBEs for the given products on the given price book, with the selling-model fields the
     * add-to-quote field builder needs. Shared by the controller's server-side PBE revalidation.
     */
    public static List<PricebookEntry> queryPBEsByProductIds(Set<Id> product2Ids, Id pricebook2Id) {
        if (product2Ids == null || product2Ids.isEmpty() || pricebook2Id == null) {
            return new List<PricebookEntry>();
        }
        return [
            SELECT Id, Product2Id, UnitPrice, ProductSellingModelId,
                   ProductSellingModel.SellingModelType, ProductSellingModel.PricingTermUnit
            FROM PricebookEntry
            WHERE Product2Id IN :product2Ids AND Pricebook2Id = :pricebook2Id AND IsActive = true
            WITH USER_MODE
        ];
    }

    /** Lowest-ordered selling model wins (OneTime → Evergreen → TermDefined); unknowns sort last. */
    private static PricebookEntry choosePreferredPbe(List<PricebookEntry> listPbe) {
        PricebookEntry chosen = listPbe[0];
        Integer chosenOrder = orderOf(chosen);
        for (Integer i = 1; i < listPbe.size(); i++) {
            Integer o = orderOf(listPbe[i]);
            if (o < chosenOrder) {
                chosen = listPbe[i];
                chosenOrder = o;
            }
        }
        return chosen;
    }

    private static Integer orderOf(PricebookEntry pbe) {
        String st = (pbe.ProductSellingModel != null) ? String.valueOf(pbe.ProductSellingModel.SellingModelType) : null;
        return (st != null && SELLING_MODEL_ORDER.containsKey(st)) ? SELLING_MODEL_ORDER.get(st) : 99;
    }
}
