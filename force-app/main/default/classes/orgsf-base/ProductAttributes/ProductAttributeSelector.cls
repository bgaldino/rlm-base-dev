public with sharing class ProductAttributeSelector implements IProductAttributeSelector {
    public List<ProductAttributeDefinition> getProductAttributeDefinitions(Set<Id> product2Ids, List<String> attributeDefinitionNames) {
        return [SELECT Id, Product2Id, AttributeDefinition.Name, DefaultValue 
                FROM ProductAttributeDefinition 
                WHERE Product2Id IN :product2Ids 
                AND AttributeDefinition.Name IN :attributeDefinitionNames
                WITH SECURITY_ENFORCED];
    }

    public List<ProductAttributeDefinition> getProductAttributeDefinitionsByProductIds(Set<Id> product2Ids) {
        return [SELECT Id, Product2Id, AttributeDefinitionId, AttributeDefinition.Name, AttributeDefinition.DeveloperName, DefaultValue 
                FROM ProductAttributeDefinition 
                WHERE Product2Id IN :product2Ids
                AND Status = 'Active'
                AND AttributeDefinition.IsActive = TRUE
                WITH SECURITY_ENFORCED];
    }

    public List<ProductClassificationAttr> getProductClassificationAttrsByClassificationIds(Set<Id> classificationIds) {
        return [SELECT Id, ProductClassificationId, AttributeDefinitionId, AttributeDefinition.Name, AttributeDefinition.DeveloperName, DefaultValue 
                FROM ProductClassificationAttr 
                WHERE ProductClassificationId IN :classificationIds
                AND Status = 'Active'
                AND AttributeDefinition.IsActive = TRUE
                WITH SECURITY_ENFORCED];
    }

    public List<Product2> getProductsByProductIdsWithClassificationId(Set<Id> product2Ids) {
        return [SELECT Id, BasedOnId FROM Product2 WHERE Id IN :product2Ids WITH SECURITY_ENFORCED];
    }
}