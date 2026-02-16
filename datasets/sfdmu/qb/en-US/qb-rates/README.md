# qb-rates Data Plan

SFDMU data plan for QuantumBit (QB) rate cards, rate card entries, and tiered rate adjustments. Defines the pricing rates used by the usage rating engine to calculate charges for QB products.

## CCI Integration

### Flow: `prepare_rating`

This plan is executed as **step 3** of the `prepare_rating` flow (when `rating=true`, `rates=true`, `qb=true`, and `refresh=false`).

| Step | Task                     | Description                                        |
|------|--------------------------|----------------------------------------------------|
| 1    | `insert_qb_rating_data`  | Runs the qb-rating SFDMU plan (prerequisite)       |
| 3    | `insert_qb_rates_data`   | **Runs this plan Pass 1** (`object_sets: [0]`)     |
| 5    | `activate_rating_records`| Runs `activateRatingRecords.apex`                  |
| 6    | `activate_rates`         | Runs `activateRateCardEntries.apex`                |
| 7    | `insert_qb_rates_data`   | **Runs this plan Pass 2** (`object_sets: [1]`) — RABT |

### Task Definition

```yaml
insert_qb_rates_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-rates"
```

## Data Plan Overview

The plan uses **2 SFDMU passes** with **Apex activation** between them:

```
Pass 1 (SFDMU)               Apex Activation            Pass 2 (SFDMU)
-----------------             -----------------          -----------------
RateCard, RateCardEntry  ->  activate_rates           -> RateAdjustmentByTier
(Draft), PriceBookRateCard   (RateCardEntry > Active)    (requires Active RCE)
```

### Pass 1 — RateCard, RateCardEntry (Draft), PriceBookRateCard

| # | Object               | Operation | External ID                                                                          | Records |
|---|----------------------|-----------|--------------------------------------------------------------------------------------|---------|
| 1 | Product2             | Update    | `StockKeepingUnit`                                                                   | 165     |
| 2 | RateCard             | Upsert    | `Name;Type`                                                                          | 3       |
| 3 | PriceBookRateCard    | Upsert    | `PriceBook.Name;RateCard.Name;RateCardType`                                          | 3       |
| 4 | RateCardEntry        | Upsert    | `Product.StockKeepingUnit;RateCard.Name;UsageResource.Code;RateUnitOfMeasure.UnitCode` | 19     |

**Note:** Product2 is an `Update` operation -- it only sets `UsageModelType` on existing products (created by qb-pcm). RateCardEntry records are inserted in `Draft` status and activated via Apex before Pass 2 can run.

### Pass 2 — RateAdjustmentByTier (requires Active RateCardEntry)

| # | Object               | Operation | External ID                                                                          | Records |
|---|----------------------|-----------|--------------------------------------------------------------------------------------|---------|
| 1 | Product2             | Readonly  | `StockKeepingUnit`                                                                   | —       |
| 2 | RateCard             | Readonly  | `Name;Type`                                                                          | —       |
| 3 | UnitOfMeasure        | Readonly  | `UnitCode`                                                                           | —       |
| 4 | UsageResource        | Readonly  | `Code`                                                                               | —       |
| 5 | RateCardEntry        | Readonly  | `Product.StockKeepingUnit;RateCard.Name;UsageResource.Code;RateUnitOfMeasure.UnitCode` | —     |
| 6 | RateAdjustmentByTier | Upsert    | `Product.StockKeepingUnit;RateCard.Name;RateUnitOfMeasure.UnitCode;UsageResource.Code;LowerBound;UpperBound` | 22 |

**Note:** Readonly parent objects in Pass 2 provide SFDMU with correct externalIds for parent lookup resolution when this object set runs independently via `object_sets` filtering. RateAdjustmentByTier uses individual relationship traversal fields in its externalId, with a `$$` column in the CSV for idempotent matching and a separate `RateCardEntry.$$...` column for parent resolution.

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

## Rate Adjustments by Tier (22 records)

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
```

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
├── export.json                # SFDMU data plan (2 passes)
├── README.md                  # This file
│
│  Source CSVs (data to load)
├── Product2.csv               # 165 records (Update UsageModelType only)
├── RateCard.csv               # 3 records
├── PriceBookRateCard.csv      # 3 records
├── RateCardEntry.csv          # 19 records (Draft status)
├── RateAdjustmentByTier.csv   # 22 records
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

- **RateCard**, **PriceBookRateCard**, and **RateCardEntry** use `Upsert` with composite external IDs, so re-runs update existing records rather than creating duplicates.
- **RateAdjustmentByTier** uses a 6-field composite external ID (`Product.StockKeepingUnit;RateCard.Name;RateUnitOfMeasure.UnitCode;UsageResource.Code;LowerBound;UpperBound`) ensuring each tier range is unique. The parent RateCardEntry is resolved via a `$$` composite column in the CSV (`RateCardEntry.$$Product.StockKeepingUnit$RateCard.Name$UsageResource.Code$RateUnitOfMeasure.UnitCode`) alongside individual relationship columns. The externalId uses individual fields (not `$$` notation) to avoid SOQL parse errors in multi-component externalIds.
- **Product2** uses `Update` by `StockKeepingUnit`, so only existing products are modified.

**Key requirement:** Objects with multi-component composite `externalId` definitions require a `$$` column in the source CSV for SFDMU to correctly match records during Upsert. The column name uses `$` between field names (e.g., `$$Field1$Field2`), and values use `;` between component values. Without this column, SFDMU inserts duplicates on re-runs. SFDMU auto-generates these columns during extraction.
