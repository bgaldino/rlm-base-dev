#!/usr/bin/env python3
"""
Generate test dataset with 1000 products using UPSERT operations.
Works on clean orgs OR orgs with existing qb-pcm data.

Usage: python3 GENERATE_1000.py
"""

import csv
import shutil
from pathlib import Path

# Configuration
TARGET_PRODUCTS = 5000
SRC = Path(__file__).parent / "qb-pcm"
DST = Path(__file__).parent / f"qb-pcm-{TARGET_PRODUCTS}"

def read_csv(filename):
    """Read CSV file from source directory."""
    filepath = SRC / filename
    if not filepath.exists() or filepath.stat().st_size == 0:
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_csv(filename, rows, dest_dir):
    """Write CSV file to destination directory."""
    if not rows:
        # Copy empty file as-is
        src_file = SRC / filename
        if src_file.exists():
            dest_dir.mkdir(exist_ok=True)
            shutil.copy2(src_file, dest_dir / filename)
        return
    
    dest_dir.mkdir(exist_ok=True)
    with open(dest_dir / filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def copy_static_files(dest_dir):
    """Copy static reference files to destination."""
    static_files = [
        'AttributePicklist.csv', 'AttributePicklistValue.csv', 'UnitOfMeasureClass.csv',
        'UnitOfMeasure.csv', 'AttributeDefinition.csv', 'AttributeCategory.csv',
        'AttributeCategoryAttribute.csv', 'ProductClassification.csv', 'ProductClassificationAttr.csv',
        'ProductSellingModel.csv', 'ProrationPolicy.csv', 'ProductRelationshipType.csv',
        'ProductCatalog.csv', 'ProductCategory.csv', 'ProdtAttrScope.csv',
        'MissingParentRecordsReport.csv', 'ProductCategoryDisqual.csv',
        'ProductCategoryQualification.csv', 'ProductDisqualification.csv',
        'ProductQualification.csv', 'ProductRelComponentOverride.csv',
        'ProductComponentGrpOverride.csv', 'export.json',
    ]
    
    dest_dir.mkdir(exist_ok=True)
    for filename in static_files:
        src_file = SRC / filename
        if src_file.exists():
            shutil.copy2(src_file, dest_dir / filename)

def replace_sku(value, old_sku, new_sku):
    """Replace SKU in a value (handles compound keys)."""
    if isinstance(value, str) and old_sku and old_sku in value:
        return value.replace(old_sku, new_sku)
    return value

def update_row(row, old_sku, new_sku):
    """Update all SKU references in a row."""
    return {key: replace_sku(val, old_sku, new_sku) for key, val in row.items()}

def main():
    print("="*70)
    print("GENERATING 1000-PRODUCT DATASET (UPSERT MODE)")
    print("="*70)
    print(f"Source: {SRC}")
    print(f"Output: {DST}")
    print()
    
    # STEP 1: Scale Product2
    print("STEP 1: Scaling Product2.csv...")
    orig_products = read_csv('Product2.csv')
    needed = TARGET_PRODUCTS - len(orig_products)
    
    print(f"  Original products: {len(orig_products)}")
    print(f"  Generating: {needed} new products")
    
    # Generate new products
    new_products = []
    sku_mapping = {}
    
    for i in range(needed):
        template_idx = i % len(orig_products)
        template = orig_products[template_idx]
        new_product = template.copy()
        
        old_sku = template['StockKeepingUnit']
        new_sku = f"{old_sku}-GEN{len(orig_products) + i:04d}"
        
        new_product['StockKeepingUnit'] = new_sku
        if new_product.get('Name'):
            new_product['Name'] += f" Gen{len(orig_products) + i}"
        if new_product.get('ProductCode'):
            new_product['ProductCode'] += f"-GEN{len(orig_products) + i:04d}"
        
        new_products.append(new_product)
        sku_mapping[new_sku] = old_sku
    
    # Write complete dataset (original + new)
    all_products = [p.copy() for p in orig_products] + new_products
    write_csv('Product2.csv', all_products, DST)
    print(f"  ✓ {len(all_products)} total ({len(orig_products)} original + {len(new_products)} new)")
    
    # STEP 2: Scale ProductComponentGroup
    print()
    print("STEP 2: Scaling ProductComponentGroup.csv...")
    print("  (Updating Code field + ParentGroup hierarchical refs)")
    orig_pcg = read_csv('ProductComponentGroup.csv')
    new_pcg = []
    
    for new_sku, old_sku in sku_mapping.items():
        sku_parts = new_sku.split('-GEN')
        suffix = f"-GEN{sku_parts[1]}" if len(sku_parts) == 2 else ""
        
        for row in orig_pcg:
            if row.get('ParentProduct.StockKeepingUnit') == old_sku:
                new_row = update_row(row, old_sku, new_sku)
                
                # Update Code (unique constraint)
                old_code = row.get('Code', '')
                if old_code and suffix:
                    new_code = old_code + suffix
                    new_row['Code'] = new_code
                    if '$$Code$ParentProduct.StockKeepingUnit' in new_row:
                        new_row['$$Code$ParentProduct.StockKeepingUnit'] = f"{new_code};{new_sku}"
                
                # Update ParentGroup references (hierarchical)
                parent_group_field = 'ParentGroup.$$Code$ParentProduct.StockKeepingUnit'
                if parent_group_field in new_row and new_row[parent_group_field] and suffix:
                    pg_value = new_row[parent_group_field]
                    pg_parts = pg_value.split(';')
                    if len(pg_parts) == 2:
                        parent_code = pg_parts[0]
                        if not parent_code.endswith(suffix):
                            new_row[parent_group_field] = f"{parent_code}{suffix};{pg_parts[1]}"
                
                new_pcg.append(new_row)
    
    # Write complete dataset
    all_pcg = [r.copy() for r in orig_pcg] + new_pcg
    write_csv('ProductComponentGroup.csv', all_pcg, DST)
    print(f"  ✓ {len(all_pcg)} total ({len(orig_pcg)} original + {len(new_pcg)} new)")
    
    # STEP 3: Scale relationship files
    print()
    print("STEP 3: Scaling relationship files...")
    
    # ProductSellingModelOption
    print("  ProductSellingModelOption.csv...")
    orig = read_csv('ProductSellingModelOption.csv')
    new_rows = []
    for new_sku, old_sku in sku_mapping.items():
        for row in orig:
            if row.get('Product2.StockKeepingUnit') == old_sku:
                new_rows.append(update_row(row, old_sku, new_sku))
    write_csv('ProductSellingModelOption.csv', [r.copy() for r in orig] + new_rows, DST)
    print(f"    {len(orig) + len(new_rows)} total ({len(orig)} original + {len(new_rows)} new)")
    
    # ProductCategoryProduct
    print("  ProductCategoryProduct.csv...")
    orig = read_csv('ProductCategoryProduct.csv')
    new_rows = []
    for new_sku, old_sku in sku_mapping.items():
        for row in orig:
            if row.get('Product.StockKeepingUnit') == old_sku:
                new_rows.append(update_row(row, old_sku, new_sku))
    write_csv('ProductCategoryProduct.csv', [r.copy() for r in orig] + new_rows, DST)
    print(f"    {len(orig) + len(new_rows)} total ({len(orig)} original + {len(new_rows)} new)")
    
    # ProductRampSegment
    print("  ProductRampSegment.csv...")
    orig = read_csv('ProductRampSegment.csv')
    new_rows = []
    for new_sku, old_sku in sku_mapping.items():
        for row in orig:
            if row.get('Product.StockKeepingUnit') == old_sku:
                new_rows.append(update_row(row, old_sku, new_sku))
    write_csv('ProductRampSegment.csv', [r.copy() for r in orig] + new_rows, DST)
    print(f"    {len(orig) + len(new_rows)} total ({len(orig)} original + {len(new_rows)} new)")
    
    # ProductAttributeDefinition (special - don't update metadata refs)
    print("  ProductAttributeDefinition.csv...")
    orig = read_csv('ProductAttributeDefinition.csv')
    new_rows = []
    for new_sku, old_sku in sku_mapping.items():
        for row in orig:
            if row.get('Product2.StockKeepingUnit') == old_sku:
                new_row = row.copy()
                # Only update Product2 SKU, not metadata references
                new_row['Product2.StockKeepingUnit'] = new_sku
                ext_id_field = '$$AttributeDefinition.Code$Product2.StockKeepingUnit'
                if ext_id_field in new_row and new_row[ext_id_field]:
                    parts = new_row[ext_id_field].split(';')
                    if len(parts) == 2:
                        new_row[ext_id_field] = f"{parts[0]};{new_sku}"
                new_rows.append(new_row)
    write_csv('ProductAttributeDefinition.csv', [r.copy() for r in orig] + new_rows, DST)
    print(f"    {len(orig) + len(new_rows)} total ({len(orig)} original + {len(new_rows)} new)")
    
    # STEP 4: Scale ProductRelatedComponent
    print()
    print("STEP 4: Scaling ProductRelatedComponent.csv...")
    print("  (Only cloning relationships for generated parent products)")
    orig_prc = read_csv('ProductRelatedComponent.csv')
    new_prc = []
    parent_count = 0
    
    for new_sku, old_sku in sku_mapping.items():
        sku_parts = new_sku.split('-GEN')
        suffix = f"-GEN{sku_parts[1]}" if len(sku_parts) == 2 else ""
        
        for row in orig_prc:
            # ONLY clone when parent product is being generated
            # This ensures original products keep their original relationships
            is_parent = row.get('ParentProduct.StockKeepingUnit') == old_sku
            
            if is_parent:
                new_row = update_row(row, old_sku, new_sku)
                
                # Update ProductComponentGroup Code for generated parent
                if suffix:
                    pcg_field = 'ProductComponentGroup.$$Code$ParentProduct.StockKeepingUnit'
                    if pcg_field in new_row and new_row[pcg_field]:
                        pcg_value = new_row[pcg_field]
                        pcg_parts = pcg_value.split(';')
                        if len(pcg_parts) == 2:
                            old_code = pcg_parts[0]
                            if not old_code.endswith(suffix):
                                new_row[pcg_field] = f"{old_code}{suffix};{pcg_parts[1]}"
                
                new_prc.append(new_row)
                parent_count += 1
    
    # Write complete dataset
    all_prc = [r.copy() for r in orig_prc] + new_prc
    write_csv('ProductRelatedComponent.csv', all_prc, DST)
    print(f"  ✓ {len(all_prc)} total ({len(orig_prc)} original + {len(new_prc)} new)")
    print(f"    - Cloned relationships for {parent_count} generated parent products")
    
    # STEP 5: Copy static files
    print()
    print("STEP 5: Copying static reference files...")
    copy_static_files(DST)
    print(f"  ✓ Copied static reference files")
    
    # STEP 6: Create README
    print()
    print("STEP 6: Creating README...")
    
    readme = f"""# QB-PCM-1000 Dataset

Complete dataset with 1000 products using UPSERT operations.

## Contents
- **Product2**: {len(all_products)} products (164 original + {len(new_products)} generated)
- **ProductComponentGroup**: {len(all_pcg)} rows
- **ProductRelatedComponent**: {len(all_prc)} rows
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
"""
    
    with open(DST / 'README.md', 'w') as f:
        f.write(readme)
    
    print(f"  ✓ Created README.md")
    
    print()
    print("="*70)
    print("✓ COMPLETE!")
    print("="*70)
    print(f"Dataset: {DST}")
    print(f"Products: {len(all_products)} (164 original + {len(new_products)} new)")
    print()
    print("To import:")
    print(f"  sfdx sfdmu:run --sourceusername csvfile --path qb-pcm-1000 --targetusername <your-org>")
    print()
    print("Works on clean orgs OR orgs with existing qb-pcm data!")
    print("="*70)

if __name__ == '__main__':
    main()

