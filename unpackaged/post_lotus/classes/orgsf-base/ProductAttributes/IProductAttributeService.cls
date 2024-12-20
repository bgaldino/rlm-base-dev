public interface IProductAttributeService {

    Map<Id, Map<String, Object>> getProductAttributesForProducts(List<Id> productIds);
    Map<Id, Map<String, Object>> getProductAttributesForProducts(List<Product2> products);

}