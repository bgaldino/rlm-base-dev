# End-to-End Trace: Generating QB-BDL-R750-GEN0001

## Original Data

### Product2.csv (Row 19)
```
StockKeepingUnit: QB-BDL-R750
Name: PowerSwerve R750 Rack Server
```

### ProductComponentGroup.csv (Rows 2-5)
```
Row 2: Code=PCG-QB-SRV-CPU, ParentProduct=QB-BDL-R750, ExternalID=PCG-QB-SRV-CPU;QB-BDL-R750
Row 3: Code=PCG-QB-SRV-HDD, ParentProduct=QB-BDL-R750, ExternalID=PCG-QB-SRV-HDD;QB-BDL-R750
Row 4: Code=PCG-QB-SRV-NIC, ParentProduct=QB-BDL-R750, ExternalID=PCG-QB-SRV-NIC;QB-BDL-R750
Row 5: Code=PCG-QB-SRV-RAM, ParentProduct=QB-BDL-R750, ExternalID=PCG-QB-SRV-RAM;QB-BDL-R750
```

### ProductRelatedComponent.csv (Row 7)
```
ExternalID: ;QB-BET X710SFP;QB-BDL-R750;PCG-QB-SRV-NIC;Bundle to Bundle Component Relationship
ChildProduct: QB-BET X710SFP
ParentProduct: QB-BDL-R750
ProductComponentGroup: PCG-QB-SRV-NIC;QB-BDL-R750
RelationshipType: Bundle to Bundle Component Relationship
```

## Step-by-Step Generation

### STEP 1: Scale Product2
```python
# Generate new product
new_product = {
    'StockKeepingUnit': 'QB-BDL-R750-GEN0001',
    'Name': 'PowerSwerve R750 Rack Server Gen1',
    ...
}

# Add to sku_mapping
sku_mapping['QB-BDL-R750-GEN0001'] = 'QB-BDL-R750'
```

**Result**: Product2 has new row with SKU=QB-BDL-R750-GEN0001 ✅

### STEP 2: Scale ProductComponentGroup
```python
old_sku = 'QB-BDL-R750'
new_sku = 'QB-BDL-R750-GEN0001'

for row in original_ProductComponentGroup:
    if row['ParentProduct.StockKeepingUnit'] == old_sku:
        # Row 2: PCG-QB-SRV-CPU;QB-BDL-R750
        new_row = update_row(row, old_sku, new_sku)
        # update_row replaces 'QB-BDL-R750' with 'QB-BDL-R750-GEN0001' in ALL fields
```

**Result**: ProductComponentGroup gets 4 new rows:
```
Row N+1: Code=PCG-QB-SRV-CPU, ParentProduct=QB-BDL-R750-GEN0001, ExternalID=PCG-QB-SRV-CPU;QB-BDL-R750-GEN0001
Row N+2: Code=PCG-QB-SRV-HDD, ParentProduct=QB-BDL-R750-GEN0001, ExternalID=PCG-QB-SRV-HDD;QB-BDL-R750-GEN0001
Row N+3: Code=PCG-QB-SRV-NIC, ParentProduct=QB-BDL-R750-GEN0001, ExternalID=PCG-QB-SRV-NIC;QB-BDL-R750-GEN0001  ← CRITICAL!
Row N+4: Code=PCG-QB-SRV-RAM, ParentProduct=QB-BDL-R750-GEN0001, ExternalID=PCG-QB-SRV-RAM;QB-BDL-R750-GEN0001
```
✅ The ProductComponentGroup records now exist!

### STEP 3: Scale ProductRelatedComponent
```python
old_sku = 'QB-BDL-R750'
new_sku = 'QB-BDL-R750-GEN0001'

for row in original_ProductRelatedComponent:
    if row['ParentProduct.StockKeepingUnit'] == old_sku:
        # Row 7 matches!
        new_row = update_row(row, old_sku, new_sku)
```

**Field-by-field transformation**:
```python
# Original row 7:
old_row = {
    '$$ChildProductClassification...': ';QB-BET X710SFP;QB-BDL-R750;PCG-QB-SRV-NIC;Bundle to Bundle Component Relationship',
    'ChildProduct.StockKeepingUnit': 'QB-BET X710SFP',
    'ParentProduct.StockKeepingUnit': 'QB-BDL-R750',
    'ProductComponentGroup.$$Code$ParentProduct.StockKeepingUnit': 'PCG-QB-SRV-NIC;QB-BDL-R750',
    'ProductRelationshipType.Name': 'Bundle to Bundle Component Relationship',
    ...
}

# After update_row(old_row, 'QB-BDL-R750', 'QB-BDL-R750-GEN0001'):
new_row = {
    '$$ChildProductClassification...': ';QB-BET X710SFP;QB-BDL-R750-GEN0001;PCG-QB-SRV-NIC;Bundle to Bundle Component Relationship',
    'ChildProduct.StockKeepingUnit': 'QB-BET X710SFP',  # unchanged (not the old_sku)
    'ParentProduct.StockKeepingUnit': 'QB-BDL-R750-GEN0001',  # ← UPDATED!
    'ProductComponentGroup.$$Code$ParentProduct.StockKeepingUnit': 'PCG-QB-SRV-NIC;QB-BDL-R750-GEN0001',  # ← UPDATED!
    'ProductRelationshipType.Name': 'Bundle to Bundle Component Relationship',  # unchanged
    ...
}
```

**Result**: ProductRelatedComponent gets new row:
```
ExternalID: ;QB-BET X710SFP;QB-BDL-R750-GEN0001;PCG-QB-SRV-NIC;Bundle to Bundle Component Relationship
ChildProduct: QB-BET X710SFP
ParentProduct: QB-BDL-R750-GEN0001  ← references generated product
ProductComponentGroup: PCG-QB-SRV-NIC;QB-BDL-R750-GEN0001  ← references generated component group (created in Step 2!)
```

## Verification

### Does the ProductComponentGroup reference exist?
✅ **YES**: Created in Step 2 as `PCG-QB-SRV-NIC;QB-BDL-R750-GEN0001`

### Is the compound key correct?
✅ **YES**: External ID contains `QB-BDL-R750-GEN0001` in correct position

### Are all SKU references updated?
✅ **YES**: Both `ParentProduct.StockKeepingUnit` and `ProductComponentGroup` compound field updated

### Will SFDMU be able to resolve the relationships?
✅ **YES**: 
- ProductComponentGroup lookup: `PCG-QB-SRV-NIC;QB-BDL-R750-GEN0001` → Row N+3 (created in Step 2)
- ParentProduct lookup: `QB-BDL-R750-GEN0001` → Row (created in Step 1)
- ChildProduct lookup: `QB-BET X710SFP` → Original product (unchanged)

## Edge Case: What if child is ALSO generated?

If we later generate `QB-BET X710SFP-GEN0050`:

### STEP 4: Scale ProductRelatedComponent (again for child)
```python
old_sku = 'QB-BET X710SFP'
new_sku = 'QB-BET X710SFP-GEN0050'

# Original row 7 (again):
for row in original_ProductRelatedComponent:
    if row['ChildProduct.StockKeepingUnit'] == old_sku:
        # Row 7 matches AGAIN!
        another_new_row = update_row(row, old_sku, new_sku)
```

**Result**: ProductRelatedComponent gets ANOTHER new row:
```
ExternalID: ;QB-BET X710SFP-GEN0050;QB-BDL-R750;PCG-QB-SRV-NIC;Bundle to Bundle Component Relationship
ChildProduct: QB-BET X710SFP-GEN0050  ← references generated child
ParentProduct: QB-BDL-R750  ← references ORIGINAL parent
ProductComponentGroup: PCG-QB-SRV-NIC;QB-BDL-R750  ← references ORIGINAL component group
```

✅ This creates a different relationship pattern (fan-out), which is valid for test data!

## Final Row Count

From 1 original ProductRelatedComponent row (QB-BET X710SFP → QB-BDL-R750):
1. Original: QB-BET X710SFP → QB-BDL-R750
2. Generated parent: QB-BET X710SFP → QB-BDL-R750-GEN0001
3. Generated child: QB-BET X710SFP-GEN0050 → QB-BDL-R750
4. (Optional) Both generated: QB-BET X710SFP-GEN0050 → QB-BDL-R750-GEN0200  ← Only if both happen to template from same source

## Conclusion

✅ **The logic is CORRECT and handles all compound keys properly!**

The string replacement approach works because:
1. Compound keys are string fields
2. SKUs are unique and don't conflict
3. Replacement happens across ALL fields simultaneously
4. Dependencies are created in correct order (ComponentGroup before RelatedComponent)

