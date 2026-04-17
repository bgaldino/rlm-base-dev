# customer-template-rating (usage — blank scaffold)

**Usage rating** SFDMU plan: **headers and `export.json` only** until you add rows for the next customer. Durable patterns live in **[`customer-demo-usage-metered-products.md`](../../../../../docs/guides/customer-demo-usage-metered-products.md)** and **[`customer-template-usage-resource.md`](../../../../../docs/references/customer-template-usage-resource.md)** ( **`UsageResource`**, **`ProductUsageResource`**, **`ProductUsageResourcePolicy`**, **`ProductUsageGrant`**, **`qb-rating`** reference shape).

## Objects in this plan (populate per onboarding)

- **`UsageResourceBillingPolicy`** — typically Upsert shared codes such as **`monthlypeak`** / **`monthlytotal`** (not removed by `delete_customer_demo_rating_data`).
- **`UsageResource`** — **`Category = Usage`**; UOM class + default UOM (**include `.Name`** columns for SFDMU v5); **`UsageDefinitionProduct`** points at usage-definition **`Product2`** rows from PCM; billing policy matches PURP aggregation.
- **`UsageGrantRenewalPolicy`** / **`UsageGrantRolloverPolicy`** — **must reference existing org policies** (e.g. `SF-DEMO-USG-RENEW`, `SF-DEMO-USG-ROLL`). SFDMU silently fails to create new policy records (logs success but records never persist). Query the org for available policies before populating CSVs.
- **`UsageOveragePolicy`** — **must reference existing org policy** by exact `Name` (e.g. `Default Usage Overage Policy`, **not** `Default Overage`). Same SFDMU silent-failure issue as renewal/rollover policies.
- **`Product2`** — Update **`UsageModelType`** on **sellable usage** SKUs to **`Anchor`** (QuantumBit **`QB-DB`** pattern). **`Pack`** breaks **`ProductUsageResourcePolicy`** and quote persist for this model.
- **`ProductUsageResource`** — junction sellable product × **`UsageResource`** (**Insert**; scoped delete before reload).
- **`UsagePrdGrantBindingPolicy`** — **Self** (or other) binding per sellable usage SKU as needed.
- **`RatingFrequencyPolicy`** — e.g. **Monthly** (Upsert by **`RatingPeriod`**).
- **`ProductUsageResourcePolicy`** — Per PUR: rating period, **`UsageAggregationPolicy.Code`** aligned with **`UsageResourceBillingPolicy`**, overage (**Insert** after scoped delete).
- **`ProductUsageGrant`** — Grant rows; include **`$$`** composite column matching **`export.json`** **`externalId`** for SFDMU v5.

## Prerequisites (load order)

1. **`customer-template-pcm`** loaded with **`UnitOfMeasureClass`**, **`UnitOfMeasure`**, sellable usage SKUs, and usage-definition **`Product2`** rows your **`UsageResource`** rows reference.
2. Org **`ProductSellingModel`** names match pricebook and rate-card rows.
3. Align **`delete_customer_demo_*` Apex** SKU/code lists and **`customer_demo_purge_records`** with the prefixes you use (see repo scripts under **`scripts/apex/`** and **`scripts/customer-demo/`**).

## Deletes and reload order

- **`customer_demo_purge_records`** — quote/order usage **policies** and **grants** on demo meters so teardown can run.
- **`delete_customer_demo_rates_data`** before **`delete_customer_demo_rating_data`** when **`RateCardEntry`** still references demo **`UsageResource`** rows.
- Run **`delete_customer_demo_rating_data`** immediately before **`insert_customer_demo_rating_data`** on reloads.

## CCI

- `insert_customer_demo_rating_data` — `sync_objectset_source_to_source: true` for pass 2 **`UsageResource`** status update.
- `delete_customer_demo_rating_data` — scoped Apex cleanup.
- `prepare_customer_demo_catalog` / `prepare_customer_demo_usage` with `customer_demo_usage: true`.

## Passes

1. **Pass 1:** Policies, **`UsageResource`**, **`Product2`** update, **`PUR`**, binding, **`RatingFrequencyPolicy`**, **`PURP`**, **`PUG`**.
2. **Pass 2:** **`UsageResource`** activation (CSV under `objectset_source/object-set-2/`).

Then **`activate_rating_records`**.

## Post-load verification (critical)

**`ProductUsageGrant` has a confirmed SFDMU v5 silent-failure bug:** the `Insert` operation reports "1 records processed, 0 records failed" but the record never appears in the org. This happens even when all parent lookups resolve correctly. **Always verify after every rating load:**

```bash
sf data query -q "SELECT Id, Quantity, Status FROM ProductUsageGrant \
  WHERE ProductUsageResource.Product.StockKeepingUnit = '<your-usage-sku>'" \
  --target-org <alias>
```

If the PUG is missing, insert via Apex (query the PUR, UOM, UOM class, definition product, and policy records by their codes/names, then `insert new ProductUsageGrant(...)`). Then activate: `pug.Status = 'Active'; update pug;` (or re-run `activate_rating_records`).

**Grant policy records also silently fail:** `UsageGrantRenewalPolicy`, `UsageGrantRolloverPolicy`, `UsageOveragePolicy` Upserts log "Inserted 1" but records don't persist. This is why the template CSVs reference existing org policies rather than creating new ones. If you see `MissingParentRecordsReport.csv` entries for `RenewalPolicy.Code` or `RolloverPolicy.Code` on `ProductUsageGrant`, this is the cause.

## Quote testing

Add **sellable usage** SKUs to the quote, not usage-definition-only products. See **`docs/guides/customer-demo-onboarding.md`**.

## Reference

**`datasets/sfdmu/qb/en-US/qb-rating/`** — full QuantumBit rating shape.
