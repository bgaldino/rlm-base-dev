// Cleanup script for qb-pricing-1000 data only
// This script removes only the pricing data that failed to import
// while preserving the successful product catalog data from qb-pcm-1000

System.debug('Starting cleanup of qb-pricing-1000 data...');
Integer totalDeleted = 0;

// Delete in reverse dependency order (children first, then parents)
// NOTE: Some objects have cascade delete behavior, so we delete parents to clean up children

// 1. Delete PricebookEntryDerivedPrice
try {
    List<PricebookEntryDerivedPrice> pbepd = [SELECT Id FROM PricebookEntryDerivedPrice WHERE PricebookEntry.Name LIKE '%GEN%'];
    if (!pbepd.isEmpty()) {
        delete pbepd;
        totalDeleted += pbepd.size();
        System.debug('✓ Deleted ' + pbepd.size() + ' PricebookEntryDerivedPrice records');
    } else {
        System.debug('No PricebookEntryDerivedPrice records to delete');
    }
} catch (Exception e) {
    System.debug('✗ Error with PricebookEntryDerivedPrice: ' + e.getMessage());
}

// 2. Delete PricebookEntry (this must be done before we can delete some adjustments)
try {
    List<PricebookEntry> pbes = [SELECT Id FROM PricebookEntry WHERE Name LIKE '%GEN%'];
    if (!pbes.isEmpty()) {
        delete pbes;
        totalDeleted += pbes.size();
        System.debug('✓ Deleted ' + pbes.size() + ' PricebookEntry records');
    } else {
        System.debug('No PricebookEntry records to delete');
    }
} catch (Exception e) {
    System.debug('✗ Error with PricebookEntry: ' + e.getMessage());
}

// 3. Delete AttributeBasedAdjustment
try {
    List<AttributeBasedAdjustment> abas = [SELECT Id FROM AttributeBasedAdjustment WHERE ProductId IN (SELECT Id FROM Product2 WHERE StockKeepingUnit LIKE '%GEN%')];
    if (!abas.isEmpty()) {
        delete abas;
        totalDeleted += abas.size();
        System.debug('✓ Deleted ' + abas.size() + ' AttributeBasedAdjustment records');
    } else {
        System.debug('No AttributeBasedAdjustment records to delete');
    }
} catch (Exception e) {
    System.debug('✗ Error with AttributeBasedAdjustment: ' + e.getMessage());
}

// 4. Delete AttributeBasedAdjRule (this should cascade delete AttributeAdjustmentCondition)
try {
    List<AttributeBasedAdjRule> abars = [SELECT Id FROM AttributeBasedAdjRule WHERE Name LIKE '%GEN%'];
    if (!abars.isEmpty()) {
        delete abars;
        totalDeleted += abars.size();
        System.debug('✓ Deleted ' + abars.size() + ' AttributeBasedAdjRule records (cascade deletes conditions)');
    } else {
        System.debug('No AttributeBasedAdjRule records to delete');
    }
} catch (Exception e) {
    System.debug('✗ Error with AttributeBasedAdjRule: ' + e.getMessage());
}

// 5. Delete BundleBasedAdjustment
try {
    List<BundleBasedAdjustment> bbas = [SELECT Id FROM BundleBasedAdjustment WHERE ProductId IN (SELECT Id FROM Product2 WHERE StockKeepingUnit LIKE '%GEN%')];
    if (!bbas.isEmpty()) {
        delete bbas;
        totalDeleted += bbas.size();
        System.debug('✓ Deleted ' + bbas.size() + ' BundleBasedAdjustment records');
    } else {
        System.debug('No BundleBasedAdjustment records to delete');
    }
} catch (Exception e) {
    System.debug('✗ Error with BundleBasedAdjustment: ' + e.getMessage());
}

// 6. Delete PriceAdjustmentTier
try {
    List<PriceAdjustmentTier> pats = [SELECT Id FROM PriceAdjustmentTier WHERE Product2Id IN (SELECT Id FROM Product2 WHERE StockKeepingUnit LIKE '%GEN%')];
    if (!pats.isEmpty()) {
        delete pats;
        totalDeleted += pats.size();
        System.debug('✓ Deleted ' + pats.size() + ' PriceAdjustmentTier records');
    } else {
        System.debug('No PriceAdjustmentTier records to delete');
    }
} catch (Exception e) {
    System.debug('✗ Error with PriceAdjustmentTier: ' + e.getMessage());
}

// 7. Verify cleanup - check if any AttributeAdjustmentCondition records remain
try {
    Integer conditionCount = [SELECT COUNT() FROM AttributeAdjustmentCondition WHERE ProductId IN (SELECT Id FROM Product2 WHERE StockKeepingUnit LIKE '%GEN%')];
    if (conditionCount > 0) {
        System.debug('⚠ Warning: ' + conditionCount + ' AttributeAdjustmentCondition records remain (cascade delete may not have worked)');
    } else {
        System.debug('✓ AttributeAdjustmentCondition records cleaned up via cascade delete');
    }
} catch (Exception e) {
    System.debug('Could not verify AttributeAdjustmentCondition cleanup: ' + e.getMessage());
}

System.debug('======================================================================');
System.debug('Cleanup completed! Total records deleted: ' + totalDeleted);
System.debug('Product catalog data from qb-pcm-1000 has been preserved.');
System.debug('======================================================================');