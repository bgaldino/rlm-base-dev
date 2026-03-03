# qb-rates Data Plan

SFDMU data plan for QuantumBit (QB) rate cards, rate card entries, and tiered rate adjustments. Defines the pricing rates used by the usage rating engine to calculate charges for QB products.

## CCI Integration

### Flow: `prepare_rating`

This plan is executed as **step 3** of the `prepare_rating` flow (when `rating=true`, `rates=true`, `qb=true`, and `refresh=false`).

| Step | Task                     | Description                                        |
|------|--------------------------|----------------------------------------------------|
| 1    | `insert_qb_rating_data`  | Runs the qb-rating SFDMU plan (prerequisite)       |
| 3    | `insert_qb_rates_data`   | **Runs this plan** (single pass — all objects)     |
| 5    | `activate_rating_records`| Runs `activateRatingRecords.apex`                  |
| 6    | `activate_rates`         | Runs `activateRateCardEntries.apex`                |

### Task Definition

```yaml
insert_qb_rates_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-rates"
```

## Data Plan Overview

The plan uses a **single SFDMU pass** followed by **Apex activation**:

```
SFDMU (single pass)                          Apex Activation
──────────────────────────────               ─────────────────
RateCard, RateCardEntry (Draft),         ->  activate_rates
PriceBookRateCard, RateAdjustmentByTier      (RateCardEntry -> Active)
```

**Key constraint:** RateAdjustmentByTier (RABT) must be inserted while its parent RateCardEntry is in `Draft` status. SFDMU processes objects in dependency order within the single pass, so RABT is inserted before any activation occurs.

### Objects

| # | Object               | Operation | External ID                                                                          | Records |
|---|----------------------|-----------|--------------------------------------------------------------------------------------|---------|
| 1 | Product2             | Update    | `StockKeepingUnit`                                                                   | 164     |
| 2 | RateCard             | Upsert    | `Name;Type`                                                                          | 3       |
| 3 | PriceBookRateCard    | Upsert    | `PriceBook.Name;RateCard.Name;RateCardType`                                          | 2       |
| 4 | RateCardEntry        | Upsert    | `Product.StockKeepingUnit;RateCard.Name;UsageResource.Code;RateUnitOfMeasure.UnitCode` | 19     |
| 5 | RateAdjustmentByTier | Upsert    | `Product.StockKeepingUnit;RateCard.Name;RateUnitOfMeasure.UnitCode;UsageResource.Code;LowerBound;UpperBound` | 21 |

**Note:** Product2 is an `Update` operation — it only sets `UsageModelType` on existing products (created by qb-pcm). RateCardEntry records are inserted in `Draft` status. RateAdjustmentByTier uses `RateCard.Name` (portable) in its composite key instead of `RateCardEntry.Name` (auto-numbered), with a separate `RateCardEntry.$$...` column in the CSV for parent RCE lookup resolution.

### Lookup Reference CSVs

The following CSVs are included for SFDMU lookup resolution only (they are not loaded as separate objects):

| File                   | Purpose                                                |
|------------------------|--------------------------------------------------------|
| Pricebook2.csv         | Standard Price Book reference for PriceBookRateCard    |
| ProductSellingModel.csv| Selling model names referenced by RateCardEntry        |
| UnitOfMeasure.csv      | UoM references for rate units                          |
| UnitOfMeasureClass.csv | UoM class references for default/rate UoM classes      |
| UsageResource.csv      | Usage resource references for RateCardEntry            |

## Apex Activation Script

**File:** `scripts/apex/activateRateCardEntries.apex`

Simple activation — queries all `RateCardEntry` records with `Status != 'Active'` and sets them to `Active`:

```apex
List<RateCardEntry> rates = [SELECT Id, Status FROM RateCardEntry WHERE Status != 'Active'];
for (RateCardEntry rate : rates) {
    rate.Status = 'Active';
}
update rates;
```

The script is **idempotent** — re-running on already-activated entries is a safe no-op.

## Rate Cards

3 rate cards define the pricing structure:

| Name            | Type      | Effective From | Description                          |
|-----------------|-----------|----------------|--------------------------------------|
| Attribute Rate  | Attribute | 2024-12-01     | Attribute-based rate card             |
| Base Rate Card  | Base      | 2023-01-01     | Flat per-unit base rates              |
| Tier Rate Card  | Tier      | 2023-01-01     | Volume tier-based rate adjustments    |

### PriceBook Associations

| Price Book           | Rate Card       | Type |
|----------------------|-----------------|------|
| Standard Price Book  | Base Rate Card  | —    |
| Standard Price Book  | Tier Rate Card  | —    |

## Rate Card Entries (19 records)

### Base Rate Card Entries (flat per-unit rates)

| Product SKU      | Resource        | Rate UoM | Rate     |
|------------------|-----------------|----------|----------|
| QB-DB            | UR-CPUTIME      | USD      | $0.004   |
| QB-DB            | UR-DATASTORAGE  | USD      | $10.00   |
| QB-DB-TOKEN      | QB-TOKEN        | USD      | $0.50    |
| QB-DB-TOKEN      | UR-CPUTIME      | TOKEN-UOM| 5 tokens |
| QB-DB-TOKEN      | UR-DATASTORAGE  | TOKEN-UOM| 10 tokens|
| QB-TOKENS-PACK   | QB-TOKEN        | USD      | $0.33    |

### Tier Rate Card Entries (rate determined by RateAdjustmentByTier)

| Product SKU      | Resource        | Rate UoM  | Selling Model |
|------------------|-----------------|-----------|---------------|
| QB-DB            | UR-CPUTIME      | USD       | Term Annual   |
| QB-DB            | UR-DATASTORAGE  | USD       | Term Annual   |
| QB-CMT-TKN-EACH | QB-TOKEN        | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-EACH | UR-CPUTIME      | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-EACH | UR-DATASTORAGE  | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-FLAT | (no resource)   | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-FLAT | QB-TOKEN        | USD       | Term Annual   |
| QB-CMT-TKN-TIER | (no resource)   | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-TIER | QB-TOKEN        | USD       | Term Annual   |
| QB-MTY-CMT       | UR-CPUTIME      | USD       | Term Annual   |
| QB-MTY-CMT       | UR-DATASTORAGE  | USD       | Term Annual   |
| QB-QTY-CMT       | UR-CPUTIME      | USD       | Term Annual   |
| QB-QTY-CMT       | UR-DATASTORAGE  | USD       | Term Annual   |

## Rate Adjustments by Tier (21 records)

### QB-DB — Compute Time (Override tiers, USD/minute)

| Lower Bound | Upper Bound | Type     | Value    |
|-------------|-------------|----------|----------|
| 1           | 100         | Override | $0.004   |
| 100         | 200         | Override | $0.0045  |
| 200         | 300         | Override | $0.005   |
| 300         | 999999999   | Override | $0.006   |

### QB-DB — Data Storage (mixed tiers, USD/TB)

| Lower Bound | Upper Bound | Type       | Value   |
|-------------|-------------|------------|---------|
| 1           | 100         | Percentage | 0%      |
| 100         | 500         | Override   | $12.50  |
| 500         | 5000        | Override   | $15.00  |
| 5000        | 999999999   | Override   | $18.00  |

### QB-CMT-TKN-EACH (Percentage tiers per resource)

| Resource        | Adjustment |
|-----------------|------------|
| UR-CPUTIME      | 5%         |
| UR-DATASTORAGE  | 4%         |
| QB-TOKEN        | 6%         |

### QB-CMT-TKN-FLAT (Percentage tiers)

| Resource   | Adjustment |
|------------|------------|
| (flat)     | 10%        |
| QB-TOKEN   | 0%         |

### QB-CMT-TKN-TIER (Volume tiers, tokens)

| Lower Bound | Upper Bound | Adjustment |
|-------------|-------------|------------|
| 0           | 1000        | 10%        |
| 1000        | 5000        | 20%        |
| 5000        | (unlimited) | 30%        |
| QB-TOKEN    | —           | 0%         |

### Commitment Products (Percentage tiers)

| Product   | Resource        | Adjustment |
|-----------|-----------------|------------|
| QB-MTY-CMT| UR-DATASTORAGE  | 10%        |
| QB-MTY-CMT| UR-CPUTIME      | 5%         |
| QB-QTY-CMT| UR-CPUTIME      | 10%        |
| QB-QTY-CMT| UR-DATASTORAGE  | 20%        |

## Product Selling Models

| Name        | Description                    |
|-------------|--------------------------------|
| One-Time    | One-time purchase (token packs)|
| Term Annual | Annual term subscription       |

## Data Extraction

This plan supports **bidirectional** operation: in addition to importing data (CSV > org), it can extract data from any org into portable CSVs.

### Extraction via CCI

```bash
# Extract rates data from the current default org
cci task run extract_qb_rates_data

# Or use the extract_rating flow to extract both rating and rates
cci flow run extract_rating

# Run all QB extract tasks (includes rates)
cci flow run run_qb_extracts --org <org>
```

To run the idempotency test for this plan: `cci task run test_qb_rates_idempotency --org <org>`. To run all QB idempotency tests: `cci flow run run_qb_idempotency_tests --org <org>`. Tasks are in the **Data Management - Extract** and **Data Management - Idempotency** groups.

### Post-Processing

```bash
# Diff only (compare extraction against current plan)
python3 scripts/post_process_extraction.py <extraction-dir> datasets/sfdmu/qb/en-US/qb-rates --diff-only

# Process and write import-ready CSVs
python3 scripts/post_process_extraction.py <extraction-dir> datasets/sfdmu/qb/en-US/qb-rates --output-dir <output-dir>
```

### Dual-Purpose SOQL Queries

The SOQL queries in `export.json` include relationship traversal fields (e.g., `Product.StockKeepingUnit`, `RateCard.Name`, `UsageResource.Code`) alongside raw ID fields. During **import**, SFDMU uses these for lookup resolution. During **extraction**, these fields are populated with human-readable values, producing portable CSVs without raw Salesforce IDs.

## File Structure

```
qb-rates/
├── export.json                # SFDMU data plan (single pass)
├── README.md                  # This file
│
│  Source CSVs (data to load)
├── Product2.csv               # 165 records (Update UsageModelType only)
├── RateCard.csv               # 3 records
├── PriceBookRateCard.csv      # 3 records
├── RateCardEntry.csv          # 19 records (Draft status)
├── RateAdjustmentByTier.csv   # 21 records
│
│  Lookup Reference CSVs (for SFDMU resolution)
├── Pricebook2.csv             # Standard Price Book
├── ProductSellingModel.csv    # One-Time, Term Annual
├── UnitOfMeasure.csv          # Token, USD, Minutes, TB
├── UnitOfMeasureClass.csv     # Token, Currency, Time, Data Volume
├── UsageResource.csv          # QB-TOKEN, UR-CPUTIME, UR-DATASTORAGE
│
│  SFDMU Runtime (gitignored)
├── source/                    # SFDMU-generated source snapshots
└── target/                    # SFDMU-generated target snapshots
```

## Dependencies

This plan depends on the following having been loaded first:

- **qb-pcm** — Product2 records, UnitOfMeasure, UnitOfMeasureClass, ProductSellingModel, Pricebook2
- **qb-rating** — UsageResource (with categories and token references), ProductUsageResource (PUR associations required for rate card entry context)

## Idempotency

> **SFDMU v5 Required.** All externalId definitions and CSV formats are optimized for SFDMU v5.

- **RateCard** uses `Upsert` with `Name;Type` composite key — matches correctly on re-run.
- **PriceBookRateCard**, **RateCardEntry**, **RateAdjustmentByTier** use `deleteOldData: true` for idempotency. These objects have auto-number Names and all-relationship externalIds that SFDMU v5 cannot match against existing target records. On re-run, records are deleted and reinserted (functional idempotency with stable counts).
- **Product2** uses `Update` by `StockKeepingUnit`, so only existing products are modified.

**Key requirement (SFDMU v5):** Objects with multi-component composite `externalId` definitions require a `$$` column in the source CSV for SFDMU to correctly match records during Upsert. The column name uses `$` between field names (e.g., `$$Field1$Field2`), and values use `;` between component values. Without this column, SFDMU inserts duplicates on re-runs. For objects where a `$$` column cannot be used (e.g., auto-number `Name` fields with all-relationship externalIds), use `deleteOldData: true` for functional idempotency. See [Composite Key Optimizations](../../../../../docs/sfdmu_composite_key_optimizations.md) for the full v5 migration guide.

## 260 Schema Analysis (Confirmed via Org Describe)

Schema was queried against a 260 scratch org. Findings below.

### Polymorphic Fields

**None found.** All reference fields on rate objects are single-target lookups.

### Self-Referencing Fields

**None found.**

### Schema Concerns

**`RateCard.Status` — NOT in 260 schema!**

The current SOQL query includes `Status`:
```sql
SELECT Description, EffectiveFrom, EffectiveTo, Name, Status, Type FROM RateCard ORDER BY Name ASC
```

However, the 260 schema describe for `RateCard` returns only:

| Field          | Type     | Updateable | In Current SOQL? |
|----------------|----------|------------|-------------------|
| `Name`         | STRING   | Yes        | Yes               |
| `Description`  | STRING   | Yes        | Yes               |
| `Type`         | PICKLIST | Yes        | Yes               |
| `EffectiveFrom`| DATETIME | Yes        | Yes               |
| `EffectiveTo`  | DATETIME | Yes        | Yes               |

**`Status` is not a field on `RateCard` in 260.** This was also confirmed in prior testing (error: "No such column 'Status' on entity 'RateCard'"). The SOQL query includes it but the field does not exist — SFDMU may handle this gracefully by ignoring unknown fields, or it may cause an error. **Needs urgent validation.**

**Note:** `RateCardEntry` *does* have a `Status` field (confirmed in schema), so the confusion may be between the two objects.

### Field Coverage Audit

| Object               | Status | Notes                                                    |
|----------------------|--------|----------------------------------------------------------|
| Product2             | ✅     | Update only (UsageModelType) — correct                   |
| RateCard             | ⚠️     | `Status` field not in 260 schema — must be removed       |
| PriceBookRateCard    | ✅     | All fields present (Name auto-generated, read-only)      |
| RateCardEntry        | ✅     | All fields present including Status, RateNegotiation     |
| RateAdjustmentByTier | ✅     | All updateable fields present (4: AdjType, AdjValue, LB, UB) |

### RateCardEntry — Read-Only Field Analysis

RateCardEntry SOQL includes several fields that are **read-only** (`updateable=false`) in the schema:

| Field                         | Updateable | Notes                                        |
|-------------------------------|------------|----------------------------------------------|
| `DefaultUnitOfMeasureClassId` | No         | Auto-populated from UsageResource             |
| `DefaultUnitOfMeasureId`      | No         | Auto-populated from UsageResource             |
| `RateUnitOfMeasureClassId`    | No         | Auto-populated from RateUnitOfMeasure         |
| `UsageProductId`              | No         | Auto-populated                                |

These read-only fields are correctly included in the SOQL for **extraction** purposes (they produce meaningful values in exported CSVs) but SFDMU will skip them during Upsert/Update operations.

### RateAdjustmentByTier — Read-Only Field Analysis

Most RABT fields are **read-only** — auto-populated from the parent RateCardEntry:

| Field                  | Updateable | Notes                                        |
|------------------------|------------|----------------------------------------------|
| `RateCardEntryId`      | No         | Parent lookup (set at insert)                |
| `RateCardEntryStatus`  | No         | Mirrors parent RCE status                     |
| `RateCardId`           | No         | Auto-populated from parent RCE               |
| `UsageResourceId`      | No         | Auto-populated from parent RCE               |
| `ProductId`            | No         | Auto-populated from parent RCE               |
| `EffectiveFrom`        | No         | Auto-populated from parent RCE               |
| `EffectiveTo`          | No         | Auto-populated from parent RCE               |
| `RateUnitOfMeasureId`  | No         | Auto-populated from parent RCE               |
| `RateUnitOfMeasureName`| No         | Auto-populated                                |
| `ProductSellingModelId`| No         | Auto-populated from parent RCE               |

Only 4 fields are updateable: `AdjustmentType`, `AdjustmentValue`, `LowerBound`, `UpperBound`. All are in the current SOQL.

### Cross-Object Dependencies

| Lookup Target        | Source       | Status     |
|----------------------|--------------|------------|
| Product2             | qb-pcm       | Update only|
| UnitOfMeasure        | qb-pcm       | Lookup CSV |
| UnitOfMeasureClass   | qb-pcm       | Lookup CSV |
| ProductSellingModel  | qb-pcm       | Lookup CSV |
| UsageResource        | qb-rating    | Lookup CSV |
| Pricebook2           | qb-pricing   | Lookup CSV |
| RateCard             | This plan    | Upsert     |
| RateCardEntry        | This plan    | Upsert     |

## External ID / Composite Key Analysis (Confirmed via Org Describe)

### Schema-Enforced Unique Fields

**None found.** No rates objects have schema-enforced unique fields.

### Auto-Numbered Name Fields

| Object               | Name Auto-Num | Current ExternalId                                                       | Assessment |
|----------------------|---------------|--------------------------------------------------------------------------|------------|
| RateCardEntry        | **Yes**       | `Product.SKU;RateCard.Name;UsageResource.Code;RateUnitOfMeasure.UnitCode` | ✅ Good — 4-field composite from parents |
| RateAdjustmentByTier | **Yes**       | `Product.SKU;RateCard.Name;RateUoM.UnitCode;UsageResource.Code;LowerBound;UpperBound` | ✅ Good — 6-field composite |
| PriceBookRateCard    | **Yes**       | `PriceBook.Name;RateCard.Name;RateCardType`                              | ✅ Good — all parent refs |

### ExternalId Assessment

| Object               | Current ExternalId                  | isUnique | Assessment |
|----------------------|-------------------------------------|----------|------------|
| Product2             | `StockKeepingUnit`                  | No*      | ✅ OK — platform-enforced unique when RLM enabled |
| RateCard             | `Name;Type`                         | No       | ✅ OK — 2-field composite, few records |
| PriceBookRateCard    | `PriceBook.Name;RateCard.Name;Type` | No       | ✅ OK — 3-field composite |
| RateCardEntry        | 4-field composite                   | No       | ✅ OK — comprehensive |
| RateAdjustmentByTier | 6-field composite                   | No       | ✅ OK — tier bounds ensure uniqueness |

### Composite Key Complexity

| Object               | Key Fields | Complexity | Simplification? |
|----------------------|-----------|------------|-----------------|
| RateCard             | 2 (Name + Type) | Low | No — Name alone may not be unique across types |
| PriceBookRateCard    | 3 fields | Medium | No — junction natural key |
| RateCardEntry        | 4 fields | Medium | No — Product + RateCard + Resource + UoM is the natural key |
| RateAdjustmentByTier | **6** fields | **High** | Possible — investigate if `RateCardEntry.Name + LowerBound + UpperBound` could work, but RCE.Name is auto-num |

The 6-field RABT key avoids using `RateCardEntry.Name` (auto-numbered) by instead using the RCE's natural key components (Product.SKU, RateCard.Name, Resource.Code, UoM.UnitCode) plus the tier bounds. This is the correct portable approach.

## Optimization Opportunities

1. **Remove `Status` from RateCard SOQL**: Field does not exist in 260 schema — must be removed to prevent query errors
2. **Fix `excludeIdsFromCSVFiles`**: Currently set to `"false"` — change to `"true"` for portability
3. **Validate RateCard.Status in CSV**: Check if `RateCard.csv` has a Status column and remove it if present
4. **Document read-only field strategy**: Many RABT and RCE fields are read-only (auto-populated) but included in SOQL for extraction — document this dual-purpose pattern clearly
