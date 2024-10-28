public with sharing class ProductAttributeService implements IProductAttributeService {

    static private Map<Id, Map<String, Object>> productAttributeCache = new Map<Id, Map<String, Object>>();

    private IProductAttributeSelector productAttributeSelector;

    public ProductAttributeService(IProductAttributeSelector productAttributeSelector) {
        this.productAttributeSelector = productAttributeSelector;
    }

    public ProductAttributeService() {
        this(new ProductAttributeSelector());
    }

    public Map<Id, Map<String, Object>> getProductAttributesForProducts(List<Id> productIds) {

        Map<Id, Map<String, Object>> productAttributes = new Map<Id, Map<String, Object>>();
        Set<Id> productIdSet = new Set<Id>(productIds);
        Set<Id> uncachedProductIds = new Set<Id>();

        for (Id productId : productIdSet) {
            if (!productAttributeCache.containsKey(productId)) {
                uncachedProductIds.add(productId);
                continue;
            }
            productAttributes.put(productId, productAttributeCache.get(productId));
        }

        if (uncachedProductIds.size() == 0) {
            return productAttributes;
        }

        List<Product2> productsWithClassification = productAttributeSelector.getProductsByProductIdsWithClassificationId(uncachedProductIds);
        Map<Id, Map<String, Object>> fetchedProductAttributes = getProductAttributesForProducts(productsWithClassification);
        for (Id productId : fetchedProductAttributes.keySet()) {
            productAttributes.put(productId, fetchedProductAttributes.get(productId));
        }

        return productAttributes;
    } 

    public Map<Id, Map<String, Object>> getProductAttributesForProducts(List<Product2> products) {
        Map<Id, Map<String, Object>> productAttributes = new Map<Id, Map<String, Object>>();
        List<Product2> uncachedProducts = new List<Product2>();

        for (Product2 product : products) {
            if (!productAttributeCache.containsKey(product.Id)) {
                uncachedProducts.add(product);
                productAttributeCache.put(product.Id, new Map<String, Object>());
                continue;
            }
            productAttributes.put(product.Id, productAttributeCache.get(product.Id));
        }

        if (uncachedProducts.size() == 0) {
            return productAttributes;
        }

        Map<Id, Map<String, Object>> uncachedProductAttributes = fetchProductAttributesForProducts(uncachedProducts);

        for (Id productId : uncachedProductAttributes.keySet()) {
            Map<String, Object> productAttributeMap = uncachedProductAttributes.get(productId);
            productAttributeCache.put(productId, productAttributeMap);
            productAttributes.put(productId, uncachedProductAttributes.get(productId));
        }

        return productAttributes;
    }

    private Map<Id, Map<String, Object>> fetchProductAttributesForProducts(List<Product2> products) {
        Map<Id, Map<String, Object>> productClassificationAttributes = new Map<Id, Map<String, Object>>();

        Map<Id, Map<String, Object>> productAttributes = new Map<Id, Map<String, Object>>();

        Set<Id> productIdSet = new Set<Id>();
        Set<Id> productClassificationIdSet = new Set<Id>();
        for (Product2 product : products) {
            if (product?.Id != null) {
                productIdSet.add(product.Id);
            }
            if (product?.BasedOnId != null) {
                productClassificationIdSet.add(product.BasedOnId);
            }
        }

        List<ProductClassificationAttr> productClassificationAttrs = productAttributeSelector.getProductClassificationAttrsByClassificationIds(productClassificationIdSet);
        for (ProductClassificationAttr pca : productClassificationAttrs) {
            Map<String, Object> productClassificationAttributeMap = productClassificationAttributes.get(pca.ProductClassificationId);
            if (productClassificationAttributeMap == null) {
                productClassificationAttributeMap = new Map<String, Object>();
                productClassificationAttributes.put(pca.ProductClassificationId, productClassificationAttributeMap);
            }
            productClassificationAttributeMap.put(pca.AttributeDefinition.DeveloperName, pca.DefaultValue); 
        }

        for (Product2 p : products) {
            Map<String, Object> productAttributeMap = productClassificationAttributes.get(p.BasedOnId);
            if (productAttributeMap == null) {
                productAttributeMap = new Map<String, Object>();
                productAttributes.put(p.Id, productAttributeMap);
            } else {
                productAttributes.put(p.Id, new Map<String, Object>(productAttributeMap));
            }
        }

        List<ProductAttributeDefinition> productAttributeDefinitionsForProducts = productAttributeSelector.getProductAttributeDefinitionsByProductIds(productIdSet);
        for (ProductAttributeDefinition pad : productAttributeDefinitionsForProducts) {
            Map<String, Object> productAttributeMap = productAttributes.get(pad.Product2Id);
            if (productAttributeMap == null) {
                productAttributeMap = new Map<String, Object>();
                productAttributes.put(pad.Product2Id, productAttributeMap);
            }
            productAttributeMap.put(pad.AttributeDefinition.DeveloperName, pad.DefaultValue);
        }

        return productAttributes;
    }
}