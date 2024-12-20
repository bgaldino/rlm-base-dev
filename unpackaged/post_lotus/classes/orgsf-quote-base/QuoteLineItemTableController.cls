public with sharing class QuoteLineItemTableController {


    @AuraEnabled
    public static Map<Id, Map<String, Object>> getProductAttributes(List<Id> productIds) {
        return ((IProductAttributeService) ServiceRegistry.getInstance('IProductAttributeService')).getProductAttributesForProducts(productIds);
    }
}
