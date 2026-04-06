# customer-template-rating (Tier-1 usage)

Minimal **usage rating design-time** slice for customer demos: one sellable SKU (**CD-USG-DATA**, `UsageModelType=Pack`), one usage definition product (**CD-DATA-THPT-BLNG**), one **UsageResource** (**CD-UR-DATAXFR**, GB / DATAVOL), one **ProductUsageResource**. No PURP/PUG/tokens.

## Prerequisites

- **PCM** rows for `CD-USG-DATA` and `CD-DATA-THPT-BLNG` (see `customer-template-pcm/Product2.csv`).
- **UnitOfMeasure** `GB` and **UnitOfMeasureClass** `DATAVOL` must already exist in the org (e.g. from `prepare_product_data` / `qb-pcm` or `qb-rating`). This plan does **not** upsert UoM/UoMClass so it does not overwrite shared catalog rows.

## CCI

- `insert_customer_demo_rating_data` — loads this plan (`sync_objectset_source_to_source: true` for pass 2).
- `delete_customer_demo_rating_data` — scoped Apex cleanup before reloads.
- `prepare_customer_demo_usage` or `prepare_customer_demo_catalog` with `customer_demo_usage: true`.

## Passes

1. **Pass 1:** `UsageResourceBillingPolicy`, `UsageResource`, `Product2` (update), `ProductUsageResource` (Insert — run delete task first to avoid duplicates).
2. **Pass 2:** `UsageResource` → Active (CSV under `objectset_source/object-set-2/`).

Then run **`activate_rating_records`** (same Apex as QuantumBit).

## Idempotency

Always run **`delete_customer_demo_rating_data`** immediately before **`insert_customer_demo_rating_data`** when re-importing (flow does this).
