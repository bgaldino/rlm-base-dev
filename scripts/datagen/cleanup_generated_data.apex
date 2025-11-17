// Apex script to delete all generated test data (records with -GEN pattern)
// Execute via: sfdx apex run -f cleanup_generated_data.apex -o <your-org>

System.debug('Starting cleanup of generated data...');

// Step 1: Delete PricebookEntryDerivedPrice
List<PricebookEntryDerivedPrice> derivedPrices = [
    SELECT Id FROM PricebookEntryDerivedPrice 
    WHERE PricebookEntry.Name LIKE '%GEN%'
];
if (!derivedPrices.isEmpty()) {
    delete derivedPrices;
    System.debug('Deleted ' + derivedPrices.size() + ' PricebookEntryDerivedPrice records');
}

// Step 2: Delete AttributeBasedAdjustment  
List<AttributeBasedAdjustment> attrAdj = [
    SELECT Id FROM AttributeBasedAdjustment 
    WHERE Product.StockKeepingUnit LIKE '%GEN%'
];
if (!attrAdj.isEmpty()) {
    delete attrAdj;
    System.debug('Deleted ' + attrAdj.size() + ' AttributeBasedAdjustment records');
}

// Step 3: Delete AttributeAdjustmentCondition
List<AttributeAdjustmentCondition> attrCond = [
    SELECT Id FROM AttributeAdjustmentCondition 
    WHERE Product.StockKeepingUnit LIKE '%GEN%'
];
if (!attrCond.isEmpty()) {
    delete attrCond;
    System.debug('Deleted ' + attrCond.size() + ' AttributeAdjustmentCondition records');
}

// Step 4: Delete AttributeBasedAdjRule (generated)
List<AttributeBasedAdjRule> adjRules = [
    SELECT Id FROM AttributeBasedAdjRule 
    WHERE Name LIKE '%GEN%'
];
if (!adjRules.isEmpty()) {
    delete adjRules;
    System.debug('Deleted ' + adjRules.size() + ' AttributeBasedAdjRule records');
}

// Step 5: Delete BundleBasedAdjustment
List<BundleBasedAdjustment> bundleAdj = [
    SELECT Id FROM BundleBasedAdjustment 
    WHERE Product.StockKeepingUnit LIKE '%GEN%' 
       OR ParentProduct.StockKeepingUnit LIKE '%GEN%' 
       OR RootBundle.StockKeepingUnit LIKE '%GEN%'
];
if (!bundleAdj.isEmpty()) {
    delete bundleAdj;
    System.debug('Deleted ' + bundleAdj.size() + ' BundleBasedAdjustment records');
}

// Step 6: Delete PriceAdjustmentTier
List<PriceAdjustmentTier> tiers = [
    SELECT Id FROM PriceAdjustmentTier 
    WHERE Product2.StockKeepingUnit LIKE '%GEN%'
];
if (!tiers.isEmpty()) {
    delete tiers;
    System.debug('Deleted ' + tiers.size() + ' PriceAdjustmentTier records');
}

// Step 7: Delete PricebookEntry
List<PricebookEntry> entries = [
    SELECT Id FROM PricebookEntry 
    WHERE Name LIKE '%GEN%'
];
if (!entries.isEmpty()) {
    delete entries;
    System.debug('Deleted ' + entries.size() + ' PricebookEntry records');
}

// Step 8: Delete ProductRelatedComponent
List<ProductRelatedComponent> relComps = [
    SELECT Id FROM ProductRelatedComponent 
    WHERE ChildProduct.StockKeepingUnit LIKE '%GEN%' 
       OR ParentProduct.StockKeepingUnit LIKE '%GEN%'
];
if (!relComps.isEmpty()) {
    delete relComps;
    System.debug('Deleted ' + relComps.size() + ' ProductRelatedComponent records');
}

// Step 9: Delete ProductComponentGroup
List<ProductComponentGroup> compGroups = [
    SELECT Id FROM ProductComponentGroup 
    WHERE Code LIKE '%GEN%'
];
if (!compGroups.isEmpty()) {
    delete compGroups;
    System.debug('Deleted ' + compGroups.size() + ' ProductComponentGroup records');
}

// Step 10: Delete ProductSellingModelOption
List<ProductSellingModelOption> sellingOptions = [
    SELECT Id FROM ProductSellingModelOption 
    WHERE Product2.StockKeepingUnit LIKE '%GEN%'
];
if (!sellingOptions.isEmpty()) {
    delete sellingOptions;
    System.debug('Deleted ' + sellingOptions.size() + ' ProductSellingModelOption records');
}

// Step 11: Delete ProductCategoryProduct
List<ProductCategoryProduct> catProds = [
    SELECT Id FROM ProductCategoryProduct 
    WHERE Product.StockKeepingUnit LIKE '%GEN%'
];
if (!catProds.isEmpty()) {
    delete catProds;
    System.debug('Deleted ' + catProds.size() + ' ProductCategoryProduct records');
}

// Step 12: Delete ProductAttributeDefinition
List<ProductAttributeDefinition> prodAttrs = [
    SELECT Id FROM ProductAttributeDefinition 
    WHERE Product2.StockKeepingUnit LIKE '%GEN%'
];
if (!prodAttrs.isEmpty()) {
    delete prodAttrs;
    System.debug('Deleted ' + prodAttrs.size() + ' ProductAttributeDefinition records');
}

// Step 13: Delete ProductRampSegment
List<ProductRampSegment> rampSegs = [
    SELECT Id FROM ProductRampSegment 
    WHERE Product.StockKeepingUnit LIKE '%GEN%'
];
if (!rampSegs.isEmpty()) {
    delete rampSegs;
    System.debug('Deleted ' + rampSegs.size() + ' ProductRampSegment records');
}

// Step 14: Delete Product2 (generated products)
List<Product2> products = [
    SELECT Id FROM Product2 
    WHERE StockKeepingUnit LIKE '%GEN%'
];
if (!products.isEmpty()) {
    delete products;
    System.debug('Deleted ' + products.size() + ' Product2 records');
}

System.debug('✓ Cleanup complete!');

// Verify
Integer prodCount = [SELECT COUNT() FROM Product2 WHERE StockKeepingUnit LIKE '%GEN%'];
Integer priceCount = [SELECT COUNT() FROM PricebookEntry WHERE Name LIKE '%GEN%'];

System.debug('Verification:');
System.debug('  Products with -GEN: ' + prodCount + ' (should be 0)');
System.debug('  PricebookEntries with GEN: ' + priceCount + ' (should be 0)');

if (prodCount == 0 && priceCount == 0) {
    System.debug('✓ All generated data successfully removed!');
} else {
    System.debug('⚠️ Warning: Some generated data may still exist');
}

