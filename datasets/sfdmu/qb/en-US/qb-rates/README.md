# qb-rates Data Plan

SFDMU data plan for QuantumBit (QB) rate cards, rate card entries, and tiered rate adjustments. Defines the pricing rates used by the usage rating engine to calculate charges for QB products.

> **Reload-safe (todo 298).** Nothing is deleted: every object matches on its externalId, and a reload into a built org changes nothing. RateCardEntry and RateAdjustmentByTier moved from `Insert` + `deleteOldData` to `Upsert`, and PriceBookRateCard dropped `deleteOldData` (owner-approved, 2026-11-02). RateCardEntry loads in two passes so Status is never sent to an Active entry, and `prepare_rating` no longer runs `delete_qb_rates_data` first.

## CCI Integration

### Flow: `prepare_rating`

This plan is executed as **step 5** of the `prepare_rating` flow (when `rating=true`, `rates=true`, `qb=true`, and `refresh=false`).

| Step | Task                     | Description                                        |
|------|--------------------------|----------------------------------------------------|
| 1    | `insert_qb_rating_data`  | Runs the qb-rating SFDMU plan (prerequisite)       |
| 2    | `insert_qb_rating_entitlements_data` | Runs the qb-rating-entitlements plan (policies and grants) |
| 5    | `insert_qb_rates_data`   | **Runs this plan** (two passes)                    |
| 7    | `activate_rating_records`| Runs `activateRatingRecords.apex`                  |
| 8    | `activate_rates`         | Activates Draft RateCardEntry records (REST)       |

`delete_qb_rates_data` (`deleteQbRatesData.apex`: deactivates Active entries, then deletes RCE, RABT, PBRC and RateCard) is a manual full teardown; no flow runs it.

### Task Definition

```yaml
insert_qb_rates_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-rates"
```

## Data Plan Overview

The plan uses **two SFDMU passes** followed by **activation**:

```
Pass 1 (Upsert)                              Pass 2 (Update)                 Activation
──────────────────────────────               ─────────────────────           ─────────────────
Product2 (Update), RateCard,             ->  RateCardEntry, no Status    ->  activate_rates
PriceBookRateCard, RateCardEntry             (Product2, RateCard             (Draft RateCardEntry
(skip existing; new rows Draft),              Readonly)                       -> Active)
RateAdjustmentByTier
```

- **Pass 1** upserts every object. RateCardEntry carries `skipExistingRecords: true`: a missing entry is inserted as `Draft` (the CSV's Status), and an existing one is never touched, so Status is never sent to an Active entry.
- **Pass 2** updates RateCardEntry from `objectset_source/object-set-2/RateCardEntry.csv`, which has no Status column. Product2 and RateCard are declared `Readonly` so the entry's lookups resolve instead of being sent as null.
- **Key constraint:** RateAdjustmentByTier (RABT) must be inserted while its parent RateCardEntry is `Draft`. Pass 1 inserts both before activation.
- **Platform locks on Active rate data** (live-verified 2026-11-02): an Active entry accepts only a Status change ("Edit Restricted. Update the status field only…"), and an RABT under an Active entry can't be edited. A correction to either is rejected and fails the load; it needs a new Draft entry, or a deactivate, edit and reactivate cycle. Pass 2 therefore only corrects Draft entries, and RateCard/PriceBookRateCard corrections land at any time.

### Objects

| # | Object               | Operation | External ID                                                                          | Records |
|---|----------------------|-----------|--------------------------------------------------------------------------------------|---------|
| 1 | Product2             | Update    | `StockKeepingUnit`                                                                   | 10       |
| 2 | RateCard             | Upsert    | `Name;Type`                                                                          | 3       |
| 3 | PriceBookRateCard    | Upsert    | `PriceBook.Name;RateCard.Name;RateCardType`                                          | 2       |
| 4 | RateCardEntry        | Upsert (skip existing); pass 2 Update | `Product.StockKeepingUnit;RateCard.Name;UsageResource.Code;RateUnitOfMeasure.UnitCode` | 126    |
| 5 | RateAdjustmentByTier | Upsert    | `Product.StockKeepingUnit;RateCardEntry.RateCard.Name;RateUnitOfMeasure.UnitCode;UsageResource.Code;LowerBound;UpperBound` | 128 |

**Note:** Product2 is an `Update` operation — it only sets `UsageModelType` on existing products (created by qb-pcm). RateCardEntry records are inserted in `Draft` status. RateAdjustmentByTier keys on `RateCardEntry.RateCard.Name` (traversing the parent RateCardEntry to its RateCard's portable `Name`) instead of `RateCardEntry.Name` (auto-numbered), with a separate `RateCardEntry.$$...` column in the CSV for parent RCE lookup resolution. Its `$$` key omits empty parts, as SFDMU does on the target: a row with a blank `UpperBound` keys as `...;0`, not `...;0;`, or it would never match and Upsert would insert a duplicate.

### Lookup Reference CSVs

The following CSVs are included for SFDMU lookup resolution only (they are not loaded as separate objects):

| File                   | Purpose                                                |
|------------------------|--------------------------------------------------------|
| Pricebook2.csv         | Standard Price Book reference for PriceBookRateCard    |
| ProductSellingModel.csv| Selling model names referenced by RateCardEntry        |
| UnitOfMeasure.csv      | UoM references for rate units                          |
| UnitOfMeasureClass.csv | UoM class references for default/rate UoM classes      |
| UsageResource.csv      | Usage resource references for RateCardEntry            |

## Reloading rates outside a full build — refresh the decision tables

Rate resolution at runtime goes through decision tables
(`Rate_Card_Entry_Resolution*`, `Asset_Rate_Decision_Table*`, …), which cache the
rate data. **Loading rates does not refresh them.** A full `prepare_rlm_org` is
safe because `refresh_all_decision_tables` runs near the end, after
`prepare_rating` — but `prepare_rating` on its own stops at `activate_rates`, so
an ad-hoc reload leaves the tables holding the *previous* rates and rating keeps
using the old values with no error anywhere.

After reloading this plan by itself, run:

```bash
cci task run refresh_dt_rating --org <cci_alias>
cci task run refresh_dt_rating_discovery --org <cci_alias>
```

These tasks (like `activate_rates`) accept `--org`; without it they run against the
CCI *default* org.

Two more ordering rules for an ad-hoc reload:

1. **A changed rate on an Active entry doesn't load.** The platform allows only a
   Status change on an Active entry, so the row is rejected and the load fails.
   Add the new rate as a new Draft entry, or deactivate, edit and reactivate.
2. **Activate after loading** (`cci task run activate_rates`); new entries load as
   `Draft` and a Draft entry is invisible to rating.

## Apex Activation Script

**File:** `scripts/apex/activateRateCardEntries.apex`

Legacy, kept as a manual fallback. The flow activates with `activate_rates`, a REST task
(`tasks/rlm_activate_rates.py`) that replaced this script after Apex DML on
`RateCardEntry.Status` failed on Release 262 (see the task's docstring).

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
| Attribute Rate  | Attribute | 2023-01-01     | Attribute-based rate card             |
| Base Rate Card  | Base      | 2023-01-01     | Flat per-unit base rates              |
| Tier Rate Card  | Tier      | 2023-01-01     | Volume tier-based rate adjustments    |

### PriceBook Associations

| Price Book           | Rate Card       | Type |
|----------------------|-----------------|------|
| Standard Price Book  | Base Rate Card  | Base |
| Standard Price Book  | Tier Rate Card  | Tier |

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
| Currency (`RateUnitOfMeasure` = USD/GBP/EUR/AUD/CAD/CHF/JPY) | 16 per currency — 6 Base + 10 Tier | **Yes** — 16 × 7 = 112 |
| Token (`RateUnitOfMeasure` = `TOKEN-UOM`) | 14 | **No** — token-denominated rates are in tokens, not money |

That is the 126 total. `RateAdjustmentByTier` follows its parent entry: 112
currency-denominated rows plus 16 token-denominated = 128.

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
- Every non-USD row is **regenerated from the base**. That is the default because this dataset is
  fully derived: `check_rates_derived_from_base` requires each non-base rate to equal the derived
  value exactly with an **empty** deviation allowlist, so preserving old rows would silently ship
  stale rates the moment `CurrencyType.ConversionRate` changes — the canonical `--apply` above would
  write nothing and the suite would then fail. Pass **`--preserve`** to fill in only the missing
  (product, rate card, usage resource, currency) combinations; anything kept that way must be added
  to `ALLOWED_RATE_DEVIATIONS` as a conscious, documented choice.

✅ **Every non-base rate is generator-derived — no hand-set values remain.** QB-DB's GBP rates are
the converted `0.003 / 7.48 / 0.0748` and JPY the converted `0.65 / 1631 / 16`; the six hand-seeded
placeholders that previously mirrored USD were corrected. `tests/test_qb_multicurrency_data.py::`
`check_rates_derived_from_base` now enforces exact derivation with an **empty**
`ALLOWED_RATE_DEVIATIONS`, so reintroducing a hand-tuned rate fails the suite until it is added to
that allowlist as a conscious, documented choice.

## Rate Card Entries (126 records)

> The tables below list the **USD** rows. Every currency-denominated entry also exists in
> GBP, EUR, AUD, CAD, CHF and JPY; only the `TOKEN-UOM` rows are single-currency.

### Base Rate Card Entries (flat per-unit rates)

| Product SKU      | Resource        | Rate UoM | Rate     |
|------------------|-----------------|----------|----------|
| QB-DB            | UR-CPUTIME      | USD      | $0.004   |
| QB-DB            | UR-DATASTORAGE  | USD      | $10.00   |
| QB-DB            | UR-DATAXFR      | USD      | $0.10    |
| QB-DB-TOKEN      | QB-TOKEN        | USD      | $0.50    |
| QB-DB-TOKEN      | UR-CPUTIME-TKN     | TOKEN-UOM| 5 tokens |
| QB-DB-TOKEN      | UR-DATASTORAGE-TKN | TOKEN-UOM| 10 tokens|
| QB-TOKENS-PACK   | QB-TOKEN        | USD      | $0.33    |
| QB-DAT-THPT      | UR-DATAXFR      | USD      | $0.10    |

### Tier Rate Card Entries (rate determined by RateAdjustmentByTier)

| Product SKU      | Resource        | Rate UoM  | Selling Model |
|------------------|-----------------|-----------|---------------|
| QB-DB            | UR-CPUTIME      | USD       | Term Annual   |
| QB-DB            | UR-DATASTORAGE  | USD       | Term Annual   |
| QB-CMT-TKN-EACH | QB-TOKEN        | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-EACH | QB-TOKEN        | USD       | Term Annual   |
| QB-CMT-TKN-EACH | UR-CPUTIME-TKN     | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-EACH | UR-DATASTORAGE-TKN | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-FLAT | QB-TOKEN        | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-FLAT | QB-TOKEN        | USD       | Term Annual   |
| QB-CMT-TKN-FLAT | UR-CPUTIME-TKN     | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-FLAT | UR-DATASTORAGE-TKN | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-TIER | QB-TOKEN        | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-TIER | QB-TOKEN        | USD       | Term Annual   |
| QB-CMT-TKN-TIER | UR-CPUTIME-TKN     | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-TIER | UR-DATASTORAGE-TKN | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-BND  | QB-TOKEN        | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-BND  | QB-TOKEN        | USD       | Term Annual   |
| QB-CMT-TKN-BND  | UR-CPUTIME-TKN     | TOKEN-UOM | Term Annual   |
| QB-CMT-TKN-BND  | UR-DATASTORAGE-TKN | TOKEN-UOM | Term Annual   |
| QB-MTY-CMT       | UR-CPUTIME      | USD       | Term Annual   |
| QB-MTY-CMT       | UR-DATASTORAGE  | USD       | Term Annual   |
| QB-QTY-CMT       | UR-CPUTIME      | USD       | Term Annual   |
| QB-QTY-CMT       | UR-DATASTORAGE  | USD       | Term Annual   |

> **`UsageResource` is required for rating (2026-07-23 fix).** The QB-CMT-TKN-FLAT / QB-CMT-TKN-TIER `TOKEN-UOM` rows previously had a blank `UsageResource`. `RateCardEntry.UsageResourceId` is non-nillable and every rate/adjustment lookup in the rating procedures (`RLM_DefaultRatingProcedure`, `Negotiable_Rating_Procedure`) keys on `UsageResource`, so a blank-resource entry is never selected — those two products' commit discounts (flat 10% / 10-20-30% tiers) applied to nothing. Since the tiers are token-denominated, the resource was first set to the aggregate **`QB-TOKEN`** (mirroring QB-CMT-TKN-EACH's `QB-TOKEN;TOKEN-UOM` row); `RateAdjustmentByTier` rows were updated to match.
>
> **Superseded 2026-07-24 — discounts moved to the `Category=Usage` resources.** A `Category=Token` resource accepts only **one** tier adjustment, so TIER's volume bands could not live on `QB-TOKEN`; and the fresh-build **Usage Product Validator** then flagged QB-CMT-TKN-FLAT with *"No effective rate card entry available for the product usage resource"* because its `UR-CPUTIME-TKN` / `UR-DATASTORAGE-TKN` PURs had no rate card entry at all (its two RCEs both sat on `QB-TOKEN`). Both FLAT and TIER now follow one rule: **the discount sits on the `Category=Usage` resources where consumption is rated, and the `Category=Token` aggregate is held neutral at 0%.** FLAT = one unbounded 10% tier per usage resource; TIER = 10/20/30% volume bands. QB-CMT-TKN-EACH predates this and still carries non-zero adjustments on all three resources. Requires a live rating run to confirm the discount applies before merge.

## Rate Adjustments by Tier (128 records)

### QB-DB — Compute Time (Override tiers, USD/minute)

| Lower Bound | Upper Bound | Type     | Value    |
|-------------|-------------|----------|----------|
| 1           | 1000        | Override | $0.004   |
| 1000        | 3000        | Override | $0.0045  |
| 3000        | 6000        | Override | $0.005   |
| 6000        | 999999999   | Override | $0.006   |

### QB-DB — Data Storage (mixed tiers, USD/TB)

| Lower Bound | Upper Bound | Type       | Value   |
|-------------|-------------|------------|---------|
| 1           | 10          | Percentage | 0%      |
| 10          | 25          | Override   | $12.50  |
| 25          | 100         | Override   | $15.00  |
| 100         | 999999999   | Override   | $18.00  |

### QB-CMT-TKN-EACH (Percentage tiers per resource)

| Resource           | Adjustment |
|--------------------|------------|
| UR-CPUTIME-TKN     | 5%         |
| UR-DATASTORAGE-TKN | 4%         |
| QB-TOKEN           | 6%         |
| QB-TOKEN (USD)     | 0%         |

### QB-CMT-TKN-FLAT (Flat percentage on the token-backed **usage** resources)

Same placement rule as QB-CMT-TKN-TIER below — the discount sits on the `Category=Usage` resources (where consumption is rated), and the `Category=Token` aggregate stays neutral. FLAT differs from TIER only in shape: **one** unbounded tier per resource instead of volume bands.

| Resource (TOKEN-UOM unless noted) | Lower Bound | Upper Bound | Adjustment |
|----------------------|-------------|-------------|------------|
| UR-CPUTIME-TKN       | 0           | (unlimited) | 10%        |
| UR-DATASTORAGE-TKN   | 0           | (unlimited) | 10%        |
| QB-TOKEN             | 0           | (unlimited) | 0% (neutral) |
| QB-TOKEN (USD)       | 0           | (unlimited) | 0% (neutral) |

### QB-CMT-TKN-TIER (Volume tiers on the token-backed **usage** resources)

The 3 volume tiers apply per usage resource (`UR-CPUTIME-TKN`, `UR-DATASTORAGE-TKN`), **not** the token resource — the platform allows only **one** RateAdjustmentByTier per `Category=Token` resource (`QB-TOKEN`), so `QB-TOKEN` carries a single 0% tier and the tiering lives on the Usage-category resources (which is where the token-commit model applies per-resource discounts).

| Resource (TOKEN-UOM unless noted) | Lower Bound | Upper Bound | Adjustment |
|----------------------|-------------|-------------|------------|
| UR-CPUTIME-TKN       | 0           | 10000       | 10%        |
| UR-CPUTIME-TKN       | 10000       | 25000       | 20%        |
| UR-CPUTIME-TKN       | 25000       | (unlimited) | 30%        |
| UR-DATASTORAGE-TKN   | 0           | 10000       | 10%        |
| UR-DATASTORAGE-TKN   | 10000       | 25000       | 20%        |
| UR-DATASTORAGE-TKN   | 25000       | (unlimited) | 30%        |
| QB-TOKEN             | 0           | (unlimited) | 0% (neutral) |
| QB-TOKEN (USD)       | 0           | (unlimited) | 0% (neutral) |

### QB-CMT-TKN-BND (same tiers as QB-CMT-TKN-FLAT)

| Resource (TOKEN-UOM unless noted) | Lower Bound | Upper Bound | Adjustment |
|----------------------|-------------|-------------|------------|
| UR-CPUTIME-TKN       | 0           | (unlimited) | 10%        |
| UR-DATASTORAGE-TKN   | 0           | (unlimited) | 10%        |
| QB-TOKEN             | 0           | (unlimited) | 0% (neutral) |
| QB-TOKEN (USD)       | 0           | (unlimited) | 0% (neutral) |

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

**When duplicates exist** (left by a load from before todo 298): run `cci task run delete_qb_rates_data --org <org>` to clear every rates record, then reload. It fails while `AssetRateCardEntry` records reference the entries.

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
├── export.json                # SFDMU data plan (two passes)
├── README.md                  # This file
│
│  Source CSVs (data to load)
├── Product2.csv               # 10 records (Update UsageModelType only)
├── RateCard.csv               # 3 records
├── PriceBookRateCard.csv      # 2 records
├── RateCardEntry.csv          # 126 records (Draft; 16 per currency x 7 + 14 token)
├── RateAdjustmentByTier.csv   # 128 records
├── objectset_source/object-set-2/
│   └── RateCardEntry.csv      # 126 records (pass 2: no Status)
│
│  Lookup Reference CSVs (for SFDMU resolution)
├── Pricebook2.csv             # Standard Price Book
├── ProductSellingModel.csv    # One-Time, Term Annual
├── UnitOfMeasure.csv          # Token, USD, Minutes, TB
├── UnitOfMeasureClass.csv     # Token, Currency, Time, Data Volume
├── UsageResource.csv          # 7 usage resources (lookup)
│
│  SFDMU Runtime (gitignored)
├── source/                    # SFDMU-generated source snapshots
└── target/                    # SFDMU-generated target snapshots
```

## Dependencies

This plan depends on the following having been loaded first:

- **qb-pcm** — Product2 records, UnitOfMeasure, UnitOfMeasureClass, ProductSellingModel
- **qb-pricing** — Pricebook2 (the Standard Price Book)
- **qb-rating** — UsageResource (with categories and token references), ProductUsageResource (PUR associations required for rate card entry context)

## Idempotency

> **SFDMU v5 Required.** All externalId definitions and CSV formats are optimized for SFDMU v5.

- **RateCard** uses `Upsert` with `Name;Type` composite key — matches correctly on re-run.
- **PriceBookRateCard**, **RateCardEntry**, **RateAdjustmentByTier** use `Upsert` on their traversal composite keys, which match on the 5.6.4+ floor. Live-verified 2026-11-02 (SFDMU 5.8.0, 264): two reloads and a full `prepare_rating` on a built org gave 0 diff with the same record Ids; a fresh load after `delete_qb_rates_data`, then `activate_rates`, then a reload, also gave 0 diff; `test_qb_rates_idempotency` passes.
- **Product2** uses `Update` by `StockKeepingUnit`, so only existing products are modified.

**Key requirement (SFDMU v5):** Objects with multi-component composite `externalId` definitions require a `$$` column in the source CSV for SFDMU to correctly match records during Upsert. The column name uses `$` between field names (e.g., `$$Field1$Field2`), and values use `;` between component values. Without this column, pre-5.6.4 SFDMU inserted duplicates on re-runs. A `$$` value omits empty parts, the way SFDMU builds the target key. See [Composite Key Optimizations](../../../../../docs/references/sfdmu-composite-key-optimizations.md) for the full v5 migration guide.

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
