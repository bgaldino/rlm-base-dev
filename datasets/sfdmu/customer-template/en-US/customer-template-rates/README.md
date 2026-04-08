# customer-template-rates (Snowflake usage rates)

**Rate card** slice for the Snowflake demo.

**Data model reference:** [`docs/references/customer-template-rate-card-entry.md`](../../../../../docs/references/customer-template-rate-card-entry.md) — how **`RateCardEntry`** stitches **rate card**, **product**, **`UsageResource`**, **`ProductSellingModel`**, **default UOM** vs **rate UOM**; **Base** ( **`Rate`**, **`RateNegotiation`**, **`RateUnitOfMeasure`** on the entry) vs **Tier** ( **`RateAdjustmentByTier`** children); **effective dates** and **`activate_rates`**.

## What this plan loads

- **CD-DEMO Base Rate Card** (**Type = Base**), linked on **Standard Price Book**
- **RateCardEntry** rows (illustrative list rates, **One-Time** selling model), each in **Draft** until **`activate_rates`**:
  - `SF-USG-STORAGE` × `SF-UR-STORAGE` — **USD per TB** (default unit Terabyte / Data Volume); **`RateNegotiation` = Negotiable**
  - `SF-USG-EGRESS` × `SF-UR-EGRESS` — **USD per GB**
  - `SF-USG-COMPUTE` × `SF-UR-COMPUTE` — **USD per CRD** (Snowflake Credits)

There are **no** **`RateAdjustmentByTier`** rows here — that is intentional (tiered pricing starts from **`qb-rates`**).

## Prerequisites

- Products and rating rows from **`customer-template-rating`**: `SF-USG-*` as Pack, `SF-UR-*` active after `activate_rating_records`, PURs active.
- Org must define **One-Time** `ProductSellingModel` (standard RLM orgs).
- Lookup CSVs (`Pricebook2`, `ProductSellingModel`, `UsageResource`, `UnitOfMeasure`, `UnitOfMeasureClass`) resolve references; they are not separate `objects` in `export.json`.

## CCI

- `insert_customer_demo_rates_data`
- `delete_customer_demo_rates_data` — removes only the CD-DEMO rate card and its entries/links.
- Then **`activate_rates`** (`activateRateCardEntries.apex`).

## Idempotency

Run **`delete_customer_demo_rates_data`** before each load (flows do this). `RateCardEntry` uses Insert without global `deleteOldData` so other rate cards stay untouched.

Adjust **Rate** or **ProductSellingModel.Name** in `RateCardEntry.csv` to match org-native names if needed.
