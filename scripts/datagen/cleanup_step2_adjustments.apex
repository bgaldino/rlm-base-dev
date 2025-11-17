// Step 2: Delete Adjustments (including all bundle references)
System.debug('=== Step 2: Cleaning up adjustments ===');
Integer total = 0, batch = 200;

// Delete AttributeBasedAdjustment
List<AttributeBasedAdjustment> aba = [SELECT Id FROM AttributeBasedAdjustment WHERE Product.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
while (!aba.isEmpty()) {
    delete aba;
    total += aba.size();
    aba = [SELECT Id FROM AttributeBasedAdjustment WHERE Product.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
}
System.debug('Deleted AttributeBasedAdjustment: ' + total);

// Delete AttributeBasedAdjRule (cascade deletes conditions)
List<AttributeBasedAdjRule> abar = [SELECT Id FROM AttributeBasedAdjRule WHERE Name LIKE '%GEN%' LIMIT :batch];
Integer abarCount = 0;
while (!abar.isEmpty()) {
    delete abar;
    abarCount += abar.size();
    abar = [SELECT Id FROM AttributeBasedAdjRule WHERE Name LIKE '%GEN%' LIMIT :batch];
}
total += abarCount;
System.debug('Deleted AttributeBasedAdjRule: ' + abarCount);

// Delete BundleBasedAdjustment (by Product)
List<BundleBasedAdjustment> bba1 = [SELECT Id FROM BundleBasedAdjustment WHERE Product.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
Integer bbaCount = 0;
while (!bba1.isEmpty()) {
    delete bba1;
    bbaCount += bba1.size();
    bba1 = [SELECT Id FROM BundleBasedAdjustment WHERE Product.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
}
System.debug('Deleted BundleBasedAdjustment (by product): ' + bbaCount);

// Delete BundleBasedAdjustment (by ParentProduct)
List<BundleBasedAdjustment> bba2 = [SELECT Id FROM BundleBasedAdjustment WHERE ParentProduct.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
Integer bba2Count = 0;
while (!bba2.isEmpty()) {
    delete bba2;
    bba2Count += bba2.size();
    bba2 = [SELECT Id FROM BundleBasedAdjustment WHERE ParentProduct.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
}
bbaCount += bba2Count;
System.debug('Deleted BundleBasedAdjustment (by parent): ' + bba2Count);

// Delete BundleBasedAdjustment (by RootBundle)
List<BundleBasedAdjustment> bba3 = [SELECT Id FROM BundleBasedAdjustment WHERE RootBundle.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
Integer bba3Count = 0;
while (!bba3.isEmpty()) {
    delete bba3;
    bba3Count += bba3.size();
    bba3 = [SELECT Id FROM BundleBasedAdjustment WHERE RootBundle.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
}
bbaCount += bba3Count;
total += bbaCount;
System.debug('Deleted BundleBasedAdjustment (by root): ' + bba3Count);
System.debug('Total BundleBasedAdjustment deleted: ' + bbaCount);

// Delete PriceAdjustmentTier
List<PriceAdjustmentTier> pat = [SELECT Id FROM PriceAdjustmentTier WHERE Product2.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
Integer patCount = 0;
while (!pat.isEmpty()) {
    delete pat;
    patCount += pat.size();
    pat = [SELECT Id FROM PriceAdjustmentTier WHERE Product2.StockKeepingUnit LIKE '%GEN%' LIMIT :batch];
}
total += patCount;
System.debug('Deleted PriceAdjustmentTier: ' + patCount);

System.debug('=== Step 2 Complete: ' + total + ' records deleted ===');