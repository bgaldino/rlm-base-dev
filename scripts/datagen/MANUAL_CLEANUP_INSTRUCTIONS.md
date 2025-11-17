# Manual Cleanup Instructions for qb-pricing-1000 Data

The automated cleanup script is encountering CLI permissions issues. Here's how to manually clean up the pricing data while preserving your product catalog:

## Option 1: Developer Console (Recommended)

1. **Open Developer Console** in your `qb-datatest` org
2. **Click**: Debug → Open Execute Anonymous Window
3. **Paste** the following code:

```apex
// Cleanup script for qb-pricing-1000 data only
System.debug('Starting cleanup of qb-pricing-1000 data...');
Integer totalDeleted = 0;

// Delete in reverse dependency order (children first, then parents)
// NOTE: AttributeAdjustmentCondition cannot be deleted directly - it's cascade deleted via AttributeBasedAdjRule

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

// 2. Delete PricebookEntry (do this early to unlock other records)
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

// 4. Delete AttributeBasedAdjRule (this cascade deletes AttributeAdjustmentCondition)
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

// 7. Verify cleanup
try {
    Integer conditionCount = [SELECT COUNT() FROM AttributeAdjustmentCondition WHERE ProductId IN (SELECT Id FROM Product2 WHERE StockKeepingUnit LIKE '%GEN%')];
    if (conditionCount > 0) {
        System.debug('⚠ Warning: ' + conditionCount + ' AttributeAdjustmentCondition records remain');
    } else {
        System.debug('✓ AttributeAdjustmentCondition records cleaned up via cascade delete');
    }
} catch (Exception e) {
    System.debug('Could not verify AttributeAdjustmentCondition: ' + e.getMessage());
}

System.debug('======================================================================');
System.debug('Cleanup completed! Total records deleted: ' + totalDeleted);
System.debug('Product catalog data from qb-pcm-1000 has been preserved.');
System.debug('======================================================================');
```

4. **Check**: "Open Log"
5. **Click**: Execute
6. **Review** the log output to see what was deleted

## Option 2: Fix CLI Permissions

If you want to fix the CLI permissions issue:

```bash
# Fix log file permissions
sudo chmod 666 /Users/bgaldino/.sf/sf-2025-10-22.log

# Or delete the log file
rm /Users/bgaldino/.sf/sf-2025-10-22.log
```

Then retry:
```bash
./CLEANUP_PRICING_DATA.sh qb-datatest
```

## Verify Cleanup

After running the cleanup, verify:

```bash
# Should return 0 (pricing data cleaned)
sfdx data query -q "SELECT COUNT() FROM PricebookEntry WHERE Name LIKE '%GEN%'" -o qb-datatest

# Should return 836 (product catalog intact)
sfdx data query -q "SELECT COUNT() FROM Product2 WHERE StockKeepingUnit LIKE '%GEN%'" -o qb-datatest
```

## Then Retry Pricing Import

```bash
cd /Users/bgaldino/Documents/GitHub/bgaldino/_bgaldino/rlm-base-dev/datasets/sfdmu
sfdx sfdmu:run --sourceusername csvfile --path qb-pricing-1000 -o qb-datatest
```
