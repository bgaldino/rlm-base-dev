// Fetch all Product2 records
List<Product2> products = [SELECT Id, ProductCode, StockKeepingUnit FROM Product2];

// Map to track unique StockKeepingUnit values
Map<String, Integer> skuMap = new Map<String, Integer>();

// List to hold products to update
List<Product2> productsToUpdate = new List<Product2>();

for (Product2 product : products) {
    String baseSku = product.ProductCode;
    String newSku = baseSku;
    
    // Check if the SKU already exists in the map
    if (skuMap.containsKey(newSku)) {
        Integer count = skuMap.get(newSku);
        count++;
        newSku = baseSku + '-' + count;
        skuMap.put(baseSku, count);
    } else {
        skuMap.put(newSku, 0);
    }
    
    // Update the StockKeepingUnit field
    product.StockKeepingUnit = newSku;
    productsToUpdate.add(product);
}

// Update the products in the database
if (!productsToUpdate.isEmpty()) {
    update productsToUpdate;
}