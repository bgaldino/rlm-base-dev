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

The plan uses **2 SFDMU passes** followed by **Apex activation**:

```
Pass 1 (SFDMU)          Pass 2 (SFDMU)         Apex Activation
─────────────────        ─────────────────      ─────────────────
Insert/Upsert all   ->  Activate UoMClass  ->  activateRatingRecords.apex
objects in Draft         and UsageResource       (7-step PUR/PUG activation)
```

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
| 10| ProductUsageResource         | Upsert    | `Product.StockKeepingUnit;UsageResource.Code`        | 20      |
| 11| UsagePrdGrantBindingPolicy   | Upsert    | `Name;Product2.StockKeepingUnit`                     | 1       |
| 12| RatingFrequencyPolicy        | Upsert    | `RatingPeriod`                                       | 1       |
| 13| ProductUsageResourcePolicy   | Upsert    | `ProductUsageResource.$$Product.StockKeepingUnit$UsageResource.Code` | 17      |
| 14| ProductUsageGrant            | Upsert    | `UsageDefinitionProduct.StockKeepingUnit;UnitOfMeasureClass.Code;UnitOfMeasure.UnitCode;ProductUsageResource.Product.StockKeepingUnit;ProductUsageResource.UsageResource.Code` | 17      |

**Composite keys for PURP and PUG:** These objects reference their parent ProductUsageResource (which has a composite externalId) for portable cross-org compatibility. ProductUsageResourcePolicy uses `$$` composite key notation as its sole externalId (SFDMU expands this to individual SOQL fields). ProductUsageGrant uses individual relationship traversal fields in its externalId (avoids `$$` in multi-component externalIds which breaks SOQL), with a separate `$$` column in the CSV for parent resolution. ProductUsageResourcePolicy is uniquely identified by its parent PUR (17 rows, 17 unique keys). ProductUsageGrant requires 5 fields for uniqueness: the usage definition product, UoM class, UoM, and the parent PUR's product and resource.

### Pass 2 — Activate UnitOfMeasureClass and UsageResource

| # | Object             | Operation | External ID | Records |
|---|--------------------|-----------|-------------|---------|
| 1 | UnitOfMeasureClass | Update    | `Code`      | 5       |
| 2 | UsageResource      | Update    | `Code`      | 5       |

Only UoMClass and UsageResource are activated in SFDMU Pass 2. PUR and PUG activation requires the Apex script (`activate_rating_records`) which enforces a strict dependency order — Token PURs must be Active before non-Token usage PURs, and all PURs must be Active before PUGs.

## Apex Activation Script

**File:** `scripts/apex/activateRatingRecords.apex`

PUR and PUG activation follows a strict 7-step dependency order:

| Step | What                                      | Why                                                                |
|------|-------------------------------------------|--------------------------------------------------------------------|
| 1    | UnitOfMeasureClass -> Active              | Safety net (Pass 2 should already do this)                         |
| 2    | UsageResource -> Active                   | Safety net (Pass 2 should already do this, including QB-TOKEN)     |
| 2.5  | Remove duplicate PURs                     | Same Product+UsageResource+overlapping effective period — keeps one, deletes Draft dupes + PUG/PURP children. Overlap uses DateTime (not Date) so same-day different-time periods are not incorrectly treated as duplicates. Prevents "effective period overlaps" when re-running the flow. |
| 3    | Pre-populate TokenResourceId on Draft PURs| Ensures clear+activate works in Step 5 (see below)                 |
| 4    | Token PUR -> Active                       | Must precede Step 5; products with Token PURs require them Active before usage PURs can activate |
| 5    | ALL non-Token PUR -> clear+activate       | TokenResourceId=null + Status='Active' in single DML               |
| 6    | ProductUsageGrant -> Active               | Depends on parent PUR being active                                 |

**Step 3 explained:** Some PURs (QB-DB;UR-\*, QB-QTY-CMT;UR-\*) don't get `TokenResourceId` auto-populated at SFDMU insert time. The clear+activate workaround in Step 5 only prevents auto-population when `TokenResourceId` changes from a non-null value to null -- a null-to-null assignment is a no-op that doesn't block auto-population. Step 3 pre-populates `TokenResourceId` from `UsageResource.TokenResourceId` on these Draft PURs so that Step 5's clear is a real change.

The script is **idempotent** — Step 2.5 queries all PURs (Active + non-Active) to detect overlapping duplicates; all other steps and DML filter on `Status != 'Active'`. Re-running on an already-activated org is a safe no-op.

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
cci flow run run_qb_extracts --org <org>
```

To run the idempotency test for this plan: `cci task run test_qb_rating_idempotency --org <org>`. To run all QB idempotency tests: `cci flow run run_qb_idempotency_tests --org <org>`. Tasks are in the **Data Management - Extract** and **Data Management - Idempotency** groups.

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

The SOQL queries in `export.json` include both raw ID fields (e.g., `ProductId`) and relationship traversal fields (e.g., `Product.StockKeepingUnit`). During **import**, SFDMU uses the traversal fields for lookup resolution. During **extraction**, SFDMU populates these fields with human-readable values (names, codes, SKUs) instead of raw Salesforce IDs, producing portable CSVs.

## Idempotency

This plan is **idempotent**. Re-running `insert_qb_rating_data` on an org that already has the data will match all existing records via composite external IDs and leave them untouched (zero new inserts). This was verified on API 260 scratch orgs with records in both Draft and Active states.

**Key requirement:** Objects with multi-component composite `externalId` definitions (ProductUsageGrant, ProductUsageResourcePolicy, ProductUsageResource, UsagePrdGrantBindingPolicy) require a `$$` column in the source CSV for SFDMU to correctly match records during Upsert. The column name uses `$` between field names (e.g., `$$Field1$Field2`), and values use `;` between component values (e.g., `val1;val2`). Without this column, SFDMU inserts duplicates on re-runs. SFDMU auto-generates these columns during extraction.

## Cleanup / Re-run

Two cleanup scripts are available:

```bash
# Full cleanup — deletes PUG, PURP, PUR, and policies in reverse dependency order
cci task run execute_anon --path scripts/apex/deleteQbRatingData.apex --org <alias>

# Legacy cleanup — similar scope, different implementation
cci task run execute_anon --path scripts/apex/cleanupRatingRecords.apex --org <alias>
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
| ProductUsageResource         | `ProductUsageResourceNum` (auto-num) | `Product.SKU;UsageResource.Code`           | ✅ Good — both parents have portable keys |
| ProductUsageGrant            | `ProductUsageGrantNum` (auto-num) | 5-field composite from parents               | ✅ Good — comprehensive |
| ProductUsageResourcePolicy   | `ProductUsageResourcePolicyNum` (auto-num) | `ProductUsageResource.$$Product.SKU$UsageResource.Code` | ✅ Good — references parent composite |
| RatingFrequencyPolicy        | Auto-num                 | `RatingPeriod`                                          | ⚠️ Picklist only (see above) |

### Composite Key Complexity

| Object                       | Key Fields | Complexity | Simplification? |
|------------------------------|-----------|------------|-----------------|
| UnitOfMeasure                | 1 (`UnitCode`) | Simple | No |
| UnitOfMeasureClass           | 1 (`Code`) | Simple | No — schema-unique |
| UsageResource                | 1 (`Code`) | Simple | No — schema-unique |
| ProductUsageResource         | 2 (Product.SKU + Resource.Code) | Low | No — junction natural key |
| UsagePrdGrantBindingPolicy   | 2 (Name + Product2.SKU) | Low | No |
| ProductUsageResourcePolicy   | 1 (parent PUR's `$$` composite) | Medium | No — correct SFDMU pattern |
| ProductUsageGrant            | **5** fields | **High** | No — all 5 required for uniqueness (grant per product per UoM per PUR) |

## Optimization Opportunities

1. **Add `ProductSellingModelId` to PUG and PURP SOQL**: New 260 field for selling-model-specific usage grants and policies. May require adding ProductSellingModel as Readonly in this plan.
2. **Add `CommitmentRate` to UsageCommitmentPolicy SOQL**: Key functional field missing from current query
3. **Add `RatingDelayDurationUnit` to RatingFrequencyPolicy SOQL**: Completes the delay duration configuration
4. **Investigate RatingFrequencyPolicy externalId**: If more policies per period are expected, switch to a composite key
5. **Fix `excludeIdsFromCSVFiles`**: Currently set to `"false"` — change to `"true"` for portability (same concern as qb-tax)
6. **Coordinate LegalEntity fields**: If qb-billing or qb-tax add LegalEntity geo/email fields, this plan's upstream dependencies should be kept in sync
