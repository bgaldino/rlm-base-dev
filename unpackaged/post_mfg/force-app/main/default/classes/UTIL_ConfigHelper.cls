public with sharing class UTIL_ConfigHelper {
    
    @AuraEnabled
    public static SObject getAttributeForId(String Id){
        if (Id == null) {
            throw new AuraHandledException('Invalid Id');
        }
        String query = 'SELECT Id, Name, Label, Description, DataType, IsActive, DeveloperName, PicklistId, DefaultValue ' +
            'FROM AttributeDefinition WHERE Id = :Id LIMIT 1';
        List<SObject> results = Database.query(query);
        return results.isEmpty() ? null : results[0];
    }
    
    @AuraEnabled
    public static List<SObject> getPicklistValuesForPicklistId(String Id){
        if (Id == null ) {
            throw new AuraHandledException('Invalid Id');
        }
        String query = 'SELECT Id, Name, PicklistId, Value, Sequence, IsDefault, DisplayValue, Code, Status, Abbreviation ' +
            'FROM AttributePicklistValue WHERE PicklistId = :Id LIMIT 2000';
        return Database.query(query);
    }
    @AuraEnabled(cacheable=true)
    public static List<SObject> getProductAttributesForProduct(String product2Id) {
        List<SObject> objReturn = new List<SObject>();
        try{
            
            if (String.isBlank(product2Id)) {
                throw new AuraHandledException('Invalid Product2Id');
            }
            // check and see if this product is inherits from a classification
            // Fetch the BasedOnId from the Product2 object
            String query = 'SELECT BasedOnId FROM Product2 WHERE Id = :product2Id LIMIT 1';
            Sobject  prod = ((Product2)Database.query(query)[0]);
            String basedOnId = (String)prod.get('BasedOnId');
            Set<Id> attributeDefinitionIds = new Set<Id>();
            
            // If BasedOnId is not null, fetch ProductClassificationAttr records
            if (basedOnId != null) {
                String classificationQuery = 'SELECT AttributeDefinitionId ' +
                    'FROM ProductClassificationAttr WHERE ProductClassificationId = :basedOnId';
                for (SObject obj : Database.query(classificationQuery)) {
                    attributeDefinitionIds.add((Id)obj.get('AttributeDefinitionId'));
                }
            }
            
            // Fetch ProductAttributeDefinitions for the current product
            String productQuery = 'SELECT AttributeDefinitionId ' +
                'FROM ProductAttributeDefinition WHERE Product2Id = :product2Id';
            for (SObject obj : Database.query(productQuery)) {
                attributeDefinitionIds.add((Id)obj.get('AttributeDefinitionId'));
            }
            
            // Fetch active AttributeDefinitions
            String attributeQuery = 'SELECT Label, Description, DefaultValue, DeveloperName, PicklistId, ' +
                'ValueDescription, Code, Name, IsActive, Id ' +
                'FROM AttributeDefinition ' +
                'WHERE Id IN :attributeDefinitionIds AND IsActive = true';
            
            objReturn = Database.query(attributeQuery);
            // String query = 'SELECT Id, Name, Product2Id, Description, ValueDescription, DefaultValue, AttributeDefinitionId ' +
            //                'FROM ProductAttributeDefinition WHERE Product2Id = :product2Id LIMIT 1000';
            
            // return Database.query(query);
        } catch(Exception e){
            System.debug(e);
        }
        return objReturn;
        
    }
    @AuraEnabled
    public static List<SObject> getProductRelatedComponentsFromProduct(String productId){
        try {
            String queryString = 'SELECT Id, Name, ParentProductId, ChildProductId, ChildProduct.ProductCode, ' +
                'ChildProduct.Name, ProductComponentGroupId, ProductComponentGroup.Name, Quantity, ' +
                'ChildProductRole, ParentProductRole, MinQuantity, MaxQuantity, IsComponentRequired ' +
                'FROM ProductRelatedComponent WHERE ParentProductId = :productId';
            
            return Database.query(queryString);
        } catch (Exception e) {
            throw new AuraHandledException(e.getMessage());
        }
    }
    @AuraEnabled
    public static Product2 getChildProductForRelatedComponentId(String Id){
        Product2 prod = new Product2();
        try{
            String queryString = 'SELECT Id, Name, ChildProductId, ChildProduct.ProductCode, ChildProduct.Name FROM ProductRelatedComponent WHERE Id =:Id LIMIT 1';
            SObject prc =  Database.query(queryString);
            String productId = (String)prc.get('ChildProductId')?? '';
            prod = [SELECT Id, ProductCode, Name FROM Product2 WHERE Id =:productId LIMIT 1];
        } catch(Exception e){
            System.debug(e);
        }
        return prod;
    }
}