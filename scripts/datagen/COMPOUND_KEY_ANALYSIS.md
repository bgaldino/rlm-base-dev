# Compound Key Analysis for Data Scaling

## Files with Product SKU References

| File | External ID | Fields with SKUs | Handled? |
|------|-------------|------------------|----------|
| **Product2.csv** | `StockKeepingUnit` | `StockKeepingUnit` | ✅ Primary |
| **ProductComponentGroup.csv** | `Code;ParentProduct.StockKeepingUnit` | `ParentProduct.StockKeepingUnit` | ✅ CRITICAL |
| **ProductAttributeDefinition.csv** | `AttributeDefinition.Code;Product2.StockKeepingUnit` | `Product2.StockKeepingUnit` | ✅ |
| **ProductSellingModelOption.csv** | `Product2.StockKeepingUnit;ProductSellingModel.Name` | `Product2.StockKeepingUnit` | ✅ |
| **ProductCategoryProduct.csv** | `ProductCategory.Code;Product.StockKeepingUnit` | `Product.StockKeepingUnit` | ✅ |
| **ProductRampSegment.csv** | `Product.StockKeepingUnit;ProductSellingModel.SellingModelType;SegmentType` | `Product.StockKeepingUnit` | ✅ |
| **ProductRelatedComponent.csv** | `ChildProductClassification.Code;ChildProduct.StockKeepingUnit;ParentProduct.StockKeepingUnit;ProductComponentGroup.Code;ProductRelationshipType.Name` | `ChildProduct.StockKeepingUnit`, `ParentProduct.StockKeepingUnit`, `ProductComponentGroup.$$Code$ParentProduct.StockKeepingUnit` | ⚠️ MOST COMPLEX |

## Critical Analysis: ProductRelatedComponent

### External ID Structure
```
ChildProductClassification.Code;ChildProduct.StockKeepingUnit;ParentProduct.StockKeepingUnit;ProductComponentGroup.Code;ProductRelationshipType.Name
```

### Example Row (QB-BET X710SFP → QB-BDL-R750)
```csv
Column 1 (External ID):           ;QB-BET X710SFP;QB-BDL-R750;PCG-QB-SRV-NIC;Bundle to Bundle Component Relationship
Column 2 (ChildProduct):          QB-BET X710SFP
Column 12 (ParentProduct):        QB-BDL-R750
Column 15 (ComponentGroup):       PCG-QB-SRV-NIC;QB-BDL-R750  ← COMPOUND!
Column 16 (RelationshipType):     Bundle to Bundle Component Relationship
```

### When Generating QB-BDL-R750-GEN0001:

#### Dependencies (MUST exist first):
1. ✅ ProductComponentGroup: `PCG-QB-SRV-NIC;QB-BDL-R750-GEN0001`
   - Created by scaling ProductComponentGroup BEFORE ProductRelatedComponent

#### Field Updates (via replace_sku):
```
OLD VALUE                          → NEW VALUE
─────────────────────────────────────────────────────────────
Column 1 (External ID):
;QB-BET X710SFP;QB-BDL-R750;...   → ;QB-BET X710SFP;QB-BDL-R750-GEN0001;...

Column 12 (ParentProduct):
QB-BDL-R750                        → QB-BDL-R750-GEN0001

Column 15 (ComponentGroup):
PCG-QB-SRV-NIC;QB-BDL-R750        → PCG-QB-SRV-NIC;QB-BDL-R750-GEN0001  ← CRITICAL!
```

### When Generating QB-BET X710SFP-GEN0100:

#### Field Updates:
```
OLD VALUE                          → NEW VALUE
─────────────────────────────────────────────────────────────
Column 1 (External ID):
;QB-BET X710SFP;QB-BDL-R750;...   → ;QB-BET X710SFP-GEN0100;QB-BDL-R750;...

Column 2 (ChildProduct):
QB-BET X710SFP                     → QB-BET X710SFP-GEN0100
```

## Verification Logic

### My Current Approach:
```python
# For ProductRelatedComponent
for new_sku, old_sku in sku_mapping.items():
    for row in original_data:
        if (row.get('ParentProduct.StockKeepingUnit') == old_sku or
            row.get('ChildProduct.StockKeepingUnit') == old_sku):
            scaled.append(update_row(row, old_sku, new_sku))

# update_row replaces old_sku with new_sku in ALL string fields
def update_row(row, old_sku, new_sku):
    return {k: replace_sku(v, old_sku, new_sku) for k, v in row.items()}

def replace_sku(val, old, new):
    return val.replace(old, new) if isinstance(val, str) and old in val else val
```

### Does This Handle Everything?

| Scenario | Handled? | Reason |
|----------|----------|--------|
| Parent product generated | ✅ YES | Checks `ParentProduct.StockKeepingUnit`, updates ALL fields including compound keys |
| Child product generated | ✅ YES | Checks `ChildProduct.StockKeepingUnit`, updates ALL fields |
| Both parent and child generated (different cycles) | ✅ YES | Each generation creates separate row with appropriate references |
| ProductComponentGroup reference | ✅ YES | `replace_sku` updates `PCG-QB-SRV-NIC;QB-BDL-R750` → `PCG-QB-SRV-NIC;QB-BDL-R750-GEN0001` |
| ProductComponentGroup exists | ✅ YES | Created BEFORE ProductRelatedComponent scaling |
| External ID compound key | ✅ YES | All parts of compound key updated via string replacement |

## Potential Issues

### ❌ Issue 1: Child products as bundles
If a child product (like QB-API) is ALSO a bundle with its own component group:
- When generating QB-API-GEN0001, we create ProductComponentGroup records for it
- ProductRelatedComponent rows where QB-API is a CHILD get updated correctly
- ProductRelatedComponent rows where QB-API is a PARENT are handled separately ✅

### ❌ Issue 2: Cross-references between generated products
If Product A-GEN0001 references Product B-GEN0002:
- This WON'T happen with current logic
- Each generated product references the SAME children/parents as its template
- This is intentional for test data (fan-out pattern) ✅

### ⚠️ Issue 3: ProductRelatedComponent where BOTH child AND parent are the same generated product?
Looking at the data, there are no self-referential products, so this doesn't apply ✅

## Execution Order (CRITICAL)

```
1. Product2                     ← Base records
2. ProductComponentGroup        ← Must be BEFORE ProductRelatedComponent
3. ProductAttributeDefinition
4. ProductSellingModelOption
5. ProductCategoryProduct
6. ProductRampSegment
7. ProductRelatedComponent      ← Last, depends on ProductComponentGroup
```

## Conclusion

✅ **The logic SHOULD handle all compound keys correctly** because:

1. **String replacement is comprehensive**: `replace_sku` updates SKUs wherever they appear in any field
2. **Dependency order is correct**: ProductComponentGroup is scaled before ProductRelatedComponent
3. **Compound keys are updated automatically**: Since they're string fields containing SKUs, they get updated
4. **Both parent and child scenarios are handled**: The OR condition catches both cases

The script handles the complexity correctly!

