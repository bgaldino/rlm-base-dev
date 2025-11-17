#!/bin/bash
# Cleanup script to remove all generated test data (records with -GEN pattern)
# This allows you to start fresh with a clean org

ORG_ALIAS="$1"

if [ -z "$ORG_ALIAS" ]; then
    echo "Usage: ./CLEANUP_GENERATED_DATA.sh <org-alias>"
    echo "Example: ./CLEANUP_GENERATED_DATA.sh qb-datatest"
    exit 1
fi

echo "======================================================================="
echo "CLEANING UP GENERATED DATA FROM ORG: $ORG_ALIAS"
echo "======================================================================="
echo ""
echo "This will delete all records with -GEN in the name/SKU"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

echo ""
echo "Step 1: Deleting PricebookEntryDerivedPrice..."
sfdx data delete record -s PricebookEntryDerivedPrice \
  -w "PricebookEntry.Name LIKE '%GEN%'" \
  -o "$ORG_ALIAS" 2>/dev/null || echo "  (No records or already deleted)"

echo ""
echo "Step 2: Deleting AttributeBasedAdjustment..."
sfdx data delete record -s AttributeBasedAdjustment \
  -w "Product.StockKeepingUnit LIKE '%GEN%'" \
  -o "$ORG_ALIAS" 2>/dev/null || echo "  (No records or already deleted)"

echo ""
echo "Step 3: Deleting AttributeAdjustmentCondition..."
sfdx data delete record -s AttributeAdjustmentCondition \
  -w "Product.StockKeepingUnit LIKE '%GEN%'" \
  -o "$ORG_ALIAS" 2>/dev/null || echo "  (No records or already deleted)"

echo ""
echo "Step 4: Deleting AttributeBasedAdjRule (generated)..."
sfdx data delete record -s AttributeBasedAdjRule \
  -w "Name LIKE '%GEN%'" \
  -o "$ORG_ALIAS" 2>/dev/null || echo "  (No records or already deleted)"

echo ""
echo "Step 5: Deleting BundleBasedAdjustment..."
sfdx data delete record -s BundleBasedAdjustment \
  -w "Product.StockKeepingUnit LIKE '%GEN%' OR ParentProduct.StockKeepingUnit LIKE '%GEN%' OR RootBundle.StockKeepingUnit LIKE '%GEN%'" \
  -o "$ORG_ALIAS" 2>/dev/null || echo "  (No records or already deleted)"

echo ""
echo "Step 6: Deleting PriceAdjustmentTier..."
sfdx data delete record -s PriceAdjustmentTier \
  -w "Product2.StockKeepingUnit LIKE '%GEN%'" \
  -o "$ORG_ALIAS" 2>/dev/null || echo "  (No records or already deleted)"

echo ""
echo "Step 7: Deleting PricebookEntry..."
sfdx data delete record -s PricebookEntry \
  -w "Name LIKE '%GEN%'" \
  -o "$ORG_ALIAS" 2>/dev/null || echo "  (No records or already deleted)"

echo ""
echo "Step 8: Deleting ProductRelatedComponent..."
sfdx data delete record -s ProductRelatedComponent \
  -w "ChildProduct.StockKeepingUnit LIKE '%GEN%' OR ParentProduct.StockKeepingUnit LIKE '%GEN%'" \
  -o "$ORG_ALIAS" 2>/dev/null || echo "  (No records or already deleted)"

echo ""
echo "Step 9: Deleting ProductComponentGroup..."
sfdx data delete record -s ProductComponentGroup \
  -w "Code LIKE '%GEN%'" \
  -o "$ORG_ALIAS" 2>/dev/null || echo "  (No records or already deleted)"

echo ""
echo "Step 10: Deleting ProductSellingModelOption..."
sfdx data delete record -s ProductSellingModelOption \
  -w "Product2.StockKeepingUnit LIKE '%GEN%'" \
  -o "$ORG_ALIAS" 2>/dev/null || echo "  (No records or already deleted)"

echo ""
echo "Step 11: Deleting ProductCategoryProduct..."
sfdx data delete record -s ProductCategoryProduct \
  -w "Product.StockKeepingUnit LIKE '%GEN%'" \
  -o "$ORG_ALIAS" 2>/dev/null || echo "  (No records or already deleted)"

echo ""
echo "Step 12: Deleting ProductAttributeDefinition..."
sfdx data delete record -s ProductAttributeDefinition \
  -w "Product2.StockKeepingUnit LIKE '%GEN%'" \
  -o "$ORG_ALIAS" 2>/dev/null || echo "  (No records or already deleted)"

echo ""
echo "Step 13: Deleting ProductRampSegment..."
sfdx data delete record -s ProductRampSegment \
  -w "Product.StockKeepingUnit LIKE '%GEN%'" \
  -o "$ORG_ALIAS" 2>/dev/null || echo "  (No records or already deleted)"

echo ""
echo "Step 14: Deleting Product2 (generated products)..."
sfdx data delete record -s Product2 \
  -w "StockKeepingUnit LIKE '%GEN%'" \
  -o "$ORG_ALIAS" 2>/dev/null || echo "  (No records or already deleted)"

echo ""
echo "======================================================================="
echo "✓ CLEANUP COMPLETE!"
echo "======================================================================="
echo ""
echo "Verify cleanup:"
echo "  sfdx data query -q \"SELECT COUNT() FROM Product2 WHERE StockKeepingUnit LIKE '%GEN%'\" -o $ORG_ALIAS"
echo "  sfdx data query -q \"SELECT COUNT() FROM PricebookEntry WHERE Name LIKE '%GEN%'\" -o $ORG_ALIAS"
echo ""
echo "Expected result: Both should return 0"
echo "======================================================================="

