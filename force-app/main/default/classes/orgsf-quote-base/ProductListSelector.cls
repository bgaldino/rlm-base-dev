public with sharing class ProductListSelector implements IProductListSelector {

    public Set<Id> selectByPriceBookId(Id pricebookId){
        Set<Id> productIds = new Set<Id>();
        for(PricebookEntry productRecord : [SELECT Product2Id FROM PricebookEntry WHERE Pricebook2Id=:pricebookId WITH SECURITY_ENFORCED]){
           productIds.add(productRecord.Product2Id);
       }
        return productIds;
    }
    
    public Id selectByProductCatalog(){
        Id catalogId;
        for(ProductCatalog catalogRecord : [SELECT Id FROM ProductCatalog WITH SECURITY_ENFORCED]){
			catalogId = catalogRecord.Id;
       }
        return catalogId;
    }
    
}