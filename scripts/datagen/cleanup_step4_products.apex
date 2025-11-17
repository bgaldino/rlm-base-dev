// Step 4: Delete Product Attributes and Products
System.debug('=== Step 4: Cleaning up products and attributes ===');
Integer total = 0, batch = 200;

// Delete ProductAttributeDefinition
List<ProductAttributeDefinition> pad = [SELECT Id FROM ProductAttributeDefinition WHERE Product2.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
while (!pad.isEmpty()) {
    delete pad;
    total += pad.size();
    pad = [SELECT Id FROM ProductAttributeDefinition WHERE Product2.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
}
System.debug('Deleted ProductAttributeDefinition: ' + total);

// Delete Product2 (LAST - after all dependencies)
List<Product2> p2 = [SELECT Id FROM Product2 WHERE StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
Integer p2Count = 0;
while (!p2.isEmpty()) {
    delete p2;
    p2Count += p2.size();
    p2 = [SELECT Id FROM Product2 WHERE StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
}
total += p2Count;
System.debug('Deleted Product2: ' + p2Count);

System.debug('=== Step 4 Complete: ' + total + ' records deleted ===');
System.debug('=== ALL CLEANUP COMPLETE ===');