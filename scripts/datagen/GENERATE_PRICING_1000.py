#!/usr/bin/env python3
"""
Generate pricing dataset for 1000 products based on qb-pcm-1000 products.
This script reads the qb-pcm-1000 products and creates matching pricing data.

Prerequisites:
- qb-pcm-1000 dataset must exist (run GENERATE_1000.py first)
- qb-pricing original dataset must exist

Usage: python3 GENERATE_PRICING_1000.py
"""

import csv
import shutil
from pathlib import Path

# Configuration
TARGET_PRODUCTS = 5000
PCM_SOURCE = Path(__file__).parent / "qb-pcm"
PCM_SCALED = Path(__file__).parent / f"qb-pcm-{TARGET_PRODUCTS}"
PRICING_SOURCE = Path(__file__).parent / "qb-pricing"
PRICING_DEST = Path(__file__).parent / f"qb-pricing-{TARGET_PRODUCTS}"

def read_csv(filepath):
    """Read CSV file."""
    if not filepath.exists() or filepath.stat().st_size == 0:
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_csv(filepath, rows):
    """Write CSV file."""
    if not rows:
        return
    
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

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
    print(f"GENERATING PRICING DATASET FOR {TARGET_PRODUCTS} PRODUCTS")
    print("="*70)
    print(f"PCM Source: {PCM_SOURCE}")
    print(f"PCM Scaled: {PCM_SCALED}")
    print(f"Pricing Source: {PRICING_SOURCE}")
    print(f"Pricing Output: {PRICING_DEST}")
    print()
    
    # Verify scaled PCM dataset exists
    if not PCM_SCALED.exists():
        print(f"❌ ERROR: {PCM_SCALED.name} directory not found!")
        print(f"   Please run GENERATE_1000.py first to create {PCM_SCALED.name} dataset")
        return
    
    # STEP 1: Build product mapping
    print("STEP 1: Building product mapping...")
    print(f"  Reading {PCM_SCALED.name} products...")
    
    pcm_scaled_products = read_csv(PCM_SCALED / 'Product2.csv')
    print(f"  Found {len(pcm_scaled_products)} products in {PCM_SCALED.name}")
    
    # Build mapping of generated SKUs to template SKUs
    sku_mapping = {}
    for product in pcm_scaled_products:
        sku = product.get('StockKeepingUnit', '')
        if '-GEN' in sku:
            # Extract template SKU
            parts = sku.split('-GEN')
            template_sku = parts[0]
            sku_mapping[sku] = template_sku
    
    print(f"  Found {len(sku_mapping)} generated products")
    
    # Get products that have pricing
    pricing_products = read_csv(PRICING_SOURCE / 'Product2.csv')
    products_with_pricing = {p['StockKeepingUnit'] for p in pricing_products}
    print(f"  {len(products_with_pricing)} original products have pricing")
    
    # STEP 2: Create Product2.csv reference list
    print()
    print("STEP 2: Creating Product2.csv reference...")
    
    # Include all products from scaled PCM that have pricing (original or generated from priced template)
    pricing_scaled_skus = []
    for product in pcm_scaled_products:
        sku = product['StockKeepingUnit']
        if sku in products_with_pricing:
            # Original product with pricing
            pricing_scaled_skus.append({'StockKeepingUnit': sku})
        elif sku in sku_mapping and sku_mapping[sku] in products_with_pricing:
            # Generated product whose template has pricing
            pricing_scaled_skus.append({'StockKeepingUnit': sku})
    
    write_csv(PRICING_DEST / 'Product2.csv', pricing_scaled_skus)
    print(f"  ✓ {len(pricing_scaled_skus)} products will have pricing")
    
    # STEP 3: Scale PricebookEntry
    print()
    print("STEP 3: Scaling PricebookEntry.csv...")
    print("  (Updating Name field to make entries unique)")
    orig_entries = read_csv(PRICING_SOURCE / 'PricebookEntry.csv')
    all_entries = [r.copy() for r in orig_entries]
    
    for new_sku, template_sku in sku_mapping.items():
        # Only create pricing for products whose template has pricing
        if template_sku not in products_with_pricing:
            continue
        
        # Extract suffix for name updates
        sku_parts = new_sku.split('-GEN')
        suffix = f" GEN{sku_parts[1]}" if len(sku_parts) == 2 else ""
        
        for row in orig_entries:
            if row.get('Product2.StockKeepingUnit') == template_sku:
                new_row = update_row(row, template_sku, new_sku)
                
                # Update the Name to be unique for generated products
                if 'Name' in new_row and new_row['Name'] and suffix:
                    new_row['Name'] = new_row['Name'] + suffix
                    
                    # Update the compound external ID to include new Name
                    ext_id_field = '$$Name$Pricebook2.Name$Product2.StockKeepingUnit$ProductSellingModel.Name$CurrencyIsoCode'
                    if ext_id_field in new_row:
                        parts = new_row[ext_id_field].split(';')
                        if len(parts) == 5:
                            new_row[ext_id_field] = f"{parts[0]}{suffix};{parts[1]};{new_sku};{parts[3]};{parts[4]}"
                
                all_entries.append(new_row)
    
    write_csv(PRICING_DEST / 'PricebookEntry.csv', all_entries)
    print(f"  ✓ {len(all_entries)} total ({len(orig_entries)} original + {len(all_entries) - len(orig_entries)} new)")
    
    # STEP 4: Scale AttributeBasedAdjRule (must be scaled for each product)
    print()
    print("STEP 4: Scaling AttributeBasedAdjRule.csv...")
    orig_rules = read_csv(PRICING_SOURCE / 'AttributeBasedAdjRule.csv')
    all_rules = [r.copy() for r in orig_rules]
    
    # Track which rules belong to which products by analyzing conditions
    rule_to_products = {}
    conditions = read_csv(PRICING_SOURCE / 'AttributeAdjustmentCondition.csv')
    for cond in conditions:
        rule_name = cond.get('AttributeBasedAdjRule.Name', '')
        product_sku = cond.get('Product.StockKeepingUnit', '')
        if rule_name and product_sku:
            if rule_name not in rule_to_products:
                rule_to_products[rule_name] = set()
            rule_to_products[rule_name].add(product_sku)
    
    # Create new rules for generated products
    rule_mapping = {}  # (old_rule, new_sku) -> new_rule_name
    for rule in orig_rules:
        rule_name = rule.get('Name', '')
        if not rule_name or rule_name not in rule_to_products:
            continue
        
        # For each product this rule applies to
        for template_sku in rule_to_products[rule_name]:
            # Create rules for all generated products from this template
            for new_sku, mapped_template in sku_mapping.items():
                if mapped_template == template_sku:
                    # Create new rule name unique to this product
                    new_rule_name = f"{rule_name}-{new_sku}"
                    new_rule = {'Name': new_rule_name}
                    all_rules.append(new_rule)
                    # Map by (old_rule, new_sku) to avoid collisions
                    rule_mapping[(rule_name, new_sku)] = new_rule_name
    
    write_csv(PRICING_DEST / 'AttributeBasedAdjRule.csv', all_rules)
    print(f"  ✓ {len(all_rules)} total ({len(orig_rules)} original + {len(all_rules) - len(orig_rules)} new)")
    print(f"    Created {len(rule_mapping)} rule mappings for generated products")
    
    # STEP 5: Scale AttributeAdjustmentCondition (with new rule names)
    print()
    print("STEP 5: Scaling AttributeAdjustmentCondition.csv...")
    print("  (Updating to product-specific rule names)")
    orig_cond = read_csv(PRICING_SOURCE / 'AttributeAdjustmentCondition.csv')
    all_cond = [r.copy() for r in orig_cond]
    
    updated_count = 0
    for new_sku, template_sku in sku_mapping.items():
        if template_sku not in products_with_pricing:
            continue
        
        for row in orig_cond:
            if row.get('Product.StockKeepingUnit') == template_sku:
                # DON'T use update_row - it would corrupt AttributeDefinition.Code!
                # Only update specific fields
                new_row = row.copy()
                new_row['Product.StockKeepingUnit'] = new_sku
                
                # Update the rule name to use the new product-specific rule
                old_rule = row.get('AttributeBasedAdjRule.Name', '')
                if old_rule:
                    # Use (rule, new_sku) tuple for lookup
                    rule_key = (old_rule, new_sku)
                    if rule_key in rule_mapping:
                        new_rule_name = rule_mapping[rule_key]
                        new_row['AttributeBasedAdjRule.Name'] = new_rule_name
                        # Update compound external ID (keep AttributeDefinition.Code unchanged!)
                        ext_id_field = '$$AttributeBasedAdjRule.Name$AttributeDefinition.Code$Product.StockKeepingUnit'
                        if ext_id_field in new_row:
                            parts = new_row[ext_id_field].split(';')
                            if len(parts) == 3:
                                # Parts: [rule_name, attr_code, product_sku]
                                new_row[ext_id_field] = f"{new_rule_name};{parts[1]};{new_sku}"
                        updated_count += 1
                    else:
                        print(f"    ⚠️ Warning: No rule mapping for ({old_rule}, {new_sku})")
                all_cond.append(new_row)
    
    write_csv(PRICING_DEST / 'AttributeAdjustmentCondition.csv', all_cond)
    print(f"  ✓ {len(all_cond)} total ({len(orig_cond)} original + {len(all_cond) - len(orig_cond)} new)")
    print(f"    Updated {updated_count} conditions with new rule names")
    
    # STEP 6: Scale AttributeBasedAdjustment (with new rule names)
    print()
    print("STEP 6: Scaling AttributeBasedAdjustment.csv...")
    print("  (Updating to product-specific rule names)")
    orig_adj = read_csv(PRICING_SOURCE / 'AttributeBasedAdjustment.csv')
    all_adj = [r.copy() for r in orig_adj]
    
    updated_adj_count = 0
    for new_sku, template_sku in sku_mapping.items():
        if template_sku not in products_with_pricing:
            continue
        
        for row in orig_adj:
            if row.get('Product.StockKeepingUnit') == template_sku:
                # DON'T use update_row - only update specific fields
                new_row = row.copy()
                new_row['Product.StockKeepingUnit'] = new_sku
                
                # Update the rule name
                old_rule = row.get('AttributeBasedAdjRule.Name', '')
                if old_rule:
                    # Use (rule, new_sku) tuple for lookup
                    rule_key = (old_rule, new_sku)
                    if rule_key in rule_mapping:
                        new_rule_name = rule_mapping[rule_key]
                        new_row['AttributeBasedAdjRule.Name'] = new_rule_name
                        # Update compound external ID (keep static refs unchanged)
                        ext_id_field = '$$AttributeBasedAdjRule.Name$PriceAdjustmentSchedule.Name$Product.StockKeepingUnit$ProductSellingModel.Name$CurrencyIsoCode'
                        if ext_id_field in new_row:
                            parts = new_row[ext_id_field].split(';')
                            if len(parts) == 5:
                                new_row[ext_id_field] = f"{new_rule_name};{parts[1]};{new_sku};{parts[3]};{parts[4]}"
                        updated_adj_count += 1
                all_adj.append(new_row)
    
    write_csv(PRICING_DEST / 'AttributeBasedAdjustment.csv', all_adj)
    print(f"  ✓ {len(all_adj)} total ({len(orig_adj)} original + {len(all_adj) - len(orig_adj)} new)")
    print(f"    Updated {updated_adj_count} adjustments with new rule names")
    
    # STEP 7: Scale PriceAdjustmentTier
    print()
    print("STEP 7: Scaling PriceAdjustmentTier.csv...")
    orig_tiers = read_csv(PRICING_SOURCE / 'PriceAdjustmentTier.csv')
    all_tiers = [r.copy() for r in orig_tiers]
    
    for new_sku, template_sku in sku_mapping.items():
        if template_sku not in products_with_pricing:
            continue
        
        for row in orig_tiers:
            if row.get('Product2.StockKeepingUnit') == template_sku:
                new_row = update_row(row, template_sku, new_sku)
                all_tiers.append(new_row)
    
    write_csv(PRICING_DEST / 'PriceAdjustmentTier.csv', all_tiers)
    print(f"  ✓ {len(all_tiers)} total ({len(orig_tiers)} original + {len(all_tiers) - len(orig_tiers)} new)")
    
    # STEP 8: Scale BundleBasedAdjustment
    print()
    print("STEP 8: Scaling BundleBasedAdjustment.csv...")
    orig_bundle = read_csv(PRICING_SOURCE / 'BundleBasedAdjustment.csv')
    all_bundle = [r.copy() for r in orig_bundle]
    
    for new_sku, template_sku in sku_mapping.items():
        if template_sku not in products_with_pricing:
            continue
        
        for row in orig_bundle:
            # BundleBasedAdjustment can reference products in multiple fields
            if (row.get('Product.StockKeepingUnit') == template_sku or
                row.get('ParentProduct.StockKeepingUnit') == template_sku or
                row.get('RootBundle.StockKeepingUnit') == template_sku):
                new_row = update_row(row, template_sku, new_sku)
                all_bundle.append(new_row)
    
    write_csv(PRICING_DEST / 'BundleBasedAdjustment.csv', all_bundle)
    print(f"  ✓ {len(all_bundle)} total ({len(orig_bundle)} original + {len(all_bundle) - len(orig_bundle)} new)")
    
    # STEP 9: Scale PricebookEntryDerivedPrice
    print()
    print("STEP 9: Scaling PricebookEntryDerivedPrice.csv...")
    print("  (Updating PricebookEntry.Name references to match scaled entries)")
    orig_derived = read_csv(PRICING_SOURCE / 'PricebookEntryDerivedPrice.csv')
    all_derived = [r.copy() for r in orig_derived]
    
    for new_sku, template_sku in sku_mapping.items():
        if template_sku not in products_with_pricing:
            continue
        
        for row in orig_derived:
            # Only scale when the main product matches, keep contributing product as original
            if row.get('Product.StockKeepingUnit') == template_sku:
                new_row = update_row(row, template_sku, new_sku)
                
                # Also update PricebookEntry.Name references to match the scaled PricebookEntry
                suffix = new_sku.replace(template_sku, '')
                
                # Update compound external ID
                ext_id_field = '$$Pricebook.Name$PricebookEntry.Name$Product.StockKeepingUnit$ContributingProduct.StockKeepingUnit$ProductSellingModel.Name$CurrencyIsoCode'
                if ext_id_field in new_row:
                    parts = new_row[ext_id_field].split(';')
                    if len(parts) == 6:
                        # parts[1] is PricebookEntry.Name
                        new_row[ext_id_field] = f"{parts[0]};{parts[1]}{suffix};{parts[2]};{parts[3]};{parts[4]};{parts[5]}"
                
                # Update lookup field
                lookup_field = 'PricebookEntry.$$Name$Pricebook2.Name$Product2.StockKeepingUnit$ProductSellingModel.Name$CurrencyIsoCode'
                if lookup_field in new_row:
                    parts = new_row[lookup_field].split(';')
                    if len(parts) == 5:
                        # parts[0] is PricebookEntry.Name
                        new_row[lookup_field] = f"{parts[0]}{suffix};{parts[1]};{parts[2]};{parts[3]};{parts[4]}"
                
                all_derived.append(new_row)
    
    write_csv(PRICING_DEST / 'PricebookEntryDerivedPrice.csv', all_derived)
    print(f"  ✓ {len(all_derived)} total ({len(orig_derived)} original + {len(all_derived) - len(orig_derived)} new)")
    
    # STEP 10: Fix PriceAdjustmentSchedule (set inactive for tier import)
    print()
    print("STEP 10: Fixing PriceAdjustmentSchedule.csv...")
    print("  (Setting schedules to INACTIVE to allow tier import)")
    schedules = read_csv(PRICING_SOURCE / 'PriceAdjustmentSchedule.csv')
    for schedule in schedules:
        # Set all schedules to inactive
        schedule['IsActive'] = 'false'
    write_csv(PRICING_DEST / 'PriceAdjustmentSchedule.csv', schedules)
    print(f"  ✓ {len(schedules)} schedules set to INACTIVE")
    print(f"  ⚠️ IMPORTANT: Manually activate schedules after import!")
    
    # STEP 11: Copy other static files
    print()
    print("STEP 11: Copying static reference files...")
    static_files = [
        'Pricebook2.csv',
        'CostBook.csv',
        'CostBookEntry.csv',
        # 'PriceAdjustmentSchedule.csv',  # Handled in STEP 10
        # 'AttributeBasedAdjRule.csv',  # Handled in STEP 4
        'AttributeDefinition.csv',
        'ProductSellingModel.csv',
        'ProrationPolicy.csv',
        'CurrencyType.csv',
        'MissingParentRecordsReport.csv',
        'export.json',
    ]
    
    PRICING_DEST.mkdir(exist_ok=True)
    for filename in static_files:
        src_file = PRICING_SOURCE / filename
        if src_file.exists():
            shutil.copy2(src_file, PRICING_DEST / filename)
    
    print(f"  ✓ Copied static files")
    
    # STEP 12: Create README
    print()
    print("STEP 12: Creating README...")
    
    # Build README without f-string to avoid syntax issues with Apex code
    readme_parts = [
        "# QB-Pricing-1000 Dataset\n",
        "\nPricing data for 1000 products (companion to qb-pcm-1000 dataset).\n",
        "\n## Contents\n",
        f"- **PricebookEntry**: {len(all_entries)} price book entries\n",
        f"- **PriceAdjustmentTier**: {len(all_tiers)} tiers\n",
        f"- **AttributeBasedAdjustment**: {len(all_adj)} adjustments\n",
        f"- **BundleBasedAdjustment**: {len(all_bundle)} bundle adjustments\n",
        f"- **PricebookEntryDerivedPrice**: {len(all_derived)} derived prices\n",
        f"- **Product2**: {len(pricing_scaled_skus)} products (reference only)\n",
        "\n## Key Features\n",
        "\n### AttributeBasedAdjRule Scaling\n",
        "- Creates unique rules for each generated product\n",
        "- Pattern: Rule_1724814105445-QB-API-GEN0170\n",
        "- Ensures business rule: all conditions must reference same product\n",
        "\n### PriceAdjustmentSchedule Fix\n",
        "- Schedules are set to INACTIVE to allow tier import\n",
        "- IMPORTANT: Manually activate schedules after import!\n",
        "\n## Post-Import Steps\n",
        "\nAfter importing, activate PriceAdjustmentSchedules via Apex:\n",
        "\n```apex\n",
        "List<PriceAdjustmentSchedule> scheds = [\n",
        "  SELECT Id FROM PriceAdjustmentSchedule WHERE IsActive = false\n",
        "];\n",
        "for (PriceAdjustmentSchedule s : scheds) {\n",
        "  s.IsActive = true;\n",
        "}\n",
        "update scheds;\n",
        "```\n",
    ]
    readme = ''.join(readme_parts)
    
    with open(PRICING_DEST / 'README.md', 'w') as f:
        f.write(readme)
    
    print(f"  ✓ Created README.md")
    
    print()
    print("="*70)
    print("✓ PRICING DATA GENERATION COMPLETE!")
    print("="*70)
    print(f"Output: {PRICING_DEST}")
    print(f"Products with pricing: {len(pricing_scaled_skus)}")
    print(f"PricebookEntries: {len(all_entries)}")
    print(f"AttributeBasedAdjRules: {len(all_rules)}")
    print()
    print("="*70)
    print("IMPORT SEQUENCE:")
    print("="*70)
    print()
    print("1. Import product catalog:")
    print("   sfdx sfdmu:run --sourceusername csvfile \\")
    print("     --path qb-pcm-1000 --targetusername <your-org>")
    print()
    print("2. Import pricing:")
    print("   sfdx sfdmu:run --sourceusername csvfile \\")
    print("     --path qb-pricing-1000 --targetusername <your-org>")
    print()
    print("3. ⚠️  ACTIVATE PRICE ADJUSTMENT SCHEDULES (required!):")
    print("   - Schedules are imported as INACTIVE to avoid tier errors")
    print("   - Activate via Apex:")
    print()
    print("   List<PriceAdjustmentSchedule> scheds = [")
    print("     SELECT Id FROM PriceAdjustmentSchedule WHERE IsActive = false")
    print("   ];")
    print("   for (PriceAdjustmentSchedule s : scheds) s.IsActive = true;")
    print("   update scheds;")
    print()
    print("="*70)

if __name__ == '__main__':
    main()

