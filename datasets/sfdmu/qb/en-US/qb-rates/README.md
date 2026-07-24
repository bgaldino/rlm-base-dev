# qb-rates Data Plan

SFDMU data plan for QuantumBit (QB) rate cards, rate card entries, and tiered rate adjustments. Defines the pricing rates used by the usage rating engine to calculate charges for QB products.

> **SFDMU 5.6.4+ floor.** RateCardEntry and RateAdjustmentByTier use `Insert` + `deleteOldData: true`, and PriceBookRateCard uses `Upsert` + `deleteOldData: true` — pre-5.6.4 workarounds for relationship-traversal externalId matching (multi-hop traversal keys produced invalid Upsert SOQL; all-traversal composite keys never matched target records). Those bugs are **fixed at/below the 5.6.4 floor**; the shipped plan keeps the workarounds deliberately. Restoring plain `Upsert` / dropping `deleteOldData` is the gated `sfdmu-v5-optimization` initiative — do not flip operations without live verification and explicit approval.

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
| 1 | Product2             | Update    | `StockKeepingUnit`                                                                   | 9       |
| 2 | RateCard             | Upsert    | `Name;Type`                                                                          | 3       |
| 3 | PriceBookRateCard    | Upsert (+deleteOldData) | `PriceBook.Name;RateCard.Name;RateCardType`                                          | 2       |
| 4 | RateCardEntry        | Insert (+deleteOldData) | `Product.StockKeepingUnit;RateCard.Name;UsageResource.Code;RateUnitOfMeasure.UnitCode` | 116    |
| 5 | RateAdjustmentByTier | Insert (+deleteOldData) | `Product.StockKeepingUnit;RateCardEntry.RateCard.Name;RateUnitOfMeasure.UnitCode;UsageResource.Code;LowerBound;UpperBound` | 118 |

**Note:** Product2 is an `Update` operation — it only sets `UsageModelType` on existing products (created by qb-pcm). RateCardEntry records are inserted in `Draft` status. RateAdjustmentByTier keys on `RateCardEntry.RateCard.Name` (traversing the parent RateCardEntry to its RateCard's portable `Name`) instead of `RateCardEntry.Name` (auto-numbered), with a separate `RateCardEntry.$$...` column in the CSV for parent RCE lookup resolution.

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

## Multicurrency: the rate's currency is its `RateUnitOfMeasure`

**No rate object has a `CurrencyIsoCode`.** A rate is denominated by its
`RateUnitOfMeasure` — a unit in the **`CURRENCY`** `UnitOfMeasureClass`. So a GBP
quote can only rate if a **GBP-denominated `RateCardEntry` exists**; there is no
runtime conversion from the USD entry. Each currency therefore needs:

1. a `CURRENCY`-class `UnitOfMeasure` whose `UnitCode` is the ISO code — these live in
   the **qb-rating** plan (`UnitOfMeasure.csv`: USD, GBP, EUR, AUD, CAD, CHF, JPY); and
2. its own `RateCardEntry` (plus matching `RateAdjustmentByTier` rows) in **both** rate cards.

| Denomination | Entries | Per currency? |
|--------------|---------|---------------|
| Currency (`RateUnitOfMeasure` = USD/GBP/EUR/AUD/CAD/CHF/JPY) | 15 per currency — 6 Base + 9 Tier | **Yes** — 15 × 7 = 105 |
| Token (`RateUnitOfMeasure` = `TOKEN-UOM`) | 11 | **No** — token-denominated rates are in tokens, not money |

That is the 116 total. `RateAdjustmentByTier` follows its parent entry: 15 currency-denominated
rows × 7 = 105, plus 13 token-denominated = 118.

**Generated by `scripts/expand_currency_rates_data.py`** (dry-run by default; `--apply` to write):

```bash
python scripts/expand_currency_rates_data.py --apply
```

Conversion rules it applies:

- `Rate` and **`Override`** `AdjustmentValue` are money → converted via `CurrencyType.ConversionRate`.
- **`Percentage`** `AdjustmentValue` is currency-neutral → copied unchanged.
- `LowerBound` / `UpperBound` are **consumption quantities** (minutes, TB, tokens), not money → never converted.
- Rounding: 2 decimals at or above 1, 4 decimals below 1 so small per-unit rates such as `0.004` stay
  distinct. Whole-unit currencies (JPY) round to a whole yen **only at or above ¥1** — a sub-yen rate
  keeps 2 decimals, because rounding ¥0.65/¥0.73/¥0.82/¥0.98 to a whole yen would flatten every tier
  of a tiered rate onto the same value.
- Existing non-USD rows are **preserved**, not regenerated (`--regenerate` overrides). This protects
  hand-tuned rates.

⚠️ **QB-DB's Base GBP and JPY rates are hand-set and live-verified, not generated.** GBP currently
mirrors USD exactly (0.004 / 10 / 0.10 rather than the converted 0.003 / 7.48 / 0.0748) and JPY uses
round demo values (1 / 1500 / 15 rather than 1 / 1631 / 16). Confirm whether those are the intended
demo figures before merge.

## Rate Card Entries (116 records)

> The tables below list the **USD** rows. Every currency-denominated entry also exists in
> GBP, EUR, AUD, CAD, CHF and JPY; only the `TOKEN-UOM` rows are single-currency.

### Base Rate Card Entries (flat per-unit rates)

| Product SKU      | Resource        | Rate UoM | Rate     |
|------------------|-----------------|----------|----------|
| QB-DB            | UR-CPUTIME      | USD      | $0.004   |
| QB-DB            | UR-DATASTORAGE  | USD      | $10.00   |
| QB-DB            | UR-DATAXFR      | USD      | $0.10    |
| QB-DB-TOKEN      | QB-TOKEN        | USD      | $0.50    |
| QB-DB-TOKEN      | UR-CPUTIME      | TOKEN-UOM| 5 tokens |
| QB-DB-TOKEN      | UR-DATASTORAGE  | TOKEN-UOM| 10 tokens|
| QB-TOKENS-PACK   | QB-TOKEN        | USD      | $0.33    |
| QB-DAT-THPT      | UR-DATAXFR      | USD      | $0.10    |

### Tier Rate Card Entries (rate determined by RateAdjustmentByTier)

| Product SKU      | Resource        | Rate UoM  | Selling Model |
|------------------|-----------------|-----------|---------------|
| QB-DB            | UR-CPUTIME      | USD       | Term Annual   |
| QB-DB            | UR-DATASTORAGE  | USD       | Term Annual   |
| QB-CMT-TKN-EACH | QB-TOKEN        | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-EACH | UR-CPUTIME      | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-EACH | UR-DATASTORAGE  | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-FLAT | QB-TOKEN        | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-FLAT | QB-TOKEN        | USD       | Term Annual   |
| QB-CMT-TKN-FLAT | UR-CPUTIME-TKN     | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-FLAT | UR-DATASTORAGE-TKN | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-TIER | QB-TOKEN        | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-TIER | QB-TOKEN        | USD       | Term Annual   |
| QB-CMT-TKN-TIER | UR-CPUTIME-TKN     | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-TIER | UR-DATASTORAGE-TKN | TOKEN-UOM | Term Annual   |
| QB-MTY-CMT       | UR-CPUTIME      | USD       | Term Annual   |
| QB-MTY-CMT       | UR-DATASTORAGE  | USD       | Term Annual   |
| QB-QTY-CMT       | UR-CPUTIME      | USD       | Term Annual   |
| QB-QTY-CMT       | UR-DATASTORAGE  | USD       | Term Annual   |

> **`UsageResource` is required for rating (2026-07-23 fix).** The QB-CMT-TKN-FLAT / QB-CMT-TKN-TIER `TOKEN-UOM` rows previously had a blank `UsageResource`. `RateCardEntry.UsageResourceId` is non-nillable and every rate/adjustment lookup in the rating procedures (`RLM_DefaultRatingProcedure`, `Negotiable_Rating_Procedure`) keys on `UsageResource`, so a blank-resource entry is never selected — those two products' commit discounts (flat 10% / 10-20-30% tiers) applied to nothing. Since the tiers are token-denominated, the resource was first set to the aggregate **`QB-TOKEN`** (mirroring QB-CMT-TKN-EACH's `QB-TOKEN;TOKEN-UOM` row); `RateAdjustmentByTier` rows were updated to match.
>
> **Superseded 2026-07-24 — discounts moved to the `Category=Usage` resources.** A `Category=Token` resource accepts only **one** tier adjustment, so TIER's volume bands could not live on `QB-TOKEN`; and the fresh-build **Usage Product Validator** then flagged QB-CMT-TKN-FLAT with *"No effective rate card entry available for the product usage resource"* because its `UR-CPUTIME-TKN` / `UR-DATASTORAGE-TKN` PURs had no rate card entry at all (its two RCEs both sat on `QB-TOKEN`). Both FLAT and TIER now follow one rule: **the discount sits on the `Category=Usage` resources where consumption is rated, and the `Category=Token` aggregate is held neutral at 0%.** FLAT = one unbounded 10% tier per usage resource; TIER = 10/20/30% volume bands. QB-CMT-TKN-EACH predates this and still carries non-zero adjustments on all three resources. Requires a live rating run to confirm the discount applies before merge.

## Rate Adjustments by Tier (118 records)

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

### QB-CMT-TKN-FLAT (Flat percentage on the token-backed **usage** resources)

Same placement rule as QB-CMT-TKN-TIER below — the discount sits on the `Category=Usage` resources (where consumption is rated), and the `Category=Token` aggregate stays neutral. FLAT differs from TIER only in shape: **one** unbounded tier per resource instead of volume bands.

| Resource (TOKEN-UOM) | Lower Bound | Upper Bound | Adjustment |
|----------------------|-------------|-------------|------------|
| UR-CPUTIME-TKN       | 0           | (unlimited) | 10%        |
| UR-DATASTORAGE-TKN   | 0           | (unlimited) | 10%        |
| QB-TOKEN             | 0           | (unlimited) | 0% (neutral) |
| QB-TOKEN (USD)       | 0           | (unlimited) | 0% (neutral) |

### QB-CMT-TKN-TIER (Volume tiers on the token-backed **usage** resources)

The 3 volume tiers apply per usage resource (`UR-CPUTIME-TKN`, `UR-DATASTORAGE-TKN`), **not** the token resource — the platform allows only **one** RateAdjustmentByTier per `Category=Token` resource (`QB-TOKEN`), so `QB-TOKEN` carries a single 0% tier and the tiering lives on the Usage-category resources (which is where the token-commit model applies per-resource discounts).

| Resource (TOKEN-UOM) | Lower Bound | Upper Bound | Adjustment |
|----------------------|-------------|-------------|------------|
| UR-CPUTIME-TKN       | 0           | 1000        | 10%        |
| UR-CPUTIME-TKN       | 1000        | 5000        | 20%        |
| UR-CPUTIME-TKN       | 5000        | (unlimited) | 30%        |
| UR-DATASTORAGE-TKN   | 0           | 1000        | 10%        |
| UR-DATASTORAGE-TKN   | 1000        | 5000        | 20%        |
| UR-DATASTORAGE-TKN   | 5000        | (unlimited) | 30%        |
| QB-TOKEN             | 0           | —           | 0%         |

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

**When duplicates exist:** If the org has duplicate rates records from previous runs, run `cci task run delete_qb_rates_data --org <org>` first to clear them, then run the idempotency test or data load.

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
├── Product2.csv               # 9 records (Update UsageModelType only)
├── RateCard.csv               # 3 records
├── PriceBookRateCard.csv      # 2 records
├── RateCardEntry.csv          # 116 records (Draft status — 15 per currency x 7 + 11 token-denominated)
├── RateAdjustmentByTier.csv   # 118 records
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
- **PriceBookRateCard**, **RateCardEntry**, **RateAdjustmentByTier** use `deleteOldData: true` for idempotency. Before the 5.6.4 floor, SFDMU v5 could not match these objects' auto-number Names / all-relationship externalIds against existing target records; those traversal-match bugs are **fixed on the 5.6.4+ floor**, but the shipped plan retains delete-and-reinsert (functional idempotency with stable counts) pending the gated `sfdmu-v5-optimization` migration (see the floor note at the top).
- **Product2** uses `Update` by `StockKeepingUnit`, so only existing products are modified.

**Key requirement (SFDMU v5):** Objects with multi-component composite `externalId` definitions require a `$$` column in the source CSV for SFDMU to correctly match records during Upsert. The column name uses `$` between field names (e.g., `$$Field1$Field2`), and values use `;` between component values. Without this column, pre-5.6.4 SFDMU inserted duplicates on re-runs. For objects where a `$$` column cannot be used (e.g., auto-number `Name` fields with all-relationship externalIds), the shipped plan uses `deleteOldData: true` for functional idempotency — a pre-5.6.4 workaround retained pending the gated migration; on the 5.6.4+ floor new plans use `Upsert`. See [Composite Key Optimizations](../../../../../docs/references/sfdmu-composite-key-optimizations.md) for the full v5 migration guide.

## 260 Schema Analysis (Confirmed via Org Describe)

Schema was queried against a 260 scratch org. Findings below.

### Polymorphic Fields

**None found.** All reference fields on rate objects are single-target lookups.

### Self-Referencing Fields

**None found.**

### Schema Concerns

**`RateCard.Status` — RESOLVED.**

The `RateCard` SOQL query no longer includes `Status` (the field does not exist on `RateCard` in 260). The current query is:
```sql
SELECT Description, EffectiveFrom, EffectiveTo, Name, Type FROM RateCard
```

The 260 schema describe for `RateCard` returns only:

| Field          | Type     | Updateable | In Current SOQL? |
|----------------|----------|------------|-------------------|
| `Name`         | STRING   | Yes        | Yes               |
| `Description`  | STRING   | Yes        | Yes               |
| `Type`         | PICKLIST | Yes        | Yes               |
| `EffectiveFrom`| DATETIME | Yes        | Yes               |
| `EffectiveTo`  | DATETIME | Yes        | Yes               |

`Status` has been removed from the query and `RateCard.csv` has no `Status` column.

**Note:** `RateCardEntry` *does* have a `Status` field (confirmed in schema), so the prior confusion was between the two objects.

### Field Coverage Audit

| Object               | Status | Notes                                                    |
|----------------------|--------|----------------------------------------------------------|
| Product2             | ✅     | Update only (UsageModelType) — correct                   |
| RateCard             | ✅     | `Status` removed from SOQL/CSV (not a 260 field) — correct |
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
| RateCardEntry        | This plan    | Insert (+deleteOldData) |

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
| PriceBookRateCard    | `PriceBook.Name;RateCard.Name;RateCardType` | No       | ✅ OK — 3-field composite |
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

1. **Fix `excludeIdsFromCSVFiles`**: Currently set to `"false"` — change to `"true"` for portability
2. **Document read-only field strategy**: Many RABT and RCE fields are read-only (auto-populated) but included in SOQL for extraction — document this dual-purpose pattern clearly
