# customer-template-rates (usage rates — blank scaffold)

**Rate card** SFDMU plan: **headers and `export.json` only** until you add **`RateCard`**, **`PriceBookRateCard`**, **`RateCardEntry`**, and **`RateAdjustmentByTier`** rows for the next customer. Patterns: **[`customer-demo-usage-metered-products.md`](../../../../../docs/guides/customer-demo-usage-metered-products.md)**, **[`customer-template-rate-card-entry.md`](../../../../../docs/references/customer-template-rate-card-entry.md)**, **[`customer-template-tier-rate-card-lessons-learned.md`](../../../../../docs/references/customer-template-tier-rate-card-lessons-learned.md)**.

## What this plan loads (when populated)

- **Base** rate card(s): **`Rate`** + **`RateNegotiation`** + rate UOM on **`RateCardEntry`**.
- **Tier** rate card(s): **`RateCardEntry`** with **empty `Rate`**; stepped **`RateAdjustmentByTier`** in the consumption UOM of each line.
- **`PriceBookRateCard`** links to **Standard Price Book** (or other book you model in lookup CSVs).
- Lookup CSVs in this folder resolve **`Product2`**, **`UsageResource`**, **`ProductSellingModel`**, **`UnitOfMeasure`**, **`Pricebook2`** for **`RateCardEntry`** — they are not separate `objects` in **`export.json`**.

**PSM on every RCE** must match **Standard `PricebookEntry`** for that product SKU (**`customer-pricebook-entries.csv`**).

## Prerequisites

- PCM + rating loaded and activated for the usage SKUs and **`UsageResource`** codes you price.
- Demo rate card names in **`delete_customer_demo_rates_data.apex`** must match **`RateCard.Name`** (and **`Type`**) you load, or update the Apex when you rename cards.

## CCI

- `insert_customer_demo_rates_data`
- `delete_customer_demo_rates_data`
- `activate_rates`

## Idempotency

Run **`delete_customer_demo_rates_data`** before each insert pass when re-loading the same demo slice.
