# Generating 1000-Product Test Datasets

## Overview

These scripts scale the qb-pcm and qb-pricing datasets from 164 products to 1000 products.

## Scripts

### 🎯 GENERATE_ALL.py (Recommended)
Runs both generation scripts in sequence.

```bash
python3 GENERATE_ALL.py
```

**Generates**:
- `qb-pcm-1000/` - Product catalog with 1000 products
- `qb-pricing-1000/` - Pricing data for those products

### 📦 GENERATE_1000.py
Generates product catalog dataset.

```bash
python3 GENERATE_1000.py
```

**Output**: `qb-pcm-1000/` directory with:
- 1000 products (164 original + 836 generated)
- All relationships (ProductComponentGroup, ProductRelatedComponent, etc.)
- All dependencies scaled proportionally

### 💰 GENERATE_PRICING_1000.py  
Generates pricing dataset (requires qb-pcm-1000 to exist first).

```bash
python3 GENERATE_PRICING_1000.py
```

**Output**: `qb-pricing-1000/` directory with:
- PricebookEntry records for all products with pricing
- Price adjustments, tiers, and derived prices
- Scaled from original qb-pricing data

## Import Sequence

After generating datasets:

```bash
# Step 1: Import product catalog
sfdx sfdmu:run --sourceusername csvfile --path qb-pcm-1000 --targetusername <your-org>

# Step 2: Import pricing
sfdx sfdmu:run --sourceusername csvfile --path qb-pricing-1000 --targetusername <your-org>
```

## UPSERT Behavior

Both datasets use UPSERT operations, so they work on:
- ✅ **Clean orgs** (no existing data) - Inserts all records
- ✅ **Orgs with existing qb-pcm/qb-pricing data** - Upserts originals, inserts new

The datasets are **idempotent** - safe to run multiple times.

## How It Works

### Product Generation
1. Keeps all 164 original products unchanged
2. Generates 836 new products by cloning templates
3. Naming: `ORIGINAL-SKU-GEN####` (e.g., `QB-API-GEN0170`)

### Relationship Scaling
For each generated product, duplicates all relationships from its template:
- ProductComponentGroup (with unique Code: `PCG-QB-SRV-CPU-GEN0181`)
- ProductRelatedComponent (updates compound keys)
- ProductSellingModelOption
- ProductCategoryProduct
- ProductAttributeDefinition
- etc.

### Pricing Scaling
Only creates pricing for products whose template has pricing:
- Template `QB-API` has pricing → `QB-API-GEN0170` gets pricing
- Template `QB-CPU-HEATSINK` has no pricing → `QB-CPU-HEATSINK-GEN0500` gets no pricing

## Key Features

### ✅ Compound Key Handling
- ProductComponentGroup: `Code;ParentProduct.StockKeepingUnit`
- ProductRelatedComponent: 5-part compound key
- PricebookEntry: `Name;Pricebook2.Name;Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode`
- All compound keys properly updated with SKU changes

### ✅ Unique Constraints
- ProductComponentGroup.Code made unique with `-GEN####` suffix
- Product2.StockKeepingUnit already unique by design

### ✅ Hierarchical References
- ProductComponentGroup.ParentGroup updated to reference generated parent groups
- BundleBasedAdjustment handles Product/ParentProduct/RootBundle references

### ✅ Static Metadata Preserved
- AttributeDefinition, ProductSellingModel, CurrencyType, etc. not scaled
- ProductAttributeDefinition references preserved (doesn't add -GEN to metadata)

## Troubleshooting

### MissingParentRecordsReport.csv shows errors
- Verify target org has all reference data (Pricebook2, CurrencyType, etc.)
- Check compound keys in generated CSVs match expected format
- Ensure qb-pcm-1000 was imported before qb-pricing-1000

### "Duplicate value found" errors
- This means org has partial data from previous runs
- Solution: Use fresh org OR delete generated data first

### "Child product exists in group" errors
- Indicates duplicate ProductRelatedComponent records
- Should not occur with fresh org + FULL dataset

## Documentation

See also:
- `COMPOUND_KEY_ANALYSIS.md` - Analysis of all compound keys
- `TRACE_EXAMPLE.md` - Detailed walkthrough of data generation
- `VERIFICATION_SUMMARY.md` - Verification methodology

