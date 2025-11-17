// Compact cleanup script - removes ALL generated data
System.debug('Starting cleanup...');
Integer total = 0, batch = 200;

// Helper method
void deleteBatch(String obj, String field, String val) {
    String q = 'SELECT Id FROM ' + obj + ' WHERE ' + field + ' LIKE \'' + val + '%\' LIMIT ' + batch;
    List<SObject> recs = Database.query(q);
    while (!recs.isEmpty()) {
        delete recs;
        total += recs.size();
        System.debug('Deleted ' + recs.size() + ' ' + obj);
        recs = Database.query(q);
    }
}

// Pricing (delete first)
try { deleteBatch('PricebookEntryDerivedPrice', 'PricebookEntry.Name', '%GEN'); } catch(Exception e) {}
try { deleteBatch('PricebookEntry', 'Name', '%GEN'); } catch(Exception e) {}
try { deleteBatch('AttributeBasedAdjustment', 'Product.StockKeepingUnit', '%GEN'); } catch(Exception e) {}
try { deleteBatch('AttributeBasedAdjRule', 'Name', '%GEN'); } catch(Exception e) {}
try { deleteBatch('BundleBasedAdjustment', 'Product.StockKeepingUnit', '%GEN'); } catch(Exception e) {}
try { deleteBatch('PriceAdjustmentTier', 'Product2.StockKeepingUnit', '%GEN'); } catch(Exception e) {}

// Product catalog
try { deleteBatch('ProductRelatedComponent', 'ParentProduct.StockKeepingUnit', '%GEN'); } catch(Exception e) {}
try { deleteBatch('ProductComponentGroup', 'ParentProduct.StockKeepingUnit', '%GEN'); } catch(Exception e) {}
try { deleteBatch('ProductSellingModelOption', 'Product2.StockKeepingUnit', '%GEN'); } catch(Exception e) {}
try { deleteBatch('ProductCategoryProduct', 'Product.StockKeepingUnit', '%GEN'); } catch(Exception e) {}
try { deleteBatch('ProductAttributeDefinition', 'Product2.StockKeepingUnit', '%GEN'); } catch(Exception e) {}
try { deleteBatch('ProductRampSegment', 'Product.StockKeepingUnit', '%GEN'); } catch(Exception e) {}
try { deleteBatch('Product2', 'StockKeepingUnit', '%GEN'); } catch(Exception e) {}

System.debug('====== Cleanup complete! Deleted ' + total + ' records ======');