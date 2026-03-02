# qb-rating Data Plan

SFDMU data plan for QuantumBit (QB) usage rating design-time configuration. Creates and activates all objects required for usage-based rating on QB products, including usage resources, product-to-resource associations, grants, and policies.

## CCI Integration

### Flow: `prepare_rating`

This plan is executed as **step 1** of the `prepare_rating` flow (when `rating=true`, `qb=true`, and `refresh=false`).

| Step | Task                     | Description                                        |
|------|--------------------------|----------------------------------------------------|
| 1    | `insert_qb_rating_data`  | Runs this SFDMU plan (2 passes)                    |
| 3    | `insert_qb_rates_data`   | Runs qb-rates plan (single pass — all objects)     |
| 5    | `activate_rating_records`| Runs `activateRatingRecords.apex`                  |
| 6    | `activate_rates`         | Runs `activateRateCardEntries.apex`                |

### Task Definition

```yaml
insert_qb_rating_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-rating"
```

## Data Plan Overview

The plan uses **2 SFDMU object sets** (Pass 1 + Pass 2) followed by **Apex activation**:

```
Pass 1 (SFDMU)                              Pass 2 (SFDMU)       Apex Activation
────────────────────────────────────────   ─────────────────     ─────────────────
Insert+deleteOldData (PUR/PURP/PUG); Upsert others  Activate UoMClass  -> activateRatingRecords.apex
                                            and UsageResource       (7-step PUR/PUG activation)
```

**PUR, PURP, and PUG idempotency (Insert+deleteOldData):** All three use `operation: Insert` with `deleteOldData: true` and **no WHERE clause** — SFDMU v5 cannot match records by relationship-traversal externalId components (even 1-hop like `Product.StockKeepingUnit`) and always inserts instead of updating, causing duplicates on re-run. The fix is Insert+deleteOldData: SFDMU processes deleteOldData in **reverse array order** (PUG → PURP → PUR), satisfying FK constraints (children deleted before parent). No WHERE clause means the plan is fully portable — extraction captures drift for any product in the org. PURP uses `externalId: ProductUsageResourceId` (direct FK, avoids SFDMU v5 validation error for all-multi-hop externalIds). The PURP and PUG CSVs provide `ProductUsageResource.Product.StockKeepingUnit` and `ProductUsageResource.UsageResource.Code` as two separate columns (no `$$` composite) so SFDMU can resolve `ProductUsageResourceId` without triggering the SOQL injection bug.

### Pass 1 — Insert/Upsert with Draft Status

All records are created in `Draft` status. SFDMU resolves lookups across objects using composite external IDs.

| # | Object                       | Operation | External ID                                          | Records |
|---|------------------------------|-----------|------------------------------------------------------|---------|
| 1 | UnitOfMeasure                | Upsert    | `UnitCode`                                           | 12      |
| 2 | UnitOfMeasureClass           | Upsert    | `Code`                                               | 5       |
| 3 | UsageResourceBillingPolicy   | Upsert    | `Code`                                               | 3       |
| 4 | UsageResource                | Upsert    | `Code`                                               | 5       |
| 5 | Product2                     | Update    | `StockKeepingUnit`                                   | 164     |
| 6 | UsageGrantRenewalPolicy      | Upsert    | `Code`                                               | 1       |
| 7 | UsageGrantRolloverPolicy     | Upsert    | `Code`                                               | 1       |
| 8 | UsageOveragePolicy           | Upsert    | `Name`                                               | 2       |
| 9 | UsageCommitmentPolicy        | Upsert    | `Name`                                               | 1       |
| 10| ProductUsageResource         | Insert¹   | `Product.StockKeepingUnit;UsageResource.Code`        | 20      |
| 11| UsagePrdGrantBindingPolicy   | Upsert    | `Name;Product2.StockKeepingUnit`                     | 1       |
| 12| RatingFrequencyPolicy        | Upsert    | `RatingPeriod`                                       | 1       |
| 13| ProductUsageResourcePolicy   | Insert¹   | `ProductUsageResourceId`                             | 17      |
| 14| ProductUsageGrant            | Insert¹   | `UsageDefinitionProduct.StockKeepingUnit;UnitOfMeasureClass.Code;UnitOfMeasure.UnitCode` | 17      |

¹ Insert+deleteOldData (no WHERE). SFDMU v5 cannot match by relationship-traversal externalId — Upsert always inserts duplicates. deleteOldData runs in reverse array order (PUG→PURP→PUR) to satisfy FK constraints.

**Full delete+insert cycle:** PUR, PURP, and PUG all use `deleteOldData: true` with no WHERE clause. Every run deletes ALL records of each type and re-inserts from CSV — no duplicate risk, fully portable. The PURP and PUG CSVs use two separate traversal columns (`ProductUsageResource.Product.StockKeepingUnit` + `ProductUsageResource.UsageResource.Code`) for FK resolution; no `$$` composite column (which caused a SOQL injection bug in the deleteOldData DELETE phase).

### Pass 2 — Activate UnitOfMeasureClass and UsageResource

| # | Object             | Operation | External ID | Records |
|---|--------------------|-----------|-------------|---------|
| 1 | UnitOfMeasureClass | Update    | `Code`      | 5       |
| 2 | UsageResource      | Update    | `Code`      | 5       |

Only UoMClass and UsageResource are activated in SFDMU Pass 2. PUR and PUG activation requires the Apex script (`activate_rating_records`) which enforces a strict dependency order — Token PURs must be Active before non-Token usage PURs, and all PURs must be Active before PUGs.

## Schema: ProductUsageResource (PUR) and product relationship

Org describe confirms: on **ProductUsageResource**, `ProductId` has `relationshipName: Product` (not Product2). So in SOQL we use **Product.StockKeepingUnit** and **UsageResource.Code** on PUR, and **ProductUsageResource.Product.StockKeepingUnit** when traversing from PURP/PUG. UsagePrdGrantBindingPolicy uses **Product2**.StockKeepingUnit (it has Product2Id). RatingFrequencyPolicy uses **Product**.StockKeepingUnit (relationshipName: Product).

PUR, PURP, and PUG all use `operation: Insert` with `deleteOldData: true` (no WHERE clause). PURP uses `externalId: ProductUsageResourceId` (direct FK — avoids SFDMU v5 validation error for all-multi-hop externalIds). The PURP and PUG CSVs have two separate traversal columns (`ProductUsageResource.Product.StockKeepingUnit` and `ProductUsageResource.UsageResource.Code`) for FK resolution — no `$$` composite (which caused a SOQL injection bug in the deleteOldData DELETE phase).

## Apex Activation Script

**File:** `scripts/apex/activateRatingRecords.apex`

PUR and PUG activation follows a strict 7-step dependency order:

| Step | What                                      | Why                                                                |
|------|-------------------------------------------|--------------------------------------------------------------------|
| 1    | UnitOfMeasureClass -> Active              | Safety net (Pass 2 should already do this)                         |
| 2    | UsageResource -> Active                   | Safety net (Pass 2 should already do this, including QB-TOKEN)     |
| 2.5  | Delete childless duplicate Draft PURs     | Defensive step — PUR now uses Insert+deleteOldData so duplicates should never exist; this is a safety net for any edge cases |
| 3    | Pre-populate TokenResourceId on Draft PURs| Ensures clear+activate works in Step 5 (see below)                 |
| 4    | Token PUR -> Active                       | Must precede Step 5; products with Token PURs require them Active before usage PURs can activate |
| 5    | ALL non-Token PUR -> clear+activate       | TokenResourceId=null + Status='Active' in single DML               |
| 6    | ProductUsageGrant -> Active               | Depends on parent PUR being active                                 |

**Step 3 explained:** Some PURs (QB-DB;UR-\*, QB-QTY-CMT;UR-\*) don't get `TokenResourceId` auto-populated at SFDMU insert time. The clear+activate workaround in Step 5 only prevents auto-population when `TokenResourceId` changes from a non-null value to null -- a null-to-null assignment is a no-op that doesn't block auto-population. Step 3 pre-populates `TokenResourceId` from `UsageResource.TokenResourceId` on these Draft PURs so that Step 5's clear is a real change.

The script is **idempotent** — all activation steps filter on `Status != 'Active'`. Step 2.5 is now a safety-net no-op (PUR uses Insert+deleteOldData, so no duplicates should exist). Re-running on an already-activated org is a safe no-op.

## Products and Usage Model Types

| Product SKU        | Usage Model Type   | Description                              |
|--------------------|--------------------|------------------------------------------|
| QB-DB              | Anchor             | QuantumDB — anchor product with token    |
| QB-DB-TOKEN        | Token              | QuantumDB Token product                  |
| QB-DAT-THPT        | (standard)         | Data Throughput — standalone usage        |
| QB-TOKENS-PACK     | TokenPack          | Token pack (one-time purchase)           |
| QB-CMT-TKN-EACH    | CommitmentToken    | Commit token — each-based pricing        |
| QB-CMT-TKN-FLAT    | CommitmentToken    | Commit token — flat-rate pricing         |
| QB-CMT-TKN-TIER    | CommitmentToken    | Commit token — tier-based pricing        |
| QB-QTY-CMT         | CommitmentQuantity | Quantity commitment (CPU/Storage)        |
| QB-MTY-CMT         | CommitmentSpend    | Monetary commitment (USD currency)       |

## Usage Resources

| Code             | Category | UoM Class       | Default UoM | Billing Policy    |
|------------------|----------|-----------------|-------------|-------------------|
| QB-TOKEN         | Token    | Token_UoM_Class | TOKEN-UOM   | monthlytotal      |
| UR-CPUTIME       | Usage    | TIME            | m (Minutes) | monthlytotal      |
| UR-DATASTORAGE   | Usage    | DATAVOL         | TB          | monthlypeak       |
| UR-DATAXFR       | Usage    | DATAVOL         | GB          | monthlytotal      |
| UR-USD           | Currency | CURRENCY        | USD         | monthlytotal      |

## ProductUsageResource (PUR) Mapping

20 records mapping products to their usage resources:

| Product          | Resource        | Token Resource | Notes                              |
|------------------|-----------------|----------------|------------------------------------|
| QB-DB            | QB-TOKEN        | —              | Token PUR for Anchor product       |
| QB-DB            | UR-DATASTORAGE  | —              | Usage PUR (TokenResourceId auto-populated) |
| QB-DB            | UR-CPUTIME      | —              | Usage PUR (TokenResourceId auto-populated) |
| QB-DAT-THPT      | UR-DATAXFR      | —              | Standalone usage (no token)        |
| QB-TOKENS-PACK   | QB-TOKEN        | —              | Token pack                         |
| QB-DB-TOKEN      | QB-TOKEN        | —              | Token PUR                          |
| QB-DB-TOKEN      | UR-DATASTORAGE  | QB-TOKEN       | Usage PUR with explicit token ref  |
| QB-DB-TOKEN      | UR-CPUTIME      | QB-TOKEN       | Usage PUR with explicit token ref  |
| QB-CMT-TKN-EACH  | QB-TOKEN        | —              | Token PUR                          |
| QB-CMT-TKN-EACH  | UR-DATASTORAGE  | QB-TOKEN       | Usage PUR with token ref           |
| QB-CMT-TKN-EACH  | UR-CPUTIME      | QB-TOKEN       | Usage PUR with token ref           |
| QB-CMT-TKN-FLAT  | QB-TOKEN        | —              | Token PUR                          |
| QB-CMT-TKN-FLAT  | UR-CPUTIME      | QB-TOKEN       | Usage PUR with token ref           |
| QB-CMT-TKN-FLAT  | UR-DATASTORAGE  | QB-TOKEN       | Usage PUR with token ref           |
| QB-CMT-TKN-TIER  | QB-TOKEN        | —              | Token PUR                          |
| QB-CMT-TKN-TIER  | UR-DATASTORAGE  | QB-TOKEN       | Usage PUR with token ref           |
| QB-CMT-TKN-TIER  | UR-CPUTIME      | QB-TOKEN       | Usage PUR with token ref           |
| QB-QTY-CMT       | UR-DATASTORAGE  | —              | Commitment qty (no token allowed)  |
| QB-QTY-CMT       | UR-CPUTIME      | —              | Commitment qty (no token allowed)  |
| QB-MTY-CMT       | UR-USD          | —              | Monetary commitment (currency)     |

## ProductUsageGrant (PUG) Summary

17 grant records across 4 usage definition products:

| Usage Definition Product | Type   | Resource          | Quantity | Validity       |
|--------------------------|--------|-------------------|----------|----------------|
| QB-CPU-BLNG              | Grant  | QB-DB;UR-CPUTIME             | 0     | 1 Month |
| QB-CPU-BLNG              | Grant  | QB-DB-TOKEN;UR-CPUTIME       | 0     | 1 Month |
| QB-CPU-BLNG              | Grant  | QB-CMT-TKN-TIER;UR-CPUTIME  | 0     | 1 Month |
| QB-CPU-BLNG              | Grant  | QB-CMT-TKN-FLAT;UR-CPUTIME  | 0     | 1 Month |
| QB-CPU-BLNG              | Grant  | QB-CMT-TKN-EACH;UR-CPUTIME  | 10    | 1 Month |
| QB-CPU-BLNG              | Commit | QB-QTY-CMT;UR-CPUTIME       | 1000  | 1 Month |
| QB-DATA-STORAGE-BLNG     | Grant  | QB-CMT-TKN-TIER;UR-DATASTORAGE | 0  | 1 Month |
| QB-DATA-STORAGE-BLNG     | Grant  | QB-CMT-TKN-FLAT;UR-DATASTORAGE | 0  | 1 Month |
| QB-DATA-STORAGE-BLNG     | Grant  | QB-DB;UR-DATASTORAGE         | 5     | 1 Month |
| QB-DATA-STORAGE-BLNG     | Grant  | QB-DB-TOKEN;UR-DATASTORAGE   | 0     | 1 Month |
| QB-DATA-STORAGE-BLNG     | Grant  | QB-CMT-TKN-EACH;UR-DATASTORAGE | 10 | 1 Month |
| QB-DATA-STORAGE-BLNG     | Commit | QB-QTY-CMT;UR-DATASTORAGE   | 1000  | 1 Month |
| QB-TOKEN-DEF             | Commit | QB-CMT-TKN-FLAT;QB-TOKEN     | 1000  | 1 Month |
| QB-TOKEN-DEF             | Grant  | QB-DB-TOKEN;QB-TOKEN         | 100000| None    |
| QB-TOKEN-DEF             | Commit | QB-CMT-TKN-TIER;QB-TOKEN     | 1000  | 1 Month |
| QB-TOKEN-DEF             | Commit | QB-CMT-TKN-EACH;QB-TOKEN     | 1000  | 1 Month |
| RES-USD-DEF              | Commit | QB-MTY-CMT;UR-USD            | 5000  | 1 Month |

## API 260 Known Issues

### TokenResourceId Auto-Population

The platform auto-populates `TokenResourceId` on non-Token PURs during ANY DML (insert or update) when their `UsageResource` has a Token association (`UsageResource.TokenResourceId` is set). This is independent of QB-TOKEN's Status -- it is driven by the UsageResource relationship field. Affected resources: UR-CPUTIME and UR-DATASTORAGE (both have `TokenResource.Code = QB-TOKEN`).

### Activation Conflict and Clear+Activate Workaround

When activating a PUR (`Status='Active'`), the platform auto-populates `TokenResourceId` during the same DML. This then fails because "TokenResourceId can't be edited when the PUR is Active." The workaround sets `TokenResourceId=null` AND `Status='Active'` in a single DML update, which prevents auto-population.

**Critical nuance:** The clear+activate only works when `TokenResourceId` changes from a **non-null** value to null. A null-to-null "clear" is a no-op and does NOT prevent auto-population. This is why Step 3 of the Apex script pre-populates `TokenResourceId` on Draft PURs where it is missing -- ensuring Step 4's clear is a real field change.

### Excluded Records (258 -> 260 Migration Gap)

The following PURs and their dependent PURP/PUG records are **excluded** from this plan because they cannot be activated in API 260:

- `QB-MTY-CMT;UR-CPUTIME` — CommitmentSpend + Usage (TokenResourceId conflict)
- `QB-MTY-CMT;UR-DATASTORAGE` — CommitmentSpend + Usage (TokenResourceId conflict)

These were `IsOptional=true` records that worked in API 258 but fail validation in 260.

### Anchor Products Require Token PUR

Products with `UsageModelType='Anchor'` (e.g., QB-DB) require a Token PUR (`QB-DB;QB-TOKEN`) to be active before their non-Token PURs can be activated. This was not required in API 258.

### Currency PUR Dependency

CommitmentSpend products (QB-MTY-CMT) require their Currency-category PUR (`QB-MTY-CMT;UR-USD`) to be Active before any Usage-category PURs can be activated.

## File Structure

```
qb-rating/
├── export.json                          # SFDMU data plan (2 passes)
├── README.md                            # This file
│
│  Source CSVs (Pass 1 - Draft status)
├── UnitOfMeasure.csv                    # 12 records
├── UnitOfMeasureClass.csv               # 5 records
├── UsageResourceBillingPolicy.csv       # 3 records
├── UsageResource.csv                    # 5 records
├── Product2.csv                         # 164 records (Update only)
├── UsageGrantRenewalPolicy.csv          # 1 record
├── UsageGrantRolloverPolicy.csv         # 1 record
├── UsageOveragePolicy.csv               # 2 records
├── UsageCommitmentPolicy.csv            # 1 record
├── ProductUsageResource.csv             # 20 records
├── UsagePrdGrantBindingPolicy.csv       # 1 record
├── RatingFrequencyPolicy.csv            # 1 record
├── ProductUsageResourcePolicy.csv       # 17 records
├── ProductUsageGrant.csv                # 17 records
│
│  Source CSVs (Pass 2 - Activate)
├── objectset_source/
│   └── object-set-2/
│       ├── UnitOfMeasureClass.csv       # 5 records (Status > Active)
│       └── UsageResource.csv            # 5 records (Status > Active)
│
│  SFDMU Runtime (gitignored)
├── source/                              # SFDMU-generated source snapshots
└── target/                              # SFDMU-generated target snapshots
```

## Data Extraction

This plan supports **bidirectional** operation: in addition to importing data (CSV > org), it can extract data from any org into portable CSVs.

### Extraction via CCI

```bash
# Extract rating data from the current default org
cci task run extract_qb_rating_data

# Or use the extract_rating flow to extract both rating and rates
cci flow run extract_rating

# Run all QB extract tasks (includes rating)
cci flow run run_qb_extracts
```

To run the idempotency test for this plan: `cci task run test_qb_rating_idempotency --org <org>`. To run all QB idempotency tests: `cci flow run run_qb_idempotency_tests --org <org>`. Tasks are in the **Data Management - Extract** and **Data Management - Idempotency** groups. The rating idempotency test uses **extraction roundtrip** — loads from source CSVs, extracts from the org, post-processes, and re-imports — requiring a Draft-only org state. See [Idempotency](#idempotency) for prerequisites.

### Extraction via SFDMU Directly

```bash
sf sfdmu run --sourceusername <org-alias> --targetusername CSVFILE -p datasets/sfdmu/qb/en-US/qb-rating --noprompt --verbose
```

### Post-Processing Extracted CSVs

Raw SFDMU extraction output contains `Active` status values and may have different column ordering. Use the post-processor to convert:

```bash
# Diff only (compare extraction against current plan)
python3 scripts/post_process_extraction.py <extraction-dir> datasets/sfdmu/qb/en-US/qb-rating --diff-only

# Process and write import-ready CSVs
python3 scripts/post_process_extraction.py <extraction-dir> datasets/sfdmu/qb/en-US/qb-rating --output-dir <output-dir>

# Process and update the plan in place
python3 scripts/post_process_extraction.py <extraction-dir> datasets/sfdmu/qb/en-US/qb-rating --copy-to-plan
```

The post-processor:
- Rewrites `Status` fields from `Active`/`Inactive` to `Draft`
- Aligns column order to match the existing plan CSVs
- Aligns composite key columns (individual relationship fields preferred over legacy `$$` notation)
- Generates `objectset_source/` CSVs for Pass 2
- Produces a diff report comparing extraction against the current plan

### Dual-Purpose SOQL Queries

The SOQL queries in `export.json` include both raw ID fields (e.g., `ProductId`) and relationship traversal fields (e.g., `Product.StockKeepingUnit` for PUR records). During **import**, SFDMU uses the traversal fields for lookup resolution. During **extraction**, SFDMU populates these fields with human-readable values (names, codes, SKUs) instead of raw Salesforce IDs, producing portable CSVs.

## Idempotency

The plan is **fully idempotent**: every run deletes ALL PUR, PURP, and PUG records (deleteOldData, no WHERE) and re-inserts from CSV. Consecutive runs always produce PUR=20, PURP=17, PUG=17. No duplicate risk.

The idempotency test (`test_qb_rating_idempotency`) uses **extraction roundtrip** (`use_extraction_roundtrip: true`): loads from source CSVs → extracts from org → post-processes → re-imports from the processed dir, confirming no record count increase. Extraction output is persisted to `datasets/sfdmu/extractions/qb-rating/<timestamp>/`.

**Prerequisite — Draft-only org state**: SFDMU's `deleteOldData` sends a direct REST DELETE. Salesforce rejects deletion of Active PURs and PUGs (the entire batch fails; Active records stay while new Drafts are inserted on top, doubling counts). Before running the idempotency test, all PURs and PUGs must be in Draft status or absent. If `prepare_rating` has been run, clean up first:

```bash
cci task run delete_qb_rates_data   # deactivate + delete rates (reference PURs via FK)
cci task run delete_qb_rating_data  # deactivate + delete PUG → PURP → PUR via Apex
```

**qb-rates note**: `test_qb_rates_idempotency` uses `use_extraction_roundtrip: false` (load-twice without extraction). SFDMU v5 cannot extract 2-hop traversal fields used as components of RABT's composite externalId (`RateCardEntry.RateCard.Name`, `RateUnitOfMeasure.UnitCode`, `UsageResource.Code`) — extraction produces `#N/A` for those components, breaking FK resolution on re-import.

**Full reset and idempotency test (org already has qb-pcm and qb-billing loaded; uses CCI default org):**

```bash
# 1. Delete rates first (they reference PURs), then rating
cci task run delete_qb_rates_data
cci task run delete_qb_rating_data

# 2. Load rating + rates and activate
cci flow run prepare_rating   # ensure options rating=true, rates=true, qb=true match your project config

# 3. Clean up Active records created by prepare_rating (required before idempotency tests)
cci task run delete_qb_rates_data
cci task run delete_qb_rating_data

# 4. Run idempotency tests from clean Draft state
cci task run test_qb_rating_idempotency
cci task run test_qb_rates_idempotency
```

## Cleanup / Re-run

Two cleanup scripts are available:

```bash
# Full cleanup — deletes PUG, PURP, PUR, and policies in reverse dependency order (uses CCI default org)
cci task run execute_anon --path scripts/apex/deleteQbRatingData.apex

# Legacy cleanup — similar scope, different implementation
cci task run execute_anon --path scripts/apex/cleanupRatingRecords.apex
```

These scripts delete PUG, PURP, PUR, binding policies, frequency policies, overage policies, and commitment policies in reverse dependency order. They do **not** delete UoM, UoMClass, UsageResource, or UsageResourceBillingPolicy (managed by qb-billing/qb-pcm).

## Dependencies

This plan depends on the following having been loaded first:

- **qb-pcm** — Product2 records (referenced by SKU), UnitOfMeasure, UnitOfMeasureClass
- **qb-billing** — UsageResourceBillingPolicy, UsageResource (base records)

This plan is a prerequisite for:

- **qb-rates** — RateCardEntry references ProductUsageResource, UsageResource, and Product2 records created here

## 260 Schema Analysis (Confirmed via Org Describe)

Schema was queried against a 260 scratch org. Findings below.

### Polymorphic Fields

**None found** (excluding standard OwnerId on UsageResource). All reference fields on rating objects are single-target lookups.

### Self-Referencing Fields

| Object         | Field             | Notes                                                    |
|----------------|-------------------|----------------------------------------------------------|
| **UsageResource** | `TokenResourceId` | Self-ref to UsageResource — already handled in plan     |

This self-reference is well-understood and documented in the API 260 Known Issues section above. SFDMU handles it correctly because the token UsageResource records (QB-TOKEN) are inserted first (no parent ref), then usage resources that reference QB-TOKEN are inserted. The Apex activation script handles the complex TokenResourceId pre-population and clear+activate sequence.

### New Fields Found in 260 (Not in Current SOQL)

| Object                       | Field                    | Type      | Updateable | Notes                                                |
|------------------------------|--------------------------|-----------|------------|-------------------------------------------------------|
| **ProductUsageGrant**        | `ProductSellingModelId`  | REFERENCE | Yes        | Lookup to ProductSellingModel — selling model context for grant |
| **ProductUsageResourcePolicy** | `ProductSellingModelId`| REFERENCE | Yes        | Lookup to ProductSellingModel — selling model context for policy |
| **RatingFrequencyPolicy**    | `RatingDelayDurationUnit`| PICKLIST  | Yes        | Unit for rating delay (currently `RatingDelayDuration` is in SOQL without its unit) |
| **UsageCommitmentPolicy**    | `CommitmentRate`         | PICKLIST  | Yes        | Commitment fulfilled rate — controls overage behavior  |

### Field Coverage Audit

| Object                       | Status | Notes                                                        |
|------------------------------|--------|--------------------------------------------------------------|
| UnitOfMeasure                | ✅     | All updateable fields present                                |
| UnitOfMeasureClass           | ✅     | All updateable fields present                                |
| UsageResourceBillingPolicy   | ✅     | All fields present (Code, Name, Status, methods, period)     |
| UsageResource                | ✅     | All fields present including TokenResourceId self-ref        |
| Product2                     | ✅     | Update only (UsageModelType) — correct                       |
| UsageGrantRenewalPolicy      | ✅     | All fields present                                           |
| UsageGrantRolloverPolicy     | ✅     | All fields present                                           |
| UsageOveragePolicy           | ✅     | All fields present (Name, OverageChargeable)                 |
| UsageCommitmentPolicy        | ⚠️     | Missing `CommitmentRate` (new picklist)                      |
| ProductUsageResource         | ✅     | All fields present                                           |
| UsagePrdGrantBindingPolicy   | ✅     | All fields present                                           |
| RatingFrequencyPolicy        | ⚠️     | Missing `RatingDelayDurationUnit` (unit for delay duration)  |
| ProductUsageResourcePolicy   | ⚠️     | Missing `ProductSellingModelId` (new lookup)                 |
| ProductUsageGrant            | ⚠️     | Missing `ProductSellingModelId` (new lookup)                 |

### Impact Assessment

- **`ProductUsageGrant.ProductSellingModelId`** and **`ProductUsageResourcePolicy.ProductSellingModelId`**: These new lookups allow associating grants and policies with specific selling models. **High priority** — enables selling-model-specific usage grant configuration, which is a key 260 rating feature.
- **`RatingFrequencyPolicy.RatingDelayDurationUnit`**: Complements the existing `RatingDelayDuration` field with its unit (currently only duration value is captured). **Medium priority** — incomplete without the unit.
- **`UsageCommitmentPolicy.CommitmentRate`**: Controls commitment fulfillment rate behavior. **Medium priority** — the current SOQL only captures `Name`, missing the key functional field.

### Cross-Object Dependencies

| Lookup Target              | Source         | Status     |
|----------------------------|----------------|------------|
| Product2                   | qb-pcm         | Update only|
| UnitOfMeasure              | qb-pcm/this    | Upsert     |
| UnitOfMeasureClass         | qb-pcm/this    | Upsert     |
| UsageResourceBillingPolicy | qb-billing/this| Upsert     |
| UsageResource              | This plan      | Upsert     |
| UsageGrantRenewalPolicy    | This plan      | Upsert     |
| UsageGrantRolloverPolicy   | This plan      | Upsert     |
| UsageOveragePolicy         | This plan      | Upsert     |
| UsageCommitmentPolicy      | This plan      | Upsert     |
| RatingFrequencyPolicy      | This plan      | Upsert     |
| ProductSellingModel        | qb-pcm         | Not in plan (new ref) |

**Note:** The new `ProductSellingModelId` lookup on ProductUsageGrant and ProductUsageResourcePolicy references ProductSellingModel from qb-pcm. If these fields are populated, a Readonly ProductSellingModel entry may need to be added to this plan for lookup resolution.

## External ID / Composite Key Analysis (Confirmed via Org Describe)

### Schema-Enforced Unique Fields

| Object                     | Field  | isUnique | isIdLookup | Current ExternalId Uses It? |
|----------------------------|--------|----------|------------|------------------------------|
| UsageResource              | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |
| UsageResourceBillingPolicy | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |
| UsageGrantRenewalPolicy    | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |
| UsageGrantRolloverPolicy   | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |
| UnitOfMeasureClass         | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |

All schema-unique fields are already correctly used as externalIds.

### Fields NOT Schema-Unique but Used as ExternalId

| Object                  | Current ExternalId                  | Name AutoNum | isUnique | Risk |
|-------------------------|-------------------------------------|-------------|----------|------|
| UnitOfMeasure           | `UnitCode`                          | No*         | No*      | OK — likely platform-enforced when RLM enabled (verify) |
| UsageOveragePolicy      | `Name`                              | No          | No       | Low — 2 records |
| UsageCommitmentPolicy   | `Name`                              | No          | No       | Low — 1 record |
| UsagePrdGrantBindingPolicy | `Name;Product2.SKU`              | No          | No       | Low — 1 record |
| RatingFrequencyPolicy   | `RatingPeriod`                      | **Yes**     | No       | ⚠️ Picklist — only unique if 1 policy per period |

### Portability Concern: RatingFrequencyPolicy

`RatingFrequencyPolicy.RatingPeriod` is a **picklist** used as the sole externalId. This only works if there is exactly one policy per rating period value. Currently there is 1 record (RatingPeriod = some value), so it works. But if multiple policies per period are needed in the future, a composite key would be required (e.g., `RatingPeriod;Product.StockKeepingUnit;UsageResource.Code`).

**Note:** RatingFrequencyPolicy has auto-numbered Name (`autoNum=true`), so Name cannot be used as a portable alternative.

### Auto-Numbered Name Fields

| Object                       | Name Field Type          | Current ExternalId                                     | Assessment |
|------------------------------|--------------------------|--------------------------------------------------------|------------|
| ProductUsageResource         | `ProductUsageResourceNum` (auto-num) | `Product.StockKeepingUnit;UsageResource.Code` (Insert+deleteOldData — v5 can't match by traversal externalId) | ✅ Good |
| ProductUsageGrant            | `ProductUsageGrantNum` (auto-num) | 3-field composite: `UsageDefinitionProduct.StockKeepingUnit;UnitOfMeasureClass.Code;UnitOfMeasure.UnitCode` (Insert+deleteOldData) | ✅ Good |
| ProductUsageResourcePolicy   | `ProductUsageResourcePolicyNum` (auto-num) | `ProductUsageResourceId` (direct FK, 1:1 with PUR) + `deleteOldData:true` | ✅ Good — SFDMU v5 safe pattern for all-multi-hop externalIds |
| RatingFrequencyPolicy        | Auto-num                 | `RatingPeriod`                                          | ⚠️ Picklist only (see above) |

### Composite Key Complexity

| Object                       | Key Fields | Complexity | Simplification? |
|------------------------------|-----------|------------|-----------------|
| UnitOfMeasure                | 1 (`UnitCode`) | Simple | No |
| UnitOfMeasureClass           | 1 (`Code`) | Simple | No — schema-unique |
| UsageResource                | 1 (`Code`) | Simple | No — schema-unique |
| ProductUsageResource         | 2 (Product.StockKeepingUnit + UsageResource.Code) | Low | No — junction natural key |
| UsagePrdGrantBindingPolicy   | 2 (Name + Product2.SKU) | Low | No |
| ProductUsageResourcePolicy   | 1 (`ProductUsageResourceId` + `deleteOldData`) | Medium | No — SFDMU v5 requires direct field; `$$` composite caused SOQL injection |
| ProductUsageGrant            | **5** fields | **High** | No — all 5 required for uniqueness (grant per product per UoM per PUR) |

## Optimization Opportunities

1. **Add `ProductSellingModelId` to PUG and PURP SOQL**: New 260 field for selling-model-specific usage grants and policies. May require adding ProductSellingModel as Readonly in this plan.
2. **Add `CommitmentRate` to UsageCommitmentPolicy SOQL**: Key functional field missing from current query
3. **Add `RatingDelayDurationUnit` to RatingFrequencyPolicy SOQL**: Completes the delay duration configuration
4. **Investigate RatingFrequencyPolicy externalId**: If more policies per period are expected, switch to a composite key
5. **Fix `excludeIdsFromCSVFiles`**: Currently set to `"false"` — change to `"true"` for portability (same concern as qb-tax)
6. **Coordinate LegalEntity fields**: If qb-billing or qb-tax add LegalEntity geo/email fields, this plan's upstream dependencies should be kept in sync

## Known Limitations / Future Work

### TODO: Multi-Shape / Overlay Support

**Current limitation**: This plan uses `deleteOldData: true` with no WHERE clause on PUR, PURP, and PUG. That means each plan run deletes **all** records of each type and re-inserts only what is in these CSVs. The plan assumes it is the sole owner of all rating data on the org. Loading a second data shape (e.g., a different product family's rating config) on the same org will cause the first shape's records to be wiped on the next run of either plan.

**Requirements to investigate**:
1. **Fresh build from scratch with multiple shapes** — support composing any number of data shapes on the same org without shapes overwriting each other. Each shape should be independently loadable and re-runnable without affecting sibling shapes.
2. **Drift capture per shape** — extract modifications made to an org and identify drift against the shape's baseline CSVs. Must work even when multiple shapes coexist.
3. **Test and approval workflow** — verify extracted drift (diff against baseline), present for review, then decide:
   - **Merge into base shape**: update the shape's source CSVs and commit.
   - **Configure as overlay in a downstream CCI project**: keep the base shape unchanged and add shape-specific overrides in a child project.
4. **Downstream CCI overlay pattern** — investigate how to configure shape variants as overlays (additional plans, post-load Apex, or plan extensions) in downstream CCI projects that inherit this base.

**Alternatives to investigate**:
- **WHERE-clause scoped plans**: Filter deleteOldData by a discriminator (e.g., product family SKU prefix). SFDMU does not natively support dynamic WHERE on deleteOldData — would require pre-filtering CSVs or a wrapper task.
- **Shape-discriminated externalIds**: Tag each PUR/PUG with a shape identifier, scope deletes to only that shape's records.
- **Upsert-based approach**: Would eliminate the deleteOldData all-or-nothing problem, but requires SFDMU v5 traversal-externalId bug fixes (Bugs 2 & 3) or a workaround.
- **CCI project inheritance overlay**: Each shape defined as a separate plan in its own CCI project that extends this base, loaded in sequence after the base plan.
