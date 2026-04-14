# Reference — customer demo usage & rates

## Findings and triage

Use this when something “should have loaded” but the org looks empty or wrong.

| Symptom | Likely cause | Fix |
|--------|----------------|-----|
| No **SF-UR-*** / **PUR** after rating load | **UsageResource** parent lookups failed | Open **`customer-template-rating/reports/MissingParentRecordsReport.csv`**. Populate **`UsageResource.csv`** **`UnitOfMeasureClass.Name`** + **`DefaultUnitOfMeasure.Name`** to match PCM (see rating README). Re-run **`delete_customer_demo_rating_data`** → **`insert_customer_demo_rating_data`** → **`activate_rating_records`**. |
| **`UsageResource` delete fails** (RCE or **QLIURG**) | **RateCardEntry** or **quote** still references the meter | **`delete_customer_demo_rates_data`** first; run **`customer_demo_purge_records`** (deletes **QuotLineItmUseRsrcGrant** / **OrderItemUsageRsrcGrant** on **`SF-UR-*`**) or remove quote lines; retry **`delete_customer_demo_rating_data`**. |
| **Quote save** **`PlaceSalesTransactionPersistException`** / index errors on usage lines | Incomplete usage shape (often **no PURP** on **`SF-USG-*`**) | Ensure **`UsageModelType = Anchor`** on **`SF-USG-*`**, reload rating, remove/re-add quote lines. |
| **PUR** shows **0** PURP | **`SF-USG-*`** has **`UsageModelType = Pack`** | Set **`Anchor`** in **`customer-template-rating` / `customer-template-rates` `Product2.csv`** (same as **QB-DB**). **`Pack`** blocks **`ProductUsageResourcePolicy`** (“pack usage model type”). Reload rating after fixing. |
| **PUR** shows **0** PUG | SFDMU UOM parent resolution | Add **`UnitOfMeasure.Name`** + **`UnitOfMeasureClass.Name`** to **`ProductUsageGrant.csv`**; check **`MissingParentRecordsReport.csv`**. |
| **PUR** shows **0** PURP / PUG (other) | Rating slice not reloaded | Run full rating delete + insert; **`UsageAggregationPolicy.Code`** on PURP must match **`UsageResourceBillingPolicy.Code`**. |
| **Rate Card Entry** shows wrong **Product Selling Model** vs product / PBE | **RateCardEntry.csv** PSM ≠ **`customer-pricebook-entries.csv`** | Set **`ProductSellingModel.Name`** (and ensure org **`SellingModelType`** matches) per SKU on **both** Base and Tier **RCE** rows; ensure **`ProductSellingModel.csv`** lookup includes that PSM. **`delete_customer_demo_rates_data`** → **`insert_customer_demo_rates_data`** → **`activate_rates`**. |
| **Tier / RABT** wrong object or load order | Treat **`PriceAdjustmentTier`** as usage rate tiers, or activate **RCE** before **RABT** insert | Usage meters on **rate cards** use **`RateAdjustmentByTier`** ( **`RateCard.Type = Tier`** ). **`PriceAdjustmentTier`** is for **`PriceAdjustmentSchedule`**. Keep **`export.json`** **RCE** before **RABT**; run **`activate_rates`** only after SFDMU. See **`docs/references/customer-template-tier-rate-card-lessons-learned.md`**. |
| **Duplicate tier rows** on reload | **Insert**-only **RABT** without clearing demo slice | **`delete_customer_demo_rates_data`** before **`insert_customer_demo_rates_data`** (removes **CD-DEMO Base + Tier** and cascaded **RCE** / **RABT**). |
| **PricebookEntry** duplicate / delete weirdness | Quotes reference PBE | Expect **PATCH** path in **`RecreateCustomerDemoPricebookViaApi`**; grant **ProductSellingModelId** edit on PBE if you must rewrite PSM. |
| **`activate_rating_records` fails CLI** | **`--org` not accepted** on **`cci task run`** | **`cci org default <alias>`** or use **flow** with **`--org`**. |
| **`customer_demo_verify_catalog`** reports **"ProductCategoryProduct missing for category"** on all SKUs | **`CategoryCode`** empty in **`customer-pricebook-entries.csv`** | Populate **`CategoryCode`** with the **`ProductCategory.Code`** for each SKU (e.g. `PC-RK-COMMERCIAL`). The verify task requires this column to validate category assignments. |
| **PCM cascade failure** — APV insert fails, then AttributeDefinition, AttributeCategoryAttribute, ProductClassificationAttr, ProductAttributeDefinition all report missing parents | Duplicate **`AttributePicklistValue.Code`** across different picklists — `Code` is a global externalId | Every `AttributePicklistValue.Code` must be unique org-wide. Use prefixed codes when the same label appears in multiple picklists (e.g. `XLarge` not a reused `Enterprise`). |
| **`AttributeDefinition`** insert fails (1 of N processed, 1 failed) | **`DeveloperName`** collision with existing org metadata | Prefix customer-specific `DeveloperName` values (e.g. `RK_Service_Tier` not `Service_Tier`). |
| **`UnitOfMeasure`** Update errors on re-run (benign) | Org-native UOMs (e.g. `USD`) exist; some fields not updatable | Ignore — existing UOM is correct; only new UOMs need Insert. |
| **PCM aborts with `ERROR_HTTP_404`** after partial load | Upstream object failed (APV/AttrDef), cascading to all downstream lookups | Fix root-cause failure, re-run. Upsert is safe to repeat. |
| **PUG missing after rating load** — SFDMU logs "1 processed, 0 failed" but PUG not in org | **SFDMU v5 silent failure** on `ProductUsageGrant` Insert — confirmed bug where REST API reports success but record never persists | **Always verify** PUG after load: `sf data query -q "SELECT Id, Quantity, Status FROM ProductUsageGrant WHERE ProductUsageResource.Product.StockKeepingUnit = '<sku>'"`. If missing, insert via **Apex** (`ProductUsageGrant pug = new ProductUsageGrant(); pug.ProductUsageResourceId = ...; insert pug;`). Then activate (`pug.Status = 'Active'; update pug;`). |
| **Grant policies** (`UsageGrantRenewalPolicy` / `UsageGrantRolloverPolicy` / `UsageOveragePolicy`) **missing after Upsert** — SFDMU logs "Inserted 1" but records don't exist | **SFDMU v5 silent failure** on setup-like objects — REST Insert reports success, records never persist | **Do not create via SFDMU.** Reference **existing org policies** (e.g. `SF-DEMO-USG-RENEW`, `SF-DEMO-USG-ROLL`, `Default Usage Overage Policy`). Create custom policies via Apex/UI before SFDMU load if needed. Without these parent records, `ProductUsageGrant` and `ProductUsageResourcePolicy` fail parent lookups (`MissingParentRecordsReport.csv` shows missing `RenewalPolicy.Code`, `RolloverPolicy.Code`, `UsageOveragePolicy.Name`). |
| **`UsageOveragePolicy` name mismatch** — `Default Overage` vs `Default Usage Overage Policy` | Org's actual policy name differs from CSV | Query org: `SELECT Name FROM UsageOveragePolicy`. Use the **exact org name** in `ProductUsageResourcePolicy.csv` → `UsageOveragePolicy.Name`. |

Repo narrative: **`docs/guides/customer-demo-usage-metered-products.md`** (durable usage-metered demo lessons), **`docs/guides/customer-demo-onboarding.md`** (Troubleshooting), **`docs/references/customer-template-rate-card-entry.md`**, **`docs/references/customer-template-tier-rate-card-lessons-learned.md`**, **`docs/references/customer-template-usage-resource.md`**.

## Directory map

| Plan | Path |
|------|------|
| PCM | `datasets/sfdmu/customer-template/en-US/customer-template-pcm` |
| Rating | `datasets/sfdmu/customer-template/en-US/customer-template-rating` |
| Rates | `datasets/sfdmu/customer-template/en-US/customer-template-rates` |
| Full QB (patterns) | `datasets/sfdmu/qb/en-US/qb-rating`, `qb-rates` |

## Snowflake template SKU prefixes (illustrative)

| Prefix | Meaning |
|--------|---------|
| `SF-USG-*` | Sellable usage SKUs (**quote these**); **`UsageModelType` = `Anchor`** (not **`Pack`**) for PURP/PUG |
| `SF-BLNG-*` | **Usage-definition** products (**UsageResource.UsageDefinitionProduct**) |
| `SF-UR-*` | **UsageResource.Code** (meters) |

## Rating CSV roles (customer-template-rating)

- **UsageResourceBillingPolicy.csv** — Upsert shared policies (**`monthlypeak`**, **`monthlytotal`**); not wiped by customer demo rating delete.
- **UsageResource.csv** — Meters; **Category = Usage**; **`.Name` columns on UOM class and default UOM** (not only **`.Code`** / **`.UnitCode`**) for SFDMU v5; links to **UsageDefinitionProduct**, **UsageResourceBillingPolicy**.
- **UsageGrantRenewalPolicy.csv**, **UsageGrantRolloverPolicy.csv**, **UsageOveragePolicy.csv** — Support **PUG** / **PURP** (Snowflake demo codes **`SF-DEMO-USG-*`**).
- **Product2.csv** — **`UsageModelType = Anchor`** on **`SF-USG-*`** (QB-DB pattern; **`Pack`** blocks PURP).
- **ProductUsageResource.csv** — **`$$Product.StockKeepingUnit$UsageResource.Code`**; **Insert**; links Pack → UR.
- **UsagePrdGrantBindingPolicy.csv** — **Self** binding per **`SF-USG-*`**.
- **RatingFrequencyPolicy.csv** — **Monthly** (global).
- **ProductUsageResourcePolicy.csv** — Per-PUR policy (**monthlypeak** / **monthlytotal** aggregation Code).
- **ProductUsageGrant.csv** — Per-PUR **Grant** rows (**`SF-BLNG-*`** definition products).

**export.json:** object set pass 2 activates **UsageResource** from `objectset_source/object-set-2/`.

## Rates CSV roles (customer-template-rates)

- **RateCard.csv** — **`CD-DEMO Base Rate Card`** (**`Type = Base`**) and **`CD-DEMO Tier Rate Card`** (**`Type = Tier`**), effective window.
- **PriceBookRateCard.csv** — **Standard Price Book** links: one row per card (**`RateCardType`** **`Base`** or **`Tier`** must match **`RateCard.Type`**).
- **RateCardEntry.csv** — Composite key **Product;RateCard;UsageResource;RateUnitOfMeasure**. **Base** rows: set **`Rate`**, **`RateNegotiation`** (e.g. **Negotiable**). **Tier** rows: **empty `Rate`**; same **PSM** / UOM binding as Base for that SKU × meter. **`ProductSellingModel.Name`** must match **Standard PricebookEntry** (**`customer-pricebook-entries.csv`**). **Draft** until **`activate_rates`**.
- **RateAdjustmentByTier.csv** — Bands (**`LowerBound`**, **`UpperBound`**, **`AdjustmentType`**, **`AdjustmentValue`**) for **Tier** card lines only. Parent **`RateCardEntry.$$...`** composite must match the corresponding **RCE** row. **`export.json`** places this object **after** **RateCardEntry** so **RABT** inserts while parent **RCE** is still **Draft**. **`Insert`** operation (relationship **externalId** — same v5 pattern as **qb-rates**).

**`delete_customer_demo_rates_data`:** Apex removes **both** CD-DEMO cards, deactivates/deletes **RCE** (child **RABT** cascade), deletes **PriceBookRateCard** for those cards, then deletes **RateCard** records.

Lookup-only CSVs in the same folder (not always separate `objects` in export): **Pricebook2**, **ProductSellingModel**, **UsageResource**, **UnitOfMeasure**, **UnitOfMeasureClass**, **Product2** — must match org names.

## CumulusCI tasks (names)

- `insert_customer_demo_pcm_data`, `insert_customer_demo_rating_data`, `insert_customer_demo_rates_data`
- `delete_customer_demo_rating_data`, `delete_customer_demo_rates_data`
- `activate_rating_records`, `activate_rates`
- Flow: `prepare_customer_demo_catalog` with **`customer_demo_usage: true`** in project `custom`, or `prepare_customer_demo_usage` after catalog through pricebook + verify

## Quote / UX notes

- Quote **Pack** SKUs (**`SF-USG-*`**), not **`SF-BLNG-*`**, for normal usage demos.
- Product record UI: **ProductUsageResources** related list shows PUR wiring.

## Implementation pointers

- **`tasks/rlm_customer_demo.py`** — **`RecreateCustomerDemoPricebookViaApi`**, **`VerifyCustomerDemoCatalog`**
- **`scripts/customer-demo/customer-pricebook-entries.csv`** — PSM per SKU (must stay aligned with **`RateCardEntry.csv`**)

## Further reading

- `datasets/sfdmu/customer-template/en-US/customer-template-rating/README.md`
- `datasets/sfdmu/customer-template/en-US/customer-template-rates/README.md`
- `docs/references/customer-template-tier-rate-card-lessons-learned.md`
- `datasets/sfdmu/qb/en-US/qb-rating/README.md`, `qb-rates/README.md`
