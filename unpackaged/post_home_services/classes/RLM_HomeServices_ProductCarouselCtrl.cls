/**
 * Controller for the self-service product carousel LWC.
 * Returns products where RLM_HomeServices_DisplayInSelfService__c = true,
 * with list price from the Standard Price Book (PricebookEntry).
 */
public with sharing class RLM_HomeServices_ProductCarouselCtrl {

    /**
     * Wrapper for product card data: name, description, list price, image URL, product Id, pricebook entry Id.
     */
    public class ProductCard {
        @AuraEnabled public String productId;
        @AuraEnabled public String name;
        @AuraEnabled public String description;
        @AuraEnabled public Decimal listPrice;
        @AuraEnabled public String displayUrl;
        @AuraEnabled public String pricebookEntryId;
        public ProductCard(String productId, String name, String description, Decimal listPrice, String displayUrl, String pricebookEntryId) {
            this.productId = productId;
            this.name = name;
            this.description = description;
            this.listPrice = listPrice;
            this.displayUrl = displayUrl;
            this.pricebookEntryId = pricebookEntryId;
        }
    }

    /**
     * Returns products to display in the carousel (RLM_HomeServices_DisplayInSelfService__c = true)
     * with list price from the Standard Price Book.
     */
    @AuraEnabled(cacheable=true)
    public static List<ProductCard> getProducts() {
        List<ProductCard> results = new List<ProductCard>();
        Id standardPricebookId = getStandardPricebookId();
        if (standardPricebookId == null) {
            return results;
        }
        List<Product2> products = [
            SELECT Id, Name, Description, DisplayUrl
            FROM Product2
            WHERE RLM_HomeServices_DisplayInSelfService__c = true
              AND IsActive = true
        ];
        if (products.isEmpty()) {
            return results;
        }
        Set<Id> productIds = new Set<Id>();
        for (Product2 p : products) {
            productIds.add(p.Id);
        }
        Map<Id, PricebookEntry> entryByProductId = new Map<Id, PricebookEntry>();
        for (PricebookEntry pbe : [
            SELECT Id, Product2Id, UnitPrice
            FROM PricebookEntry
            WHERE Pricebook2Id = :standardPricebookId
              AND Product2Id IN :productIds
              AND IsActive = true
        ]) {
            entryByProductId.put(pbe.Product2Id, pbe);
        }
        for (Product2 p : products) {
            PricebookEntry pbe = entryByProductId.get(p.Id);
            if (pbe != null) {
                results.add(new ProductCard(
                    p.Id,
                    p.Name,
                    p.Description != null ? p.Description : '',
                    pbe.UnitPrice != null ? pbe.UnitPrice : 0,
                    p.DisplayUrl,
                    pbe.Id
                ));
            }
        }
        return results;
    }

    private static Id getStandardPricebookId() {
        List<Pricebook2> pb = [SELECT Id FROM Pricebook2 WHERE IsStandard = true LIMIT 1];
        return pb.isEmpty() ? null : pb[0].Id;
    }
}