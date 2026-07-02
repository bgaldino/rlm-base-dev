/**
 * Resolves Product2 identifiers (ProductCode or Name) to active PricebookEntry rows for a price book.
 * Shared by RLM_SetUpQuoteInvocable (CSV / tree / hierarchy) and DemoInvocableAction (PST add-products).
 */
public with sharing class RLM_ProductCatalogPbeService {
    public class ProductCatalogPbeException extends Exception {}

    /**
     * Standard Price Book Id. In tests uses Test.getStandardPricebookId(); otherwise queries IsStandard = true.
     * @throws ProductCatalogPbeException when no standard price book exists (non-test).
     */
    public static Id resolveStandardPricebook2Id() {
        if (Test.isRunningTest()) {
            return Test.getStandardPricebookId();
        }
        List<Pricebook2> pbs = [SELECT Id FROM Pricebook2 WHERE IsStandard = true WITH USER_MODE LIMIT 1];
        if (pbs.isEmpty()) {
            throw new ProductCatalogPbeException('Standard Price Book not found.');
        }
        return pbs[0].Id;
    }

    /** Resolve product identifier (code or name) to a PricebookEntry for the given price book. Tries ProductCode first, then Name. PBE order: OneTime → Evergreen → TermDefined. If not found and identifier contains a comma, retries with the part before the last comma. */
    public static PricebookEntry resolveProductToPBE(String productIdentifier, Id pricebook2Id) {
        if (String.isBlank(productIdentifier) || pricebook2Id == null) {
            return null;
        }
        List<String> ids = new List<String>{ productIdentifier.trim() };
        Map<String, PricebookEntry> m = resolveProductsToPBEMap(ids, pricebook2Id);
        String trimmed = productIdentifier.trim();
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

    /** Bulk resolve: run SOQL once per batch. Returns map identifier -> PBE (ProductCode wins over Name; PBE order OneTime → Evergreen → TermDefined). */
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
        List<String> idList = new List<String>(idSet);
        // Lookup maps keyed by identifier (ProductCode / Name) so each requested
        // identifier resolves in O(1) below instead of re-scanning the result lists.
        Map<String, Id> productIdByCode = new Map<String, Id>();
        Map<String, Id> productIdByName = new Map<String, Id>();
        for (Product2 p : [SELECT Id, ProductCode, Name FROM Product2 WHERE ProductCode IN :idList AND IsActive = true WITH USER_MODE]) {
            if (String.isNotBlank(p.ProductCode) && !productIdByCode.containsKey(p.ProductCode)) {
                productIdByCode.put(p.ProductCode, p.Id);
            }
        }
        for (Product2 p : [SELECT Id, ProductCode, Name FROM Product2 WHERE Name IN :idList AND IsActive = true WITH USER_MODE]) {
            if (String.isNotBlank(p.Name) && !productIdByName.containsKey(p.Name)) {
                productIdByName.put(p.Name, p.Id);
            }
        }
        Set<Id> product2Ids = new Set<Id>();
        product2Ids.addAll(productIdByCode.values());
        product2Ids.addAll(productIdByName.values());
        if (product2Ids.isEmpty()) {
            return result;
        }
        List<PricebookEntry> pbes = [
            SELECT Id, Product2Id, UnitPrice, ProductSellingModel.SellingModelType, ProductSellingModel.PricingTermUnit
            FROM PricebookEntry
            WHERE Product2Id IN :product2Ids AND Pricebook2Id = :pricebook2Id AND IsActive = true
            WITH USER_MODE
        ];
        Map<Id, List<PricebookEntry>> pbeByProduct = new Map<Id, List<PricebookEntry>>();
        Map<String, Integer> orderMap = new Map<String, Integer>{
            'OneTime' => 1,
            'Evergreen' => 2,
            'TermDefined' => 3
        };
        for (PricebookEntry pe : pbes) {
            if (!pbeByProduct.containsKey(pe.Product2Id)) {
                pbeByProduct.put(pe.Product2Id, new List<PricebookEntry>());
            }
            pbeByProduct.get(pe.Product2Id).add(pe);
        }
        for (String iden : idList) {
            // ProductCode wins over Name, matching the prior resolution order.
            Id product2Id = productIdByCode.containsKey(iden)
                ? productIdByCode.get(iden)
                : productIdByName.get(iden);
            if (product2Id == null) {
                continue;
            }
            List<PricebookEntry> listPbe = pbeByProduct.get(product2Id);
            if (listPbe == null || listPbe.isEmpty()) {
                continue;
            }
            PricebookEntry chosen = listPbe[0];
            Integer chosenOrder = orderMap.containsKey(
                    String.valueOf(chosen.ProductSellingModel != null ? chosen.ProductSellingModel.SellingModelType : null))
                ? orderMap.get(String.valueOf(chosen.ProductSellingModel.SellingModelType))
                : 99;
            for (Integer i = 1; i < listPbe.size(); i++) {
                String st = listPbe[i].ProductSellingModel != null
                    ? String.valueOf(listPbe[i].ProductSellingModel.SellingModelType)
                    : null;
                Integer o = orderMap.containsKey(st) ? orderMap.get(st) : 99;
                if (o < chosenOrder) {
                    chosen = listPbe[i];
                    chosenOrder = o;
                }
            }
            result.put(iden, chosen);
        }
        return result;
    }
}
