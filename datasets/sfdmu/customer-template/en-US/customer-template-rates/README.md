# customer-template-rates (Snowflake usage rates)

**Rate card** slice for the **example** Snowflake-themed demo (`SF-*` SKUs). Replace CSVs and card names when the demo customer changes. **Transferable usage-metered patterns:** [`docs/guides/customer-demo-usage-metered-products.md`](../../../../../docs/guides/customer-demo-usage-metered-products.md).

**Data model reference:** [`docs/references/customer-template-rate-card-entry.md`](../../../../../docs/references/customer-template-rate-card-entry.md) — how **`RateCardEntry`** stitches **rate card**, **product**, **`UsageResource`**, **`ProductSellingModel`**, **default UOM** vs **rate UOM**; **Base** ( **`Rate`**, **`RateNegotiation`**, **`RateUnitOfMeasure`** on the entry) vs **Tier** ( **`RateAdjustmentByTier`** children); **effective dates** and **`activate_rates`**.

## What this plan loads

- **CD-DEMO Base Rate Card** (**Type = Base**), linked on **Standard Price Book**
- **CD-DEMO Tier Rate Card** (**Type = Tier**), also on **Standard Price Book** — stepped **`RateAdjustmentByTier`** rows per usage line (**`Override`** by consumption band)
- **RateCardEntry** rows (Base carries **`Rate`**; Tier rows leave **`Rate`** empty and use tiers), each in **Draft** until **`activate_rates`**. **`ProductSellingModel`** on each row matches **Standard PricebookEntry** for that SKU (**Term Monthly** / **TermDefined** for **`SF-USG-*`**, per **`customer-pricebook-entries.csv`** — not One-Time):
  - `SF-USG-STORAGE` × `SF-UR-STORAGE` — **USD per TB** (default unit Terabyte / Data Volume); **`RateNegotiation` = Negotiable**
  - `SF-USG-EGRESS` × `SF-UR-EGRESS` — **USD per GB**
  - `SF-USG-COMPUTE` × `SF-UR-COMPUTE` — **USD per CRD** (Snowflake Credits)

**Tier ladder (illustrative):** storage TB bands **1–100 / 100–500 / 500+**; egress GB **0–10k / 10k–100k / 100k+**; compute credits **1–10k / 10k–100k / 100k+**. Adjust **`RateAdjustmentByTier.csv`** to match your demo narrative; keep **`LowerBound` / `UpperBound`** disjoint and consistent with default consumption UOM on each **`RateCardEntry`**.

## Prerequisites

- Products and rating rows from **`customer-template-rating`**: `SF-USG-*` with **`UsageModelType` = `Anchor`** (not **`Pack`** — required for **`ProductUsageResourcePolicy`**); `SF-UR-*` active after `activate_rating_records`, PURs active.
- Org must define the **`ProductSellingModel`** rows referenced in **`RateCardEntry.csv`** (template lookup includes **Term Monthly** / **TermDefined** and **One-Time** for other demos).
- Lookup CSVs (`Pricebook2`, `ProductSellingModel`, `UsageResource`, `UnitOfMeasure`, `UnitOfMeasureClass`) resolve references; they are not separate `objects` in `export.json`.

**PSM must match PBE:** When you change **`PSMName`** on a SKU in **`customer-pricebook-entries.csv`**, update **`ProductSellingModel.Name`** on every **`RateCardEntry`** line for that **`Product.StockKeepingUnit`** so it stays aligned with the product’s Standard **PricebookEntry**.

## CCI

- `insert_customer_demo_rates_data`
- `delete_customer_demo_rates_data` — removes **CD-DEMO Base** and **CD-DEMO Tier** rate cards and their entries, tier adjustments, and **PriceBookRateCard** links.
- Then **`activate_rates`** (`activateRateCardEntries.apex`).

## Idempotency

Run **`delete_customer_demo_rates_data`** before each load (flows do this). `RateCardEntry` and **`RateAdjustmentByTier`** use **Insert** without **`deleteOldData`** so other rate cards stay untouched; the Apex delete clears the demo slice for a clean re-run.

Adjust **Rate**, tier **`AdjustmentValue`**, or **ProductSellingModel.Name** in the CSVs to match org-native names if needed.

**Lessons learned (tier + SFDMU + delete order):** [`docs/references/customer-template-tier-rate-card-lessons-learned.md`](../../../../../docs/references/customer-template-tier-rate-card-lessons-learned.md).
