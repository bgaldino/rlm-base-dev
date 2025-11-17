// Step 3: Delete Product Relationships (correct order for dependencies)
System.debug('=== Step 3: Cleaning up product relationships ===');
Integer total = 0, batch = 200;

// Delete ProductRampSegment FIRST (depends on ProductSellingModelOption)
List<ProductRampSegment> prs = [SELECT Id FROM ProductRampSegment WHERE Product.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
while (!prs.isEmpty()) {
    delete prs;
    total += prs.size();
    prs = [SELECT Id FROM ProductRampSegment WHERE Product.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
}
System.debug('Deleted ProductRampSegment: ' + total);

// Delete ProductRelatedComponent
List<ProductRelatedComponent> prc = [SELECT Id FROM ProductRelatedComponent WHERE ParentProduct.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
Integer prcCount = 0;
while (!prc.isEmpty()) {
    delete prc;
    prcCount += prc.size();
    prc = [SELECT Id FROM ProductRelatedComponent WHERE ParentProduct.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
}
total += prcCount;
System.debug('Deleted ProductRelatedComponent: ' + prcCount);

// Delete ProductComponentGroup
List<ProductComponentGroup> pcg = [SELECT Id FROM ProductComponentGroup WHERE ParentProduct.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
Integer pcgCount = 0;
while (!pcg.isEmpty()) {
    delete pcg;
    pcgCount += pcg.size();
    pcg = [SELECT Id FROM ProductComponentGroup WHERE ParentProduct.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
}
total += pcgCount;
System.debug('Deleted ProductComponentGroup: ' + pcgCount);

// Delete ProductSellingModelOption (AFTER ProductRampSegment)
List<ProductSellingModelOption> psmo = [SELECT Id FROM ProductSellingModelOption WHERE Product2.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
Integer psmoCount = 0;
while (!psmo.isEmpty()) {
    delete psmo;
    psmoCount += psmo.size();
    psmo = [SELECT Id FROM ProductSellingModelOption WHERE Product2.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
}
total += psmoCount;
System.debug('Deleted ProductSellingModelOption: ' + psmoCount);

// Delete ProductCategoryProduct
List<ProductCategoryProduct> pcp = [SELECT Id FROM ProductCategoryProduct WHERE Product.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
Integer pcpCount = 0;
while (!pcp.isEmpty()) {
    delete pcp;
    pcpCount += pcp.size();
    pcp = [SELECT Id FROM ProductCategoryProduct WHERE Product.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
}
total += pcpCount;
System.debug('Deleted ProductCategoryProduct: ' + pcpCount);

System.debug('=== Step 3 Complete: ' + total + ' records deleted ===');