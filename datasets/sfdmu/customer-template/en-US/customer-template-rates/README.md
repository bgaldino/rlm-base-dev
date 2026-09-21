# customer-template-rates (Salesforce demo — Agentforce rate cards)

**Rate card** SFDMU plan for the **Salesforce** customer demo (prefix **`SFDC`**). Patterns: **[`customer-demo-usage-metered-products.md`](../../../../../docs/guides/customer-demo-usage-metered-products.md)**, **[`customer-template-rate-card-entry.md`](../../../../../docs/references/customer-template-rate-card-entry.md)**, **[`customer-template-tier-rate-card-lessons-learned.md`](../../../../../docs/references/customer-template-tier-rate-card-lessons-learned.md)**.

## What this plan loads

**`CD-DEMO Base Rate Card`** (`Type = Base`) — flat rates, `Rate` on the entry:

| SKU | UsageResource | Consumption UOM | Rate | Rate UOM |
|---|---|---|---|---|
| `SFDC-USG-FLEX` | `SFDC-UR-FLEX` | Flex Credit (`FLEXCRD`) | 0.005 | USD |
| `SFDC-USG-CONV` | `SFDC-UR-CONV` | Agentforce Conversation (`AFCONV`) | 2.00 | USD |

$0.005 per Flex Credit is Salesforce's published $500 per 100,000 credits.

**`CD-DEMO Tier Rate Card`** (`Type = Tier`) — `SFDC-USG-FLEX` only, `Rate` **empty** on the entry; stepped bands on `RateAdjustmentByTier` in Flex Credits:

| Lower | Upper | Adjustment | Value |
|---|---|---|---|
| 0 | 1,000,000 | Override | 0.005 |
| 1,000,000 | 5,000,000 | Override | 0.004 |
| 5,000,000 | 999,999,999 | Override | 0.003 |

The top band uses `999999999` rather than a blank `UpperBound` — an open-ended band keeps the composite key ambiguous, and this template has only ever loaded bounded `Override` rows.

Both cards link to **Standard Price Book** via `PriceBookRateCard` and run from **2025-01-01**, comfortably before any demo sell date.

`Pricebook2.csv`, `Product2.csv`, `ProductSellingModel.csv`, `UnitOfMeasure.csv`, `UnitOfMeasureClass.csv`, and `UsageResource.csv` are lookup CSVs that resolve `RateCardEntry` parents; only `Product2` is an object in `export.json`.

## Object order in `export.json`

1. `Product2` — Update on `StockKeepingUnit` (keeps `UsageModelType = Anchor`)
2. `RateCard` — Upsert on `Name;Type`
3. `PriceBookRateCard` — Upsert on `PriceBook.Name;RateCard.Name;RateCardType`
4. `RateCardEntry` — **Insert** (no `deleteOldData`)
5. `RateAdjustmentByTier` — **Insert** (no `deleteOldData`)

`RateCardEntry` stays ahead of `RateAdjustmentByTier` in a single pass so RABT inserts while the parent entry is still **Draft**. `activate_rates` moves entries to Active afterwards — never before the load finishes.

### Why Insert on RateCardEntry and RateAdjustmentByTier

Both external ids are composed entirely of relationship traversals, so Upsert hits **SFDMU v5 Bug 3** (traversal external ids never match and re-insert every run) and, for the 2-hop `RateCardEntry.RateCard.Name` on RABT, **Bug 2** (the Upsert TARGET SELECT is built with a stripped prefix and throws). `Insert` skips the TARGET SELECT phase. `deleteOldData: true` is deliberately **not** used — it would wipe org-wide rate card entries; the scoped `delete_customer_demo_rates_data` Apex removes the CD-DEMO slice instead.

`validate_sfdmu_v5_datasets.py` reports a **Medium** note on the nested `RateCardEntry.RateCard.Name` path in the RABT external id. That is expected — `qb-rates` carries the same shape and loads correctly.

## Product selling model

Every `RateCardEntry` uses **Term Monthly** (`TermDefined`), matching `PSMName` for `SFDC-USG-FLEX` and `SFDC-USG-CONV` in `scripts/customer-demo/customer-pricebook-entries.csv`. A mismatch against the Standard `PricebookEntry` breaks quote and rating consistency.

## Prerequisites

- `customer-template-pcm` and `customer-template-rating` loaded and activated for `SFDC-USG-*` and `SFDC-UR-*`.
- `delete_customer_demo_rates_data.apex` keys on the card names `CD-DEMO Base Rate Card` (Base) and `CD-DEMO Tier Rate Card` (Tier) — unchanged here, so it covers all rows in this plan including RABT (cascades on `RateCardEntry` delete).

## CCI

- `insert_customer_demo_rates_data`
- `delete_customer_demo_rates_data`
- `activate_rates`

## Idempotency

Run `delete_customer_demo_rates_data` before each insert pass when reloading the same demo slice.
