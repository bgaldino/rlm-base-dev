# customer-template-rating (Salesforce demo — Agentforce consumption)

**Usage rating** SFDMU plan for the **Salesforce** customer demo (prefix **`SFDC`**). Models the two Agentforce consumption meters from the SKU contract (`../sku-contract.yaml`). Durable patterns live in **[`customer-demo-usage-metered-products.md`](../../../../../docs/guides/customer-demo-usage-metered-products.md)** and **[`customer-template-usage-resource.md`](../../../../../docs/references/customer-template-usage-resource.md)**.

## What this plan loads

| Meter | UsageResource | UOM class | Default unit | Definition SKU | Billing policy |
|---|---|---|---|---|---|
| Agentforce Flex Credits | `SFDC-UR-FLEX` | `SFDCCRED` — Salesforce Flex Credits | `FLEXCRD` — Flex Credit | `SFDC-BLNG-FLEX` | `monthlytotal` |
| Agentforce Conversations | `SFDC-UR-CONV` | `SFDCCONV` — Agentforce Conversations | `AFCONV` — Agentforce Conversation | `SFDC-BLNG-CONV` | `monthlytotal` |

Sellable SKUs **`SFDC-USG-FLEX`** and **`SFDC-USG-CONV`** are set to **`UsageModelType = Anchor`** (never `Pack` — `Pack` breaks `ProductUsageResourcePolicy` and quote persist). Both sell on **Term Monthly**.

`CRD` (Snowflake Credit, class `SNFCRED`) and `EVENT` (class `DEVICE_EVENTS`) are **not** reused: a `UnitOfMeasure` belongs to exactly one class, so Salesforce metering gets dedicated classes and units.

## Object order in `export.json`

**Pass 1 — Draft load**

1. `UsageResourceBillingPolicy` — Upsert on `Code` (`monthlytotal`)
2. `UsageResource` — Upsert on `Code`
3. `UsageGrantRenewalPolicy` — Upsert on `Code`
4. `UsageGrantRolloverPolicy` — Upsert on `Code`
5. `UsageOveragePolicy` — Upsert on `Name`
6. `Product2` — Update on `StockKeepingUnit` (sets `UsageModelType = Anchor`)
7. `ProductUsageResource` — **Insert** (no `deleteOldData`)
8. `UsagePrdGrantBindingPolicy` — Upsert on `Name;Product2.StockKeepingUnit`
9. `RatingFrequencyPolicy` — Upsert on `RatingPeriod`
10. `ProductUsageResourcePolicy` — **Insert** (no `deleteOldData`)
11. `ProductUsageGrant` — **Insert** (no `deleteOldData`)

**Pass 2 — activation:** `UsageResource` Update → `Active` (CSV under `objectset_source/object-set-2/`). Then run `activate_rating_records`.

### Why Insert on PUR, PURP, and PUG

All three carry relationship-traversal external ids, which hit **SFDMU v5 Bug 3** — Upsert never matches and duplicates on every run. They use `Insert` **without** `deleteOldData: true`, so non-demo org rating data survives; the scoped `delete_customer_demo_rating_data` Apex clears the demo slice instead.

- `ProductUsageResource` — `Product.StockKeepingUnit;UsageResource.Code`
- `ProductUsageResourcePolicy` — `ProductUsageResourceId` (auto-number `Name`, no direct unique field)
- `ProductUsageGrant` — `UsageDefinitionProduct.StockKeepingUnit;UnitOfMeasureClass.Code;UnitOfMeasure.UnitCode`

## Grant policies reference existing org records

`SF-DEMO-USG-RENEW`, `SF-DEMO-USG-ROLL`, and `Default Usage Overage Policy` already exist in the target org. SFDMU v5 logs "Inserted 1" for these objects but nothing persists, so the CSV rows exist only to let `ProductUsageGrant.RenewalPolicy.Code` / `RolloverPolicy.Code` and `ProductUsageResourcePolicy.UsageOveragePolicy.Name` resolve. The `SF-` prefix is intentional — these are shared demo policies, not Salesforce-demo-specific records.

## Prerequisites

1. **`customer-template-pcm`** must load first with `UnitOfMeasureClass` `SFDCCRED` / `SFDCCONV`, `UnitOfMeasure` `FLEXCRD` / `AFCONV`, and `Product2` rows for `SFDC-USG-FLEX`, `SFDC-USG-CONV`, `SFDC-BLNG-FLEX`, `SFDC-BLNG-CONV`.
2. `UsageResource.csv` and `ProductUsageGrant.csv` carry both `.Code` / `.UnitCode` **and** `.Name` columns for the UOM lookups — SFDMU v5 needs the `Name` columns to resolve these parents.
3. `delete_customer_demo_rating_data.apex` currently scopes to `SF-USG-*` / `OC-*` SKUs and `SF-UR-*` / `OC-UR-*` codes. **It does not cover `SFDC-*`** — add the Salesforce SKUs and meter codes before relying on idempotent reloads.

## Deletes and reload order

1. `customer_demo_purge_records` — quote/order usage policies and grants on demo meters
2. `delete_customer_demo_rates_data` — must run before rating delete; `RateCardEntry` references the meters
3. `delete_customer_demo_rating_data`
4. `insert_customer_demo_rating_data`

## Post-load verification (critical)

**`ProductUsageGrant` has a confirmed SFDMU v5 silent-failure bug:** `Insert` reports "1 records processed, 0 records failed" while the record never appears in the org, even with every parent lookup resolving. **Always verify after each rating load:**

```bash
sf data query -q "SELECT Id, Quantity, Status FROM ProductUsageGrant \
  WHERE ProductUsageResource.Product.StockKeepingUnit IN ('SFDC-USG-FLEX','SFDC-USG-CONV')" \
  --target-org <alias>
```

Expect two rows: 100,000 `FLEXCRD` on `SFDC-USG-FLEX` and 0 `AFCONV` on `SFDC-USG-CONV`. If a row is missing, insert via Apex (query the PUR, UOM, UOM class, definition product, and policies by code/name) and set `Status = 'Active'`, or re-run `activate_rating_records`.

Also check `reports/MissingParentRecordsReport.csv` after every run — entries for `UnitOfMeasure`, `UnitOfMeasureClass`, or `UsageDefinitionProduct` mean PCM has not created the referenced rows yet.

## Quote testing

Quote the sellable **`SFDC-USG-FLEX`** / **`SFDC-USG-CONV`** SKUs, never the `SFDC-BLNG-*` usage-definition products.

## Reference

**`datasets/sfdmu/qb/en-US/qb-rating/`** — full QuantumBit rating shape.
