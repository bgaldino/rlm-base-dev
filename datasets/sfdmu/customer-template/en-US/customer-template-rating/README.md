# customer-template-rating (Snowflake usage)

**Usage rating design-time** slice for the Snowflake Revenue Cloud demo.

**Data model reference:** [`docs/references/customer-template-usage-resource.md`](../../../../../docs/references/customer-template-usage-resource.md) — **`UsageResource`** (meter definition) plus **`ProductUsageResource`** (junction: **sellable Pack SKU → meter**), billing policies, and how that differs from **`ProductUsageResourcePolicy`** (tier-2).

## Objects in this plan

- **`UsageResourceBillingPolicy`** — Upserts **`monthlypeak`** (Peak/Monthly) and **`monthlytotal`** (Sum/Monthly) to align with standard QB/org naming (shared; **not** deleted by `delete_customer_demo_rating_data`).
- **`UsageResource`** — **`Category = Usage`**; **`DefaultUnitOfMeasure.UnitCode`** within **`UnitOfMeasureClass.Code`**; **`UsageDefinitionProduct`** = `SF-BLNG-*`; billing policy **`monthlypeak`** (storage) or **`monthlytotal`** (egress/compute).
- **Sellable Pack products:** `SF-USG-STORAGE`, `SF-USG-EGRESS`, `SF-USG-COMPUTE` (`Product2` update).
- **Usage-definition products:** `SF-BLNG-STORAGE`, `SF-BLNG-EGRESS`, `SF-BLNG-COMPUTE` (created in PCM).
- **`ProductUsageResource`** — one row per **Pack × meter** (e.g. `SF-USG-STORAGE` → `SF-UR-STORAGE`); this is what stitches the **sellable SKU** to **`UsageResource`** for rating and rate cards. **Insert** — run delete task before reload.
- No PURP/PUG/tokens at this tier.

## Prerequisites (load order)

1. **`customer-template-pcm`** must be loaded first. It seeds **UnitOfMeasureClass** (`DATAVOL`, `SNFCRED` with **`Type = Usage`**, base/default UOM) and **UnitOfMeasure** (`GB`, `TB`, `CRD`) plus all `Product2` rows referenced here.
2. Org **ProductSellingModel** names used elsewhere (e.g. `Term Monthly` / `One-Time` on rate card) must exist — match org-native names if your tenant differs.
3. If the org has **never** had QB rating data, **`monthlypeak` / `monthlytotal`** policies are created by this plan’s Upsert; otherwise they merge with existing rows.

## CCI

- `insert_customer_demo_rating_data` — loads this plan (`sync_objectset_source_to_source: true` for pass 2 activation of `UsageResource`).
- `delete_customer_demo_rating_data` — scoped Apex cleanup before reloads (does **not** remove shared billing policies).
- `prepare_customer_demo_usage` or `prepare_customer_demo_catalog` with `customer_demo_usage: true`.

## Passes

1. **Pass 1:** `UsageResourceBillingPolicy`, `UsageResource`, `Product2` (update), `ProductUsageResource` (Insert).
2. **Pass 2:** `UsageResource` → Active (CSV under `objectset_source/object-set-2/`).

Then run **`activate_rating_records`** (same Apex as QuantumBit).

## Quote / guided-selling testing

Add **`SF-USG-STORAGE`**, **`SF-USG-EGRESS`**, and/or **`SF-USG-COMPUTE`** to the quote for user-visible usage (**Pack**). Do **not** add **`SF-BLNG-*`** for normal metering demos (those are usage-definition products for rating). See **`docs/guides/customer-demo-onboarding.md`**.

## Idempotency

Always run **`delete_customer_demo_rating_data`** immediately before **`insert_customer_demo_rating_data`** when re-importing (the catalog flow does this when `customer_demo_usage` is true).
