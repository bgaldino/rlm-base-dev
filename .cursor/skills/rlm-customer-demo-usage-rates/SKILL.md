---
name: rlm-customer-demo-usage-rates
description: >-
  Builds or extends Revenue Cloud customer-demo usage (UsageResource, PUR), rate cards
  (RateCardEntry Base vs Tier, RateAdjustmentByTier on CD-DEMO Tier Rate Card), and SFDMU
  plans under datasets/sfdmu/customer-template. Covers ProductSellingModel alignment
  between RateCardEntry and Standard PricebookEntry (customer-pricebook-entries.csv),
  RABT vs PriceAdjustmentTier, UsageResource CSV UnitOfMeasureClass.Name and
  DefaultUnitOfMeasure.Name for SFDMU v5 parent resolution, ProductUsageGrant UOM Name
  columns, UsageModelType Anchor vs Pack (PURP / quote persist), customer_demo_purge_records
  vs QLIURG, delete_customer_demo_rates_data scope (Base+Tier+RABT), MissingParentRecordsReport
  triage, customer_demo_recreate_pricebook_via_api upsert behavior, and CumulusCI org
  defaults for activate_rating_records / activate_rates. Use when onboarding customer
  demo catalogs with usage metering, rating data loads, CD-DEMO Base and Tier rate cards,
  ProductUsageResource, tier bands, effective dates, or customer_demo_usage flows.
---

# RLM customer demo — usage, rating, and rates

## When to read this

Apply when working on **`datasets/sfdmu/customer-template`**, **`customer_demo_usage`**, sellable usage SKUs (**`SF-USG-*`**; **`UsageModelType` = `Anchor`** for PURP/PUG), **`UsageResource`**, **`ProductUsageResource`**, **`RateCard` / `RateCardEntry` / `RateAdjustmentByTier`** (**`CD-DEMO`** Base + Tier template), or extending toward **QuantumBit `qb-rating` / `qb-rates`** patterns.

**Canonical repo docs (read these for full detail):**

- `docs/guides/customer-demo-usage-metered-products.md` — **durable** usage-metered demo patterns (any customer; `SF-*` example data replaceable)
- `docs/references/customer-template-usage-resource.md` — **UsageResource** + **ProductUsageResource**
- `docs/references/customer-template-rate-card-entry.md` — **RateCardEntry**, Base vs Tier, effective dates
- `docs/references/customer-template-tier-rate-card-lessons-learned.md` — **RateAdjustmentByTier**, SFDMU **Insert**, RCE **Draft** ordering, Apex delete + cascade, **not** **`PriceAdjustmentTier`**
- `docs/guides/customer-demo-onboarding.md` — end-to-end step order
- `AGENTS.md` — Customer Demo Product Onboarding UX (PCM → usage → rates)

**Deeper tables and file map:** [reference.md](reference.md)

## Load order (do not reorder)

1. **`customer-template-pcm`** — `Product2` (sellable **`SF-USG-*`**, usage-definition **`SF-BLNG-*`**), **UOM / UOM class** used by meters.
2. **`customer-template-rating`** — **URBP**, **UsageResource**, grant policies (renewal/rollover/overage), **Product2** update, **PUR**, **UsagePrdGrantBindingPolicy**, **RatingFrequencyPolicy**, **ProductUsageResourcePolicy**, **ProductUsageGrant**. Pass 2 activates **UsageResource**; then **`activate_rating_records`** (PUR → PUG activation order).
3. **`customer-template-rates`** — **RateCard** (**`CD-DEMO Base`** + **`CD-DEMO Tier`**), **PriceBookRateCard** (Base + **Tier** link rows), **RateCardEntry** (Insert, Draft — Base rows carry **`Rate`**; Tier rows leave **`Rate`** empty), **RateAdjustmentByTier** (Insert, only for Tier card — same pass as RCE so parent stays **Draft**); then **`activate_rates`**.

**Idempotency:** When re-importing **rating**, run **`delete_customer_demo_rates_data`** **before** **`delete_customer_demo_rating_data`** if **RateCardEntry** references **`SF-UR-*`** (otherwise **UsageResource** delete fails). **`delete_customer_demo_rates_data`** clears **both** CD-DEMO cards, all demo **RCE**, **RABT** (cascade on RCE delete), and **PriceBookRateCard** rows for those cards. Then **`delete_customer_demo_rating_data`** (removes **PUG → PURP → PUR → UR** for demo SKUs). Customer plans avoid global **`deleteOldData`** on RCE/RABT/PURP/PUG so non-demo org data stays intact; scoped Apex + explicit delete-before-insert handle the demo slice.

## Data model (mental model)

| Piece | Role |
|-------|------|
| **UsageResource** | Meter: **Category = Usage**, UOM class + default UOM, **UsageDefinitionProduct** (`SF-BLNG-*`), **UsageResourceBillingPolicy**. |
| **ProductUsageResource** | Junction: **sellable Pack SKU** (`SF-USG-*`) → **UsageResource** (`SF-UR-*`). Required for rating/rates to resolve product → meter. |
| **RateCard** + **RateCardEntry** | Prices **product × UsageResource × rate UOM** + **ProductSellingModel** + **DefaultUnitOfMeasure** (consumption) vs **RateUnitOfMeasure** (money). |
| **RateAdjustmentByTier** | Child of **RateCardEntry** on **`RateCard.Type = Tier`**. Stepped **`Override`** / **`Percentage`** by **`LowerBound`/`UpperBound`** in the **consumption** UOM of the line. **Not** **`PriceAdjustmentTier`** ( **`PriceAdjustmentSchedule`** — see **`qb-pricing`** ). |
| **ProductUsageResourcePolicy** | Per-PUR: **Monthly** rating, **UsageAggregationPolicy.Code** = same **Code** as **UsageResourceBillingPolicy** (**monthlypeak** / **monthlytotal**), default overage. |
| **ProductUsageGrant** | Per-PUR **Grant** (included qty, renewal/rollover, **`SF-BLNG-*`** usage-definition product) — **QuantumBit `QB-DB`** pattern. |

Customer template loads **Base + Tier** demo rate cards and **RateAdjustmentByTier** under **`customer-template-rates`**. For **Attribute** cards or alternate tier matrices, still mirror **`qb-rates`**.

## ProductSellingModel on RateCardEntry (must match PricebookEntry)

**`RateCardEntry.ProductSellingModelId`** must be the **same** **`ProductSellingModel`** as the product’s **Standard `PricebookEntry`** for that SKU (**`scripts/customer-demo/customer-pricebook-entries.csv`** → **`PSMName`** / **`PSMSellingModelType`**). Mismatch (e.g. RCE **One-Time** while PBE is **Term Monthly**) breaks quote/pricing consistency. Template usage SKUs (**`SF-USG-*`**) use **Term Monthly** (**TermDefined**).

## Base vs tiered rate cards

- **Base (`RateCard.Type = Base`):** Set **`Rate`**, **`RateUnitOfMeasure`**, **`RateNegotiation`** (e.g. **Negotiable**) **on the RateCardEntry**. Template: **`CD-DEMO Base Rate Card`** rows in **`customer-template-rates/RateCardEntry.csv`**.
- **Tier (`RateCard.Type = Tier`):** **RateCardEntry** rows use **empty `Rate`**; stepped pricing on **`RateAdjustmentByTier`**. **`export.json`** lists **RCE** before **RABT** so **RABT inserts while parent RCE is still `Draft`**; then **`activate_rates`**. Template: **`CD-DEMO Tier Rate Card`** + **`RateAdjustmentByTier.csv`**. **`ProductSellingModel`** on Tier **RCE** must still match **Standard PBE** per SKU (same as Base). Advanced patterns: **`datasets/sfdmu/qb/en-US/qb-rates`**.

## Effective dates and activation

- **RateCardEntry.EffectiveFrom** (and **RateCard** window) must be **on or after** the card’s validity and **strictly before** the calendar day you treat as “sell / quote demo day” so rates are in force.
- **RateCardEntry** loads as **Draft** → **`activate_rates`** sets **Active**.
- **UsageResource** / **PUR** follow **`activate_rating_records`** (after SFDMU); see `scripts/apex/activateRatingRecords.apex` for token vs non-token PUR behavior.

## SFDMU v5 (critical)

- **externalId** uses **`;`** delimiters, not v4 `$$` in **export.json** (CSV may still use **`$$`** composite columns per plan).
- **Relationship-traversal externalIds** often force **Insert** + scoped delete or **`deleteOldData: true`** — see `CLAUDE.md` / `docs/references/sfdmu-composite-key-optimizations.md`. Do **not** switch Upsert → Insert + deleteOldData on existing plans without user approval and bug justification.

## Extending the template

1. Add PCM rows first (SKUs, UOMs, bundles as needed).
2. Add **UsageResource** + **PUR** rows with stable **Code** / SKU references.
3. Add **RateCardEntry** rows matching **product + UR + rate UOM**; **`ProductSellingModel.Name` (+ org `SellingModelType`) must match that SKU’s Standard `PricebookEntry`** (**`customer-pricebook-entries.csv`**), not merely “any valid PSM in the org.”
4. For tiers: add **RateCard** (**Tier**), **PriceBookRateCard** (**RateCardType = Tier**), **RateCardEntry** (Draft, empty **Rate**), **RateAdjustmentByTier** (composite **`$$`** parent key matches **RCE** externalId shape) — see existing **`customer-template-rates`** or **qb-rates** `export.json` and README.
5. Run **`python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/customer-template/en-US/customer-template-rates`** (or the plan path you changed). Expect a possible **Medium** validator note on **`RateCardEntry.RateCard.Name`** in RABT **externalId**; **Insert** still works (same as **qb-rates**).

## Product2 typing

**`Product2.Type`**: org picklists typically allow **Bundle** or blank — verify before inserts; see onboarding docs and verify tasks.

## Field-tested findings (keep these in mind)

| Topic | What we learned |
|-------|------------------|
| **RateCardEntry ↔ PricebookEntry** | **`ProductSellingModel` on RCE must match Standard PBE** for the same SKU. Source of truth for demo SKUs: **`scripts/customer-demo/customer-pricebook-entries.csv`** (`PSMName`, `PSMSellingModelType`). **`SF-USG-*`** use **Term Monthly** / **TermDefined** — do not use **One-Time** on RCE unless PBE also uses One-Time. |
| **UsageResource CSV / SFDMU v5** | **`UnitOfMeasureClass.Name`** and **`DefaultUnitOfMeasure.Name`** are required alongside **`.Code`** / **`.UnitCode`** so parent lookups resolve; without them, **`reports/MissingParentRecordsReport.csv`** shows placeholder parent IDs and **SF-UR-*** rows may not load. Align names with PCM **`UnitOfMeasure`** / **`UnitOfMeasureClass`** rows. |
| **`customer_demo_recreate_pricebook_via_api`** | Uses **query-by-(Pricebook + Product + Currency) → PATCH or POST** (not delete-only). **Quote lines** can block **PricebookEntry** delete — task logs warnings and **updates in place**. If **`ProductSellingModelId`** is not editable (FLS), task **PATCHes price/active** and **verifies** existing PSM matches CSV or fails clearly. Implementation: **`tasks/rlm_customer_demo.py`**. |
| **CumulusCI `--org` on some tasks** | On some CCI versions, **`cci task run activate_rating_records --org <alias>`** errors with **No such option: --org**. Use **`cci org default <alias>`** then **`cci task run activate_rating_records`** (same for **`activate_rates`**), or run **`cci flow run prepare_customer_demo_catalog --org <alias>`** which passes the org correctly. |
| **Reload rates after PSM fix** | **`delete_customer_demo_rates_data`** → **`insert_customer_demo_rates_data`** → **`activate_rates`** (flow does this when `customer_demo_usage` is true). |
| **Rating delete / UR blocked** | **RateCardEntry** or **QLIURG** still references **`UsageResource`**. Delete **CD-DEMO** rates first; run **`customer_demo_purge_records`** (clears **QuotLineItmUseRsrcGrant** / **OrderItemUsageRsrcGrant** on **`SF-UR-*`**) or fix quote lines; then **`delete_customer_demo_rating_data`**. |
| **Tier rates / RABT** | Confusing **`RateAdjustmentByTier`** with **`PriceAdjustmentTier`**, or putting flat **`Rate`** on Tier **RCE**. Usage **rate card** tiers = **RABT** on **`RateCardEntry`**. **`PriceAdjustmentTier`** belongs to **`PriceAdjustmentSchedule`**. Tier **RCE**: **empty `Rate`**; bands in **`RateAdjustmentByTier.csv`**. |
| **RABT load failure** | Parent **RCE** already **Active** or wrong object order | Single-pass order: **RCE** then **RABT** in **`export.json`**. Do not activate until after SFDMU finishes. |
| **Stale tier rows on reload** | Insert-only RABT without delete | **`delete_customer_demo_rates_data`** before **`insert_customer_demo_rates_data`** (removes **Base + Tier** cards and cascaded children). |
| **`AttributePicklistValue.Code` collision** | `Code` is the **global externalId** — two APVs with the same `Code` across different picklists collide. One insert overwrites the other, and downstream `AttributeDefinition`, `AttributeCategoryAttribute`, `ProductClassificationAttr`, `ProductAttributeDefinition` cascade-fail with missing parents, potentially aborting the entire PCM job. | Ensure every `Code` is org-unique per APV; use prefixed codes when the same label appears in multiple picklists (e.g. `XLarge` not reused `Enterprise`). |
| **`AttributeDefinition.DeveloperName` conflict** | `DeveloperName` is org-unique. Packages or prior demos may already own names like `Service_Tier`. | Prefix customer-specific developer names (e.g. `RK_Service_Tier`). |
| **`CategoryCode` in pricebook CSV** | `customer_demo_verify_catalog` checks `ProductCategoryProduct` per SKU + category. Empty `CategoryCode` causes all-SKU **"missing category"** false alarm. | Always populate `CategoryCode` in **`customer-pricebook-entries.csv`** with the `ProductCategory.Code` for each SKU. |
| **Static resource + DisplayUrl sequencing** | `DisplayUrl` in PCM `Product2.csv` resolves only after `deploy_customer_demo_staticresources`. Setting it in PCM before resources exist produces a broken URL. | Leave `DisplayUrl` empty in PCM CSV. Populate via **`customer-template-product-images`** (step 5) after static resource deploy (step 3). |
| **Grant policy SFDMU silent failure** | `UsageGrantRenewalPolicy`, `UsageGrantRolloverPolicy`, `UsageOveragePolicy` Upserts log "Inserted 1" but records never persist. Downstream `ProductUsageGrant` and `ProductUsageResourcePolicy` then fail parent lookups (`MissingParentRecordsReport.csv`). | **Always reference existing org policies** (e.g. `SF-DEMO-USG-RENEW`, `SF-DEMO-USG-ROLL`, `Default Usage Overage Policy`). Do not create customer-specific policy records via SFDMU. Create via Apex/UI if needed. |
| **`ProductUsageGrant` SFDMU silent failure** | SFDMU `Insert` for `ProductUsageGrant` reports "1 records processed, 0 records failed" but the record never appears in the org — confirmed on multiple runs even with all parent lookups resolving correctly (no `MissingParentRecordsReport.csv`). | **Always verify** PUG after rating load: `sf data query ... WHERE ProductUsageResource.Product.StockKeepingUnit = '<sku>'`. If missing, insert via Apex fallback. `activate_rating_records` Step 6 will activate it; if already past activation, manually set `Status = 'Active'`. |
| **Re-run safety** | PCM Upserts are safe to re-run — existing records match on `externalId` and update. Downstream steps are also idempotent. Partial failure can be fixed and the full flow re-run without manual cleanup. |

Full checklist: [reference.md — Findings and triage](reference.md#findings-and-triage).
