# customer-template-rating (Snowflake usage)

**Usage rating design-time** slice for the **example** Snowflake-themed demo (`SF-*` SKUs). This data can be replaced when onboarding another customer; keep **[`customer-demo-usage-metered-products.md`](../../../../../docs/guides/customer-demo-usage-metered-products.md)** as the durable pattern guide.

**Data model reference:** [`docs/references/customer-template-usage-resource.md`](../../../../../docs/references/customer-template-usage-resource.md) — **`UsageResource`**, **`ProductUsageResource`**, **`ProductUsageResourcePolicy`**, **`ProductUsageGrant`**, and how they mirror **QuantumBit `QB-DB`** in **`qb-rating`**.

## Objects in this plan

- **`UsageResourceBillingPolicy`** — Upserts **`monthlypeak`** and **`monthlytotal`** (shared; **not** deleted by `delete_customer_demo_rating_data`).
- **`UsageResource`** — **`Category = Usage`**; UOM class + default UOM (**include `.Name`** columns for SFDMU v5); **`UsageDefinitionProduct`** = `SF-BLNG-*`; billing policy **`monthlypeak`** (storage) or **`monthlytotal`** (egress/compute).
- **`UsageGrantRenewalPolicy`** / **`UsageGrantRolloverPolicy`** — Demo codes **`SF-DEMO-USG-RENEW`** / **`SF-DEMO-USG-ROLL`** (Upsert).
- **`UsageOveragePolicy`** — **Default Usage Overage Policy** (Upsert; merges with org if present).
- **`Product2`** — Update **`UsageModelType`** on sellable **`SF-USG-*`** rows to **`Anchor`** (same as QuantumBit **`QB-DB`**). **`Pack`** causes the platform to reject **`ProductUsageResourcePolicy`** (“pack usage model type” error) and can break quote persist (**`PlaceSalesTransactionPersistException`** / related errors).
- **`ProductUsageResource`** — Pack → meter (**Insert**); junction for each **`SF-USG-*`** × **`SF-UR-*`**.
- **`UsagePrdGrantBindingPolicy`** — **Self** grant binding per **`SF-USG-*`** (Upsert).
- **`RatingFrequencyPolicy`** — Single **Monthly** row (Upsert by **`RatingPeriod`**).
- **`ProductUsageResourcePolicy`** — Per-PUR: **Monthly** rating, **`UsageAggregationPolicy.Code`** = **`monthlypeak`** or **`monthlytotal`** (same Code as **`UsageResourceBillingPolicy`**), default overage (**Insert** after scoped delete).
- **`ProductUsageGrant`** — Per-PUR **Grant** rows (included quantity, renewal/rollover, **`SF-BLNG-*`** definition product) (**Insert**).

No tokens, no **`UsageResourcePolicy`** at UR level, no **`ProductUsageResourcePolicy`**-only QB token variants.

## Prerequisites (load order)

1. **`customer-template-pcm`** must be loaded first (**`UnitOfMeasureClass`**, **`UnitOfMeasure`**, **`Product2`** including **`SF-USG-*`** and **`SF-BLNG-*`**).
2. Org **`ProductSellingModel`** names used on quotes/rates must exist where referenced elsewhere.
3. **`monthlypeak` / `monthlytotal`** policies: created or merged by this plan’s Upsert.

## Deletes and reload order

- **`prepare_customer_demo_catalog` step 1** runs **`customer_demo_purge_records`**, which deletes **`QuotLineItmUseRsrcGrant`** and **`OrderItemUsageRsrcGrant`** rows tied to **`SF-UR-*`** so **`delete_customer_demo_rating_data`** is not blocked by quotes/orders.
- **`delete_customer_demo_rates_data`** **before** **`delete_customer_demo_rating_data`** when **CD-DEMO `RateCardEntry`** rows reference **`SF-UR-*`** (otherwise **`UsageResource`** delete fails).
- Always run **`delete_customer_demo_rating_data`** immediately before **`insert_customer_demo_rating_data`** when re-importing (catalog flow does this after rates delete when `customer_demo_usage` is true).

## CCI

- `insert_customer_demo_rating_data` — loads this plan (`sync_objectset_source_to_source: true` for pass 2 **`UsageResource` → Active`).
- `delete_customer_demo_rating_data` — Apex cleanup (**PUG → PURP → PUR → UR** for demo SKUs/codes).
- `prepare_customer_demo_usage` or `prepare_customer_demo_catalog` with `customer_demo_usage: true`.

## Passes

1. **Pass 1:** Policies (**URBP**, renewal/rollover/overage), **`UsageResource`**, **`Product2`**, **`PUR`**, **`UsagePrdGrantBindingPolicy`**, **`RatingFrequencyPolicy`**, **`PURP`**, **`PUG`**.
2. **Pass 2:** **`UsageResource` → Active** (CSV under `objectset_source/object-set-2/`).

Then run **`activate_rating_records`** (same Apex as QuantumBit — activates **PUR**, then **PUG**, etc.).

## Quote / guided-selling testing

Add **`SF-USG-*`** Pack SKUs to the quote for user-visible usage. Do **not** add **`SF-BLNG-*`** for normal metering demos. See **`docs/guides/customer-demo-onboarding.md`**.

## Reference shape

**`datasets/sfdmu/qb/en-US/qb-rating/`** — full QuantumBit rating (**`ProductUsageResourcePolicy.csv`**, **`ProductUsageGrant.csv`**) for **`QB-DB`**, tokens, and commitment variants.
