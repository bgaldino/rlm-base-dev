# qb-rates Data Plan

SFDMU data plan for QuantumBit (QB) rate cards, rate card entries, and tiered rate adjustments. Defines the pricing rates used by the usage rating engine to calculate charges for QB products.

## CCI Integration

### Flow: `prepare_rating`

This plan is executed as **step 3** of the `prepare_rating` flow (when `rating=true`, `rates=true`, `qb=true`, and `refresh=false`).

| Step | Task                     | Description                                        |
|------|--------------------------|----------------------------------------------------|
| 1    | `insert_qb_rating_data`  | Runs the qb-rating SFDMU plan (prerequisite)       |
| 3    | `insert_qb_rates_data`   | **Runs this SFDMU plan (1 pass)**                  |
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
Pass 1 (SFDMU)               Apex Activation
─────────────────             ─────────────────
Insert/Upsert all        →   activateRateCardEntries.apex
objects in Draft status       (activate RateCardEntry)
```

### Pass 1 — Insert/Upsert with Draft Status

| # | Object               | Operation | External ID                                                                          | Records |
|---|----------------------|-----------|--------------------------------------------------------------------------------------|---------|
| 1 | Product2             | Update    | `StockKeepingUnit`                                                                   | 165     |
| 2 | RateCard             | Upsert    | `Name;Type`                                                                          | 3       |
| 3 | PriceBookRateCard    | Upsert    | `PriceBook.Name;RateCard.Name;RateCardType`                                          | 3       |
| 4 | RateCardEntry        | Upsert    | `Product.StockKeepingUnit;RateCard.Name;UsageResource.Code;RateUnitOfMeasure.UnitCode` | 19     |
| 5 | RateAdjustmentByTier | Upsert    | `Product.StockKeepingUnit;RateCardEntry.Name;RateUnitOfMeasure.UnitCode;UsageResource.Code;LowerBound;UpperBound` | 22 |

**Note:** Product2 is an `Update` operation — it only sets `UsageModelType` on existing products (created by qb-pcm). RateCardEntry records are inserted in `Draft` status and activated via Apex.

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

## File Structure

```
qb-rates/
├── export.json                # SFDMU data plan (1 pass)
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
- **RateAdjustmentByTier** uses a 6-field composite external ID (`Product.StockKeepingUnit;RateCardEntry.Name;RateUnitOfMeasure.UnitCode;UsageResource.Code;LowerBound;UpperBound`) ensuring each tier range is unique.
- **Product2** uses `Update` by `StockKeepingUnit`, so only existing products are modified.
