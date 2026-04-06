# customer-template-rates (Tier-1 rates)

Minimal **rate card** slice for customer demos: **CD-DEMO Base Rate Card** (Base), link on **Standard Price Book**, one **RateCardEntry** for **CD-USG-DATA** × **CD-UR-DATAXFR** at **$0.25/USD** per GB default, **ProductSellingModel** = **One-Time**.

## Prerequisites

- Products and usage rating rows from **`customer-template-rating`** (or equivalent): `CD-USG-DATA`, `CD-UR-DATAXFR` active, PUR active after `activate_rating_records`.
- Org must define **One-Time** selling model (standard RLM orgs).
- Lookup CSVs (`Pricebook2`, `ProductSellingModel`, `UsageResource`, `UnitOfMeasure`, `UnitOfMeasureClass`) resolve references; they are not separate `objects` in `export.json`.

## CCI

- `insert_customer_demo_rates_data`
- `delete_customer_demo_rates_data` — removes only the CD-DEMO rate card and its entries/links.
- Then **`activate_rates`** (`activateRateCardEntries.apex`).

## Idempotency

This plan does **not** use global `deleteOldData` on `RateCardEntry` (unlike `qb-rates`) so other rate cards in the org are untouched. Run **`delete_customer_demo_rates_data`** before each load (flows do this).

Adjust **Rate** or **ProductSellingModel.Name** in `RateCardEntry.csv` to match org-native PSM names if needed.
