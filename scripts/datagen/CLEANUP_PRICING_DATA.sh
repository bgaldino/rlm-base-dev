#!/bin/bash

# Cleanup script for qb-pricing-1000 data only
# This script removes only the pricing data that failed to import
# while preserving the successful product catalog data from qb-pcm-1000

if [ $# -eq 0 ]; then
    echo "Usage: $0 <org-alias>"
    echo "Example: $0 qb-datatest"
    exit 1
fi

ORG_ALIAS=$1

echo "======================================================================="
echo "CLEANING UP qb-pricing-1000 DATA FROM ORG: $ORG_ALIAS"
echo "======================================================================="
echo "This will delete only the pricing data that failed to import"
echo "Product catalog data from qb-pcm-1000 will be preserved"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

echo "Step 1: Deleting failed pricing data..."
sfdx force:apex:execute -f cleanup_pricing_data.apex -u $ORG_ALIAS

echo ""
echo "======================================================================="
echo "✓ PRICING DATA CLEANUP COMPLETE!"
echo "======================================================================="
echo "Product catalog data from qb-pcm-1000 has been preserved."
echo ""
echo "Verify cleanup:"
echo "sfdx data query -q \"SELECT COUNT() FROM PricebookEntry WHERE Name LIKE '%GEN%'\" -o $ORG_ALIAS"
echo "Expected result: Should return 0"
echo ""
echo "Verify product catalog is intact:"
echo "sfdx data query -q \"SELECT COUNT() FROM Product2 WHERE StockKeepingUnit LIKE '%GEN%'\" -o $ORG_ALIAS"
echo "Expected result: Should return 836 (generated products)"
echo "======================================================================="
