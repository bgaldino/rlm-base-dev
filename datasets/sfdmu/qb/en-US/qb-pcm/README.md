# qb-pcm Data Plan

SFDMU data plan for QuantumBit (QB) Product Catalog Management (PCM). Creates the full product catalog including attribute definitions, picklists, product classifications, products, selling models, component groups, bundle relationships, catalogs, categories, qualifications, and attribute scopes.

## CCI Integration

### Flow: `prepare_product_data`

This plan is executed as **step 1** of the `prepare_product_data` flow (when `qb=true`).

| Step | Task                                | Description                                |
|------|-------------------------------------|--------------------------------------------|
| 1    | `insert_quantumbit_pcm_data`        | Runs this SFDMU plan (single pass)         |
| 3    | `insert_quantumbit_product_image_data` | Runs qb-product-images plan (DisplayUrl)  |

### Task Definition

```yaml
insert_quantumbit_pcm_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-pcm"
```

## Data Plan Overview

The plan uses a **single SFDMU pass** with no Apex activation required. All 28 objects are inserted/upserted in dependency order within a single object set.

```
Single Pass (SFDMU)
─────────────────────────────────────────────
Upsert all 28 objects in dependency order
(attributes, classifications, products,
 selling models, bundles, catalogs)
```

### Objects

| #  | Object                        | Operation | External ID                                                                                           | Records |
|----|-------------------------------|-----------|-------------------------------------------------------------------------------------------------------|---------|
| 1  | AttributePicklist             | Upsert    | `Name`                                                                                                | 25      |
| 2  | AttributePicklistValue        | Upsert    | `Code`                                                                                                | 87      |
| 3  | UnitOfMeasureClass            | Upsert    | `Code`                                                                                                | 5       |
| 4  | UnitOfMeasure                 | Upsert    | `UnitCode`                                                                                            | 12      |
| 5  | AttributeDefinition           | Upsert    | `Code`                                                                                                | 39      |
| 6  | AttributeCategory             | Upsert    | `Code`                                                                                                | 18      |
| 7  | AttributeCategoryAttribute    | Upsert    | `AttributeCategory.Code;AttributeDefinition.Code`                                                     | 34      |
| 8  | ProductClassification         | Upsert    | `Code`                                                                                                | 16      |
| 9  | ProductClassificationAttr     | Upsert    | `Name` (SFDMU v5: simplified from composite) | 36      |
| 10 | Product2                      | Upsert    | `StockKeepingUnit`                                                                                    | 178     |
| 11 | ProductAttributeDefinition    | Upsert    | `AttributeDefinition.Code;Product2.StockKeepingUnit`                                                  | 17      |
| 12 | ProductSellingModel           | Upsert    | `Name;SellingModelType`                                                                               | 9       |
| 13 | ProrationPolicy               | Upsert    | `Name`                                                                                                | 1       |
| 14 | ProductSellingModelOption     | Upsert    | `Product2.StockKeepingUnit;ProductSellingModel.Name;ProductSellingModel.SellingModelType`              | 115     |
| 15 | ProductRampSegment            | Upsert    | `Product.StockKeepingUnit;ProductSellingModel.SellingModelType;SegmentType`                            | 6       |
| 16 | ProductRelationshipType       | Upsert    | `Name`                                                                                                | 4       |
| 17 | ProductComponentGroup         | Upsert    | `Code;ParentProduct.StockKeepingUnit`                                                                 | 26      |
| 18 | ProductRelatedComponent       | Upsert    | `ChildProductClassification.Code;ChildProduct.StockKeepingUnit;ParentProduct.StockKeepingUnit;ProductComponentGroup.Code;ProductRelationshipType.Name` | 78 |
| 19 | ProductComponentGrpOverride   | Upsert    | `Name`                                                                                                | 0       |
| 20 | ProductRelComponentOverride   | Upsert    | `ProductRelatedComponent.Name;OverrideContext.StockKeepingUnit`                                       | 0       |
| 21 | ProductCatalog                | Upsert    | `Code`                                                                                                | 3       |
| 22 | ProductCategory               | Upsert    | `Code`                                                                                                | 18      |
| 23 | ProductCategoryProduct        | Upsert    | `ProductCategory.Code;Product.StockKeepingUnit`                                                       | 98      |
| 24 | ProductQualification          | (default) | `Name`                                                                                                | 0       |
| 25 | ProductDisqualification       | (default) | `Name`                                                                                                | 0       |
| 26 | ProductCategoryDisqual        | (default) | `Name`                                                                                                | 0       |
| 27 | ProductCategoryQualification  | (default) | `Name`                                                                                                | 0       |
| 28 | ProdtAttrScope                | (default) | `Name`                                                                                                | 3       |

**Note:** Objects 19-20 and 24-27 have empty CSVs (0 data records) and serve as placeholders for future data. Objects 24-27 do not specify an `operation` in `export.json`, so SFDMU uses the default behavior.

## Key Object Groups

### Attributes (Objects 1-7)

Attribute infrastructure: picklists with values, definitions with data types, categories for grouping, and the junction object (`AttributeCategoryAttribute`) linking categories to definitions.

### Product Classifications (Objects 8-9)

Hierarchical product classification tree (`ParentProductClassificationId` self-reference) with classification-level attribute assignments (`ProductClassificationAttr`). Currently all 16 records are root-level (no parent set), but the schema supports nesting.

### Products and Selling Models (Objects 10-15)

Core product records (178 products) with product-level attribute overrides, 9 selling models (Evergreen, Term, One-Time variants), proration policy, selling model assignments per product, and ramp segments.

### Bundles and Components (Objects 16-18)

Product bundle structure: relationship types define roles (e.g., "Bundle to Bundle Component"), component groups organize child products within a parent, and `ProductRelatedComponent` maps the actual parent-child relationships with quantities, sequences, and pricing inclusion rules.

### Catalogs and Categories (Objects 21-23)

Product catalog structure with categories (supporting hierarchy via `ParentCategoryId`) and product-to-category assignments. One self-reference exists: "Network Adapter" (`ParentCategory.Code = PCIe`).

## Self-Referencing Objects (Hierarchy Concerns)

Three objects in this plan have self-referential parent lookups:

### ProductComponentGroup (`ParentGroupId` -> ProductComponentGroup)

The QB-QRack-750 bundle has a **2-level hierarchy** of component groups:

| Level 1 (root)            | Level 2 (children)                           |
|---------------------------|----------------------------------------------|
| Computing;QB-QRack-750    | Processor, Cooling                           |
| PCIe;QB-QRack-750         | GPUs, I/O, Networking                        |
| Storage;QB-QRack-750      | Hard Drives, Solid State Drives              |

All other products (QB-BDL-R750, QB-BDL-SRVC, QB-BDL-STND, QB-COMPLETE) have flat (1-level) component groups with no parent.

SFDMU should handle this automatically by detecting the self-referential `ParentGroupId` lookup and internally inserting parent records (those with no `ParentGroup`) before children. **Needs validation** — if SFDMU does not handle this correctly, a 2-pass architecture would be required (Pass 1: root groups, Pass 2: child groups).

### ProductClassification (`ParentProductClassificationId` -> ProductClassification)

Currently **all 16 records are root-level** (no `ParentProductClassification.Code` set). No multi-pass issue today, but adding child classifications in the future would create the same hierarchy concern.

### ProductCategory (`ParentCategoryId` -> ProductCategory)

One self-reference: "Network Adapter" has `ParentCategory.Code = PCIe`. Single-level nesting. SFDMU should handle this automatically.

## Polymorphic Fields

Two objects use **polymorphic lookups** via the `$ObjectType` syntax. The `OverrideContextId` field is polymorphic, meaning it can point to different Salesforce object types. SFDMU handles this by specifying the target type in the field name (e.g., `OverrideContextId$Product2`) and filtering with `WHERE OverrideContext.Type = 'Product2'`.

### Schema (confirmed via org describe)

| Object                        | Field               | Polymorphic Targets     |
|-------------------------------|---------------------|-------------------------|
| ProductComponentGrpOverride   | `OverrideContextId` | **Product2, Promotion** |
| ProductRelComponentOverride   | `OverrideContextId` | **Product2, Promotion** |

### Current Coverage

The plan currently only handles the **Product2** polymorphic type:

```json
// ProductComponentGrpOverride (Object 19)
"query": "SELECT ... OverrideContextId$Product2 FROM ProductComponentGrpOverride WHERE OverrideContext.Type = 'Product2'"
"externalId": "Name"

// ProductRelComponentOverride (Object 20)
"query": "SELECT ... OverrideContextId$Product2 FROM ProductRelComponentOverride WHERE OverrideContext.Type = 'Product2'"
"externalId": "ProductRelatedComponent.Name;OverrideContext.StockKeepingUnit"
```

Both CSVs are currently **empty (0 records)**.

### Missing Coverage: Promotion

The `Promotion` polymorphic type is **not covered** by this plan. To support Promotion-based overrides, additional object entries would be needed:

```json
// ProductComponentGrpOverride for Promotion context
{
  "query": "SELECT Id, IsExcluded, MaxBundleComponents, MinBundleComponents, Name, OverrideContextId$Promotion FROM ProductComponentGrpOverride WHERE OverrideContext.Type = 'Promotion'",
  "operation": "Upsert",
  "externalId": "Name"
}

// ProductRelComponentOverride for Promotion context
{
  "query": "SELECT DoesBundlePriceIncludeChild, Id, IsComponentRequired, IsDefaultComponent, IsExcluded, IsQuantityEditable, MaxQuantity, MinQuantity, Name, OverrideContextId$Promotion, ProductRelatedComponentId, Quantity, QuantityScaleMethod, UnitOfMeasureId FROM ProductRelComponentOverride WHERE OverrideContext.Type = 'Promotion'",
  "operation": "Upsert",
  "externalId": "ProductRelatedComponent.Name;OverrideContext.Name"
}
```

**Note:** The `externalId` for Promotion-context overrides would need to use `OverrideContext.Name` (Promotion Name) instead of `OverrideContext.StockKeepingUnit` (which is Product2-specific). The exact external ID strategy for Promotion overrides needs to be determined based on which Promotion fields provide a portable unique key.

### Plan for Full Polymorphic Support

To support all polymorphic variations of `OverrideContextId`, the plan needs:

1. **One SFDMU object entry per polymorphic type per object** — each with its own `$ObjectType` suffix, `WHERE` filter, and type-appropriate `externalId`
2. **Separate CSV files per type** — SFDMU's `useSeparatedCSVFiles` or manual file naming to keep Product2-based and Promotion-based overrides in separate CSVs
3. **Portable external IDs per type** — `OverrideContext.StockKeepingUnit` for Product2, `OverrideContext.Name` (or another portable field) for Promotion
4. **Extraction support** — the extraction queries must also include the polymorphic type filter to produce clean, type-specific CSVs

## Composite External IDs

Several objects use multi-field composite external IDs for idempotent matching:

| Object                      | Composite Key                                                         | CSV `$$` Column |
|-----------------------------|-----------------------------------------------------------------------|-----------------|
| AttributeCategoryAttribute  | `AttributeCategory.Code;AttributeDefinition.Code`                     | Yes             |
| ProductClassificationAttr   | `ProductClassification.Code;AttributeDefinition.Code;AttributeCategory.Code` | Yes      |
| ProductAttributeDefinition  | `AttributeDefinition.Code;Product2.StockKeepingUnit`                  | Yes             |
| ProductSellingModel         | `Name;SellingModelType`                                               | Yes             |
| ProductSellingModelOption   | `Product2.StockKeepingUnit;ProductSellingModel.Name;ProductSellingModel.SellingModelType` | Yes |
| ProductRampSegment          | `Product.StockKeepingUnit;ProductSellingModel.SellingModelType;SegmentType` | Yes        |
| ProductComponentGroup       | `Code;ParentProduct.StockKeepingUnit`                                 | Yes             |
| ProductRelatedComponent     | 5-field composite (Classification, Child, Parent, Group, RelType)     | Yes             |
| ProductCategoryProduct      | `ProductCategory.Code;Product.StockKeepingUnit`                       | Yes             |

Objects with composite external IDs include a `$$` column in their CSV for SFDMU matching (e.g., `$$AttributeCategory.Code$AttributeDefinition.Code`). Several CSVs also include nested `$$` columns for parent lookup resolution (e.g., `ProductSellingModel.$$Name$SellingModelType`).

## Portability

All external IDs use portable, human-readable fields:

- **Code** fields: `AttributePicklistValue.Code`, `UnitOfMeasure.UnitCode`, `AttributeDefinition.Code`, `AttributeCategory.Code`, `ProductClassification.Code`, `ProductCatalog.Code`, `ProductCategory.Code`, `ProductComponentGroup.Code`
- **StockKeepingUnit**: Used for all Product2 references
- **Name** fields: `AttributePicklist.Name`, `ProductSellingModel.Name`, `ProrationPolicy.Name`, `ProductRelationshipType.Name` — all human-readable (not auto-numbered)
- **DeveloperName**: `AttributeDefinition.DeveloperName` (human-readable)

No auto-numbered Name fields are used in this plan. All `Name`-based external IDs contain descriptive, stable values that are consistent across orgs.

## Dependencies

This plan has **no upstream dependencies** — it is the first plan loaded in the `prepare_rlm_org` flow.

This plan is a prerequisite for:

- **qb-product-images** — Updates `DisplayUrl` on Product2 records created here
- **qb-pricing** — References Product2 (SKU), ProductSellingModel (Name;SellingModelType), ProrationPolicy, AttributeDefinition
- **qb-rating** — References Product2 (SKU), UnitOfMeasure, UnitOfMeasureClass
- **qb-rates** — References Product2 (SKU) created here
- **qb-tax** — Updates Product2 `TaxPolicyId` on records created here
- **qb-billing** — Updates Product2 `BillingPolicyId` on records created here
- **qb-dro** — Updates Product2 DRO fields on records created here

## File Structure

```
qb-pcm/
├── export.json                          # SFDMU data plan (single pass, 28 objects)
├── README.md                            # This file
│
│  Source CSVs — Attribute Infrastructure
├── AttributePicklist.csv                # 25 records
├── AttributePicklistValue.csv           # 87 records
├── AttributeDefinition.csv              # 39 records
├── AttributeCategory.csv                # 18 records
├── AttributeCategoryAttribute.csv       # 34 records
│
│  Source CSVs — Units of Measure
├── UnitOfMeasureClass.csv               # 5 records
├── UnitOfMeasure.csv                    # 12 records
│
│  Source CSVs — Classifications
├── ProductClassification.csv            # 16 records
├── ProductClassificationAttr.csv        # 36 records
│
│  Source CSVs — Products and Selling Models
├── Product2.csv                         # 178 records
├── ProductAttributeDefinition.csv       # 17 records
├── ProductSellingModel.csv              # 9 records
├── ProrationPolicy.csv                  # 1 record
├── ProductSellingModelOption.csv        # 115 records
├── ProductRampSegment.csv               # 6 records
│
│  Source CSVs — Bundles and Components
├── ProductRelationshipType.csv          # 4 records
├── ProductComponentGroup.csv            # 26 records
├── ProductRelatedComponent.csv          # 78 records
├── ProductComponentGrpOverride.csv      # 0 records (placeholder)
├── ProductRelComponentOverride.csv      # 0 records (placeholder)
│
│  Source CSVs — Catalogs and Categories
├── ProductCatalog.csv                   # 3 records
├── ProductCategory.csv                  # 18 records
├── ProductCategoryProduct.csv           # 98 records
│
│  Source CSVs — Qualifications (placeholders)
├── ProductQualification.csv             # 0 records (placeholder)
├── ProductDisqualification.csv          # 0 records (placeholder)
├── ProductCategoryDisqual.csv           # 0 records (placeholder)
├── ProductCategoryQualification.csv     # 0 records (placeholder)
│
│  Source CSVs — Attribute Scopes
├── ProdtAttrScope.csv                   # 3 records
│
│  SFDMU Runtime (gitignored)
├── source/                              # SFDMU-generated source snapshots
└── target/                              # SFDMU-generated target snapshots
```

## Extraction

```bash
cci task run extract_qb_pcm_data --org <your-org>
```

This task is in the **Data Management - Extract** group. To run all QB extract tasks: `cci flow run run_qb_extracts --org <org>`. To run all idempotency tests (including qb-pcm): `cci flow run run_qb_idempotency_tests --org <org>`.

Extracted CSVs are written to a timestamped directory under `datasets/sfdmu/extractions/qb-pcm/`. **The extract task runs the post-processor by default**, so re-import-ready CSVs (with `$$` composite key columns) are in `<timestamp>/processed/`. To re-process an existing extraction manually:

```bash
python3 scripts/post_process_extraction.py <extraction-dir> datasets/sfdmu/qb/en-US/qb-pcm --output-dir <output-dir>
```

To get only raw SFDMU output (no post-process), run the task with `-o run_post_process false`.

The idempotency task uses this flow (load → extract → post-process → load from processed) when `use_extraction_roundtrip` is true (the default for `test_qb_pcm_idempotency`; from CLI use `-o use_extraction_roundtrip true`). With `persist_extraction_output: true` (default for qb-pcm), extraction and processed output are written to `datasets/sfdmu/extractions/qb-pcm/<timestamp>/` instead of a temp dir. To validate that extracted data can be re-imported without creating duplicates, run the idempotency task as-is.

## Idempotency

This plan should be idempotent via SFDMU's Upsert operation with composite external IDs. Re-running on an org that already has the data should match all existing records and leave them untouched (zero new inserts).

**SFDMU v5 composite key notation:** Objects with multi-component `externalId` (e.g. `Name;SellingModelType`) require a `$$` column in the CSV for idempotent matching: column name uses `$` between components (e.g. `$$Name$SellingModelType`), values use `;` (e.g. `Evergreen Monthly;Evergreen`). The qb-pcm source CSVs include these columns. To verify idempotency, run:

```bash
cci task run test_qb_pcm_idempotency --org <your-org>
```

That task runs the load twice and fails if any object's record count increases on the second run. By default it uses **extraction roundtrip**: the second run loads from post-processed extracted data (extract → post-process → load), validating that extracted data is v5 re-import ready. To test idempotency from source only (no extraction), run with `use_extraction_roundtrip: false` (e.g. `-o use_extraction_roundtrip false`).

**Not yet validated** — idempotency testing against a 260 org is pending.

## 260 Schema Validation Notes

- **API Version**: `66.0` (Release 260)
- **Schema validation pending** — needs to be tested against a 260 scratch org to confirm all fields in SOQL queries are valid
- Objects 24-27 (Qualification/Disqualification) have no `operation` specified in `export.json` — should be verified that SFDMU handles the default behavior correctly for empty datasets
- `ProductComponentGrpOverride` and `ProductRelComponentOverride` use polymorphic `OverrideContextId$Product2` syntax — should verify this works correctly in 260
- Self-referencing objects (ProductComponentGroup, ProductClassification, ProductCategory) — verify SFDMU handles the internal multi-pass automatically in 260

## External ID / Composite Key Analysis (Confirmed via Org Describe)

### Schema-Enforced Unique Fields

The following fields have `isUnique=true` in the 260 schema — the platform guarantees no duplicates:

| Object                  | Field  | isUnique | isIdLookup | Current ExternalId Uses It? |
|-------------------------|--------|----------|------------|------------------------------|
| AttributePicklistValue  | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |
| UnitOfMeasureClass      | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |
| AttributeDefinition     | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |
| AttributeCategory       | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |
| ProductClassification   | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |
| ProductComponentGroup   | `Code` | **Yes**  | Yes        | ⚠️ Partially — uses `Code;ParentProduct.StockKeepingUnit` |
| ProductCatalog          | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |
| ProductCategory         | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |

### Simplification Opportunity: ProductComponentGroup

`ProductComponentGroup.Code` is **schema-enforced unique**. The current externalId is `Code;ParentProduct.StockKeepingUnit` (2-field composite), but since `Code` alone guarantees uniqueness, the `ParentProduct.StockKeepingUnit` component is **redundant**. This simplification would:
- Remove the need for the `$$` composite key column in the CSV
- Simplify the SFDMU matching logic
- Reduce the risk of matching failures when parent product changes

**Recommendation:** Simplify externalId from `Code;ParentProduct.StockKeepingUnit` to just `Code`.

### Fields NOT Schema-Unique but Used as ExternalId

| Object                  | Current ExternalId      | isUnique | isIdLookup | Risk    |
|-------------------------|-------------------------|----------|------------|---------|
| Product2                | `StockKeepingUnit`      | No*      | No*        | OK — see note |
| AttributePicklist       | `Name`                  | No       | Yes        | Low — manually managed |
| ProductRelationshipType | `Name`                  | No       | Yes        | Low — 4 records |
| ProrationPolicy         | `Name`                  | No       | Yes        | Low — 1 record |
| ProdtAttrScope          | `Name`                  | No       | Yes        | Low — 3 records |

**Note on `Product2.StockKeepingUnit`:** The schema describe does not report `isUnique=true` or `isIdLookup=true` for SKU. However, Salesforce enforces uniqueness at the application level when Industries CPQ / RLM features are enabled. SKU is historically considered unique in RLM contexts and is the standard portable product identifier across all plans. Will validate via testing.

### Auto-Numbered Name Fields (Portability Assessment)

Objects with `Name autoNum=true` cannot use Name as a portable externalId. Assessment of current handling:

| Object                       | Name Auto-Num | Current ExternalId                     | Assessment |
|------------------------------|---------------|----------------------------------------|------------|
| AttributeCategoryAttribute   | **Yes**       | `AttributeCategory.Code;AttributeDefinition.Code` | ✅ Good — both parents have unique Code |
| ProductSellingModelOption    | **Yes**       | `Product2.SKU;PSM.Name;PSM.SellingModelType` | ✅ Good — composite from parents |
| ProductRampSegment           | **Yes**       | `Product.SKU;PSM.SellingModelType;SegmentType` | ✅ Good — composite from parents |
| ProductRelatedComponent      | **Yes**       | 5-field composite from parents         | ✅ Good — comprehensive composite |
| ProductCategoryProduct       | **Yes**       | `ProductCategory.Code;Product.SKU`     | ✅ Good — Code is unique, SKU by convention |
| ProductComponentGrpOverride  | **Yes**       | `Name`                                 | **PROBLEM** — auto-num Name (0 records) |
| ProductRelComponentOverride  | **Yes**       | `ProductRelatedComponent.Name;OverrideContext.SKU` | **PROBLEM** — refs auto-num parent Name |
| ProductQualification         | **Yes**       | `Name`                                 | **PROBLEM** — auto-num Name (0 records) |
| ProductDisqualification      | **Yes**       | `Name`                                 | **PROBLEM** — auto-num Name (0 records) |
| ProductCategoryDisqual       | **Yes**       | `Name`                                 | **PROBLEM** — auto-num Name (0 records) |
| ProductCategoryQualification | **Yes**       | `Name`                                 | **PROBLEM** — auto-num Name (0 records) |

### Portability Fixes Needed (Before Data is Added)

**Objects 19-20 (Overrides) — must fix before Promotion data is added:**
- `ProductComponentGrpOverride`: Replace `Name` with a composite key from parent fields (e.g., `ProductComponentGroup.Code;OverrideContext.StockKeepingUnit` or `OverrideContext.Name` for Promotion context)
- `ProductRelComponentOverride`: Replace `ProductRelatedComponent.Name` reference — the parent PRC has auto-num Name. Need a composite key from PRC's parent fields instead.

**Objects 24-27 (Qualification/Disqualification) — must fix before data is added:**
- All four objects use auto-num `Name` as externalId. Need to identify composite keys from their parent lookup fields for portable matching.

### Additional Discovery: ProductAttributeDefinition.OverrideContextId

Schema describe revealed that `ProductAttributeDefinition` has a **polymorphic** `OverrideContextId` field targeting **Product2** and **Promotion** — same pattern as the Override objects. Currently not used in the SOQL query (only `AttributeDefinition.Code;Product2.StockKeepingUnit` is selected). If override-context PAD records are needed, this polymorphic field will need the same `$ObjectType` handling.

## Optimization Opportunities

1. **Simplify ProductComponentGroup externalId**: `Code` is schema-unique — remove redundant `ParentProduct.StockKeepingUnit` component
2. **Fix override object externalIds**: Replace auto-num `Name` on ProductComponentGrpOverride and ProductRelComponentOverride with composite parent-based keys before Promotion data is added
3. **Fix qualification/disqualification externalIds**: Replace auto-num `Name` on all 4 qualification objects with composite parent-based keys before data is added
4. **Validate self-referencing objects**: Test that SFDMU handles ProductComponentGroup's 2-level hierarchy in a single pass
5. **Add Promotion polymorphic support**: `OverrideContextId` targets both Product2 and Promotion — see "Polymorphic Fields" section
6. **Handle ProductAttributeDefinition polymorphic**: `OverrideContextId` also targets Product2 and Promotion on PAD
7. **Verify empty-object behavior**: Confirm SFDMU handles objects 19-20 and 24-27 correctly when CSVs have no data rows
8. **Add explicit operations**: Objects 24-28 should have explicit `operation` fields in `export.json` for clarity
9. **Consider `excludeIdsFromCSVFiles`**: Already set to `"true"` — good for portability
