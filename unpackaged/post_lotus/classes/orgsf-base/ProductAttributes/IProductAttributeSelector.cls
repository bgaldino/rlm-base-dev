public interface IProductAttributeSelector {
    List<ProductAttributeDefinition> getProductAttributeDefinitions(Set<Id> product2Ids, List<String> attributeDefinitionNames);
    List<ProductAttributeDefinition> getProductAttributeDefinitionsByProductIds(Set<Id> product2Ids);
    List<ProductClassificationAttr> getProductClassificationAttrsByClassificationIds(Set<Id> classificationIds);
    List<Product2> getProductsByProductIdsWithClassificationId(Set<Id> product2Ids);
}