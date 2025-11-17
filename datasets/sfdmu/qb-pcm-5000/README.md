# QB-PCM-1000 Dataset

Complete dataset with 1000 products using UPSERT operations.

## Contents
- **Product2**: 5000 products (164 original + 4836 generated)
- **ProductComponentGroup**: 794 rows
- **ProductRelatedComponent**: 2378 rows
- All other relationships scaled proportionally

## Usage - Works on ANY Org

This dataset uses UPSERT operations via external IDs.

### On a Clean Org (no data)
```bash
sfdx sfdmu:run --sourceusername csvfile --path qb-pcm-1000 --targetusername <clean-org>
```
**Result**: Inserts all 1000 products + relationships

### On an Org with qb-pcm Data (164 products)
```bash
sfdx sfdmu:run --sourceusername csvfile --path qb-pcm-1000 --targetusername <org-with-qb-pcm>
```
**Result**: 
- Upserts 164 original products (no change if data matches)
- Inserts 836 new generated products
- **Total: 1000 products**

## How UPSERT Works

SFDMU matches records using external IDs:
- `Product2`: `StockKeepingUnit`
- `ProductComponentGroup`: `Code;ParentProduct.StockKeepingUnit`
- `ProductRelatedComponent`: Complex 5-part compound key
- etc.

When matched → UPDATE (or skip if unchanged)  
When not found → INSERT

## Features
- ✅ Self-contained dataset (all lookups resolved)
- ✅ Works on clean orgs AND orgs with data
- ✅ Idempotent (safe to run multiple times)
- ✅ Proper compound key handling
- ✅ Unique ProductComponentGroup Codes

## Generated Data Patterns
- Product SKU: `ORIGINAL-SKU-GEN####` (e.g., `QB-API-GEN0170`)
- Product Name: `Original Name Gen###` (e.g., `Additional API Gen170`)
- ComponentGroup Code: `ORIGINAL-CODE-GEN####` (e.g., `PCG-QB-SRV-CPU-GEN0181`)
