# Customer demo catalog onboarding

Runbook for loading the **customer-template** datasets and avoiding common SFDMU / org pitfalls. Agents should follow **`AGENTS.md` → Customer Demo Product Onboarding UX** for conversational onboarding; this document is the technical reference.

**Ephemeral vs durable:** The concrete **Snowflake-style `SF-*` SKUs**, logos, and rate-card names in `datasets/sfdmu/customer-template/` can be **replaced or purged** when switching to another customer or practice. **`docs/guides/customer-demo-usage-metered-products.md`** captures **transferable** rules for **any** usage-metered demo ( **`UsageModelType`**, SFDMU **Name** columns, PURP/PUG, QLIURG, quotes); **`qb-rating`** remains the **canonical product-shape reference**.

**Cursor:** the project skill **`.cursor/skills/rlm-customer-demo-usage-rates`** (`SKILL.md` + `reference.md`) summarizes load order, **UsageResource** / **ProductUsageResource** / **RateCardEntry** (**CD-DEMO Base** flat **`Rate`** vs **CD-DEMO Tier** + **`RateAdjustmentByTier`**), **`delete_customer_demo_rates_data`** scope (**Base + Tier** + cascade **RABT**), activations, and SFDMU cautions. **`SKILL.md` → “Field-tested findings”** and **`reference.md` → “Findings and triage”** capture lessons from real deploys (RCE **ProductSellingModel** = Standard PBE on **all** RCE rows, **RABT** vs **`PriceAdjustmentTier`**, **UsageResource** UOM **Name** columns for v5, pricebook API upsert / quotes / FLS, CCI **`--org`** on **`activate_*`** tasks). Tier-specific consolidation: **`docs/references/customer-template-tier-rate-card-lessons-learned.md`**.

## Flow and flag

```bash
# Set customer_demo_usage: true in cumulusci.yml project → custom (or org override) to include rating + rates + activations
cci flow run prepare_customer_demo_catalog --org <alias>
```

**Step order (summary):** **`customer_demo_purge_records`** (removes **QLIURG** / **OrderItemUsageRsrcGrant** on **`SF-UR-*`** so rating delete can run) → PCM → deploy `unpackaged/post_customer_demo/staticresources` → product-images SFDMU → billing SFDMU → `customer_demo_recreate_pricebook_via_api` → `customer_demo_verify_catalog` → (if usage) **`delete_customer_demo_rates_data`** (clears **CD-DEMO Base + Tier**, **RCE**, **RABT**, **PriceBookRateCard**) → **`delete_customer_demo_rating_data`** → insert rating → insert rates (**RateCard**, **PBRC**, **RCE**, **`RateAdjustmentByTier`**) → `activate_rating_records` → `activate_rates`.

## Product2 CSV shape (SFDMU) — critical

The PCM `export.json` **Product2** query selects `BasedOnId`, `UnitOfMeasureId`, `QuantityUnitOfMeasure`, and related fields. If the CSV **omits** the relationship columns SFDMU expects, the tool can still report inserts as “processed” while **lookup resolution fails** (bogus parent keys like `ID000…` in **`reports/MissingParentRecordsReport.csv`**). Downstream tasks then fail (e.g. **Missing Product2 records for SKUs** in `customer_demo_recreate_pricebook_via_api`) even though the log showed Product2 activity.

**Mitigation:** align **`Product2.csv`** with the same **column pattern as `datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv`**:

| Column | Typical customer-template usage |
|--------|----------------------------------|
| `BasedOn.Code` | Leave **empty** unless the product is based on a `ProductClassification` |
| `CanRamp` | `false` for template SKUs |
| `ConfigureDuringSale` | **Allowed** only on parent **Bundle** rows; otherwise empty |
| `IsSoldOnlyWithOtherProds` | `false` |
| `QuantityUnitOfMeasure` | Often **`EACH`** (confirm `UnitOfMeasure` with `UnitCode=EACH` exists in the org) |
| `UnitOfMeasure.UnitCode` | **`EACH`** (or another org-native default quantity UOM) |
| `Type` | **`Bundle`** only for parent bundle SKUs; **blank/null** for all others (see `AGENTS.md`) |
| `DisplayUrl` | Usually left empty in PCM; set via `customer-template-product-images` after static resource deploy |

After any PCM load, if behavior is suspicious, open **`datasets/sfdmu/.../customer-template-pcm/reports/MissingParentRecordsReport.csv`** and fix CSV columns before re-running.

## Catalog verification and pricebook CSV

- **`scripts/customer-demo/customer-pricebook-entries.csv`** drives both API pricebook recreation and **`customer_demo_verify_catalog`**.
- Include **`ProductTypeExpected`**: `Bundle` on bundle SKUs, **empty** on all others — verify then enforces **Type = Bundle vs blank** (not “any non-null type”).
- If `ProductTypeExpected` is **absent**, **`require_product_type`** (default **true**) requires `Type` non-blank on every row.
- **`CategoryCode` is required** — populate with the **`ProductCategory.Code`** for each SKU (e.g. `PC-RK-COMMERCIAL`). The verify task checks that a `ProductCategoryProduct` row exists for each SKU + category pair. Leaving `CategoryCode` empty causes the verify step to report **"ProductCategoryProduct missing for category"** on every SKU, even when catalog objects loaded correctly.

## Usage and rates prerequisites

- **PCM** must define **sellable** usage products (**`SF-USG-*`**), **usage-definition** `Product2` rows (**`SF-BLNG-*`**), and **UOM / UOM class** codes referenced by `UsageResource` (template uses `DATAVOL`, `SNFCRED`; keep names aligned across PCM, rating, and rates lookup CSVs).
- **`UsageModelType` on sellable usage SKUs (`SF-USG-*`):** the **`customer-template-rating`** and **`customer-template-rates`** plans set **`Anchor`** (same as QuantumBit **`QB-DB`**). **`Pack`** is invalid for this shape: the platform **rejects `ProductUsageResourcePolicy`** (“pack usage model type” error), **PURP** never persists, and quote save can fail with **`PlaceSalesTransactionPersistException`** (e.g. index / persist errors). Do not change **`SF-USG-*`** back to **`Pack`** for tier-1 usage demos.
- **`UsageResource` design:** see **`docs/references/customer-template-usage-resource.md`** — **`Category = Usage`**, **default UOM ∈ UOM class**, **`UsageDefinitionProduct`** (`SF-BLNG-*`), **`UsageResourceBillingPolicy`** (template Upserts **`monthlypeak`** + **`monthlytotal`**; shared policies are **not** deleted by `delete_customer_demo_rating_data`).
- **Grant policies must reference existing org records** — `UsageGrantRenewalPolicy`, `UsageGrantRolloverPolicy`, and `UsageOveragePolicy` are **setup-like objects** that SFDMU may silently fail to create (the REST API Insert logs "processed 1" while the record never persists). **Do not create customer-specific policy records via SFDMU.** Instead, reference policies already in the org (e.g. `SF-DEMO-USG-RENEW`, `SF-DEMO-USG-ROLL`, `Default Usage Overage Policy`). If a matching policy does not exist, create it via Apex or the UI before running the SFDMU load.
- **`ProductUsageGrant` — verify after every load** — SFDMU's `Insert` operation for `ProductUsageGrant` can silently report success ("1 records processed, 0 records failed") while the record never appears in the org. This is a confirmed SFDMU v5 behavior with `ProductUsageGrant` specifically. After any rating load, **always verify**: `sf data query -q "SELECT Id, Quantity, Status FROM ProductUsageGrant WHERE ProductUsageResource.Product.StockKeepingUnit = '<usage-sku>'"`. If the PUG is missing, insert via Apex (see Troubleshooting).
- **`Default Proration Policy`** must exist (or change `ProductSellingModelOption` CSV to match the org’s proration policy **Name**).

## Testing on a quote

Add **sellable usage** lines, not usage-definition-only products:

| SKU | Use on quote |
|-----|----------------|
| `SF-USG-STORAGE` | Metered storage (TB) |
| `SF-USG-EGRESS` | Metered egress (GB) |
| `SF-USG-COMPUTE` | Metered compute credits (CRD) |

Do **not** add **`SF-BLNG-*`** to the quote for normal usage demos — those back **UsageResource** / rating design, not merchandising.

Template list price for usage lines is often **0**; **overage** is illustrated via **`CD-DEMO Base Rate Card`** (flat **`Rate`**) and optional **`CD-DEMO Tier Rate Card`** (**`RateAdjustmentByTier`** bands) after rates activation.

## Troubleshooting

- **`cci task run activate_rating_records --org <alias>`** may fail with **No such option: --org** on some CCI versions. Use **`cci org default <alias>`** then **`cci task run activate_rating_records`** (same for **`activate_rates`**), or rely on **`cci flow run prepare_customer_demo_catalog --org <alias>`**, which passes the org correctly.
- **`customer_demo_recreate_pricebook_via_api`**: quote lines can block **PricebookEntry** delete; the task **updates in place** when possible. If **`ProductSellingModelId`** is not editable for your user, ensure existing PBE already matches the CSV or adjust FLS.
- **Rating load / empty `SF-UR-*`**: check **`reports/MissingParentRecordsReport.csv`** under the rating plan directory. If **UnitOfMeasure** or **UnitOfMeasureClass** lookups show placeholder IDs, align **`UsageResource.csv`** **`UnitOfMeasureClass.Name`** and **`DefaultUnitOfMeasure.Name`** with PCM (see **`customer-template-rating/README.md`**).
- **`RateCardEntry` Product Selling Model wrong**: **`ProductSellingModel`** on **each** entry (Base **and** Tier **`RateCardEntry`** rows) must match **`PSMName`** / **`PSMSellingModelType`** for that SKU in **`scripts/customer-demo/customer-pricebook-entries.csv`** (usage **`SF-USG-*`** use **Term Monthly** / **TermDefined**). Fix **`customer-template-rates/RateCardEntry.csv`**, then **`delete_customer_demo_rates_data`** → **`insert_customer_demo_rates_data`** → **`activate_rates`**.
- **Tier rates confusion**: Usage **rate card** volume bands are **`RateAdjustmentByTier`** ( **`customer-template-rates/RateAdjustmentByTier.csv`** ), not **`PriceAdjustmentTier`**. Tier **`RateCardEntry`** rows keep **`Rate`** empty. See **`docs/references/customer-template-tier-rate-card-lessons-learned.md`**.
- **`delete_customer_demo_rating_data` fails on `UsageResource`**: Run **`delete_customer_demo_rates_data`** first if **CD-DEMO** rate entries reference **`SF-UR-*`**. If the error cites **quote line item usage resource grants** (**QLIURG** / **`QuotLineItmUseRsrcGrant`**), run **`cci task run customer_demo_purge_records`** (deletes those grants for **`SF-UR-*`**), or remove the quote lines manually, then retry.
- **`ProductUsageGrant` missing-parent / empty grants in org:** ensure **`UnitOfMeasure.Name`** and **`UnitOfMeasureClass.Name`** are present in **`ProductUsageGrant.csv`** (SFDMU v5 resolves those lookups like **`UsageResource.csv`**); see **`customer-template-rating/README.md`**.
- **`AttributePicklistValue` duplicate `Code`**: `Code` is the **global externalId** across all picklists. Two values with the same `Code` but different `Picklist.Name` will collide — the second insert fails or overwrites the first. Use unique codes per value (e.g. `Enterprise` for service tier, `XLarge` for property size). A failed APV cascades: the `AttributeDefinition` referencing that picklist may still load, but downstream `AttributeCategoryAttribute`, `ProductClassificationAttr`, and `ProductAttributeDefinition` fail with **missing parent** errors, potentially aborting the entire PCM job.
- **`AttributeDefinition.DeveloperName` conflicts**: `DeveloperName` must be unique across the org. If an RLM org already has a `Service_Tier` or `Property_Size` developer name from another package, the insert fails silently in the SFDMU batch. Prefix customer-specific developer names (e.g. `RK_Service_Tier`) to avoid collisions.
- **`UnitOfMeasure` update failures on re-run**: When UOMs like `USD` already exist in the org (from `qb-pcm`), the Upsert's Update phase may fail because fields like `ConversionFactor` or `Type` are not updatable. This is **benign** — the existing UOM is correct. The Insert phase for truly new UOMs (e.g. `EVENT`) succeeds.
- **Product images and static resources**: `DisplayUrl` should be left **empty** in the PCM `Product2.csv`. The flow deploys static resources at step 3 (after PCM at step 2), then the `customer-template-product-images` SFDMU step (step 5) sets `DisplayUrl` to `/resource/<StaticResourceName>`. Setting `DisplayUrl` in PCM before resources exist results in a temporarily broken image URL.
- **`ProductUsageGrant` SFDMU silent failure (SFDMU v5 bug)**: SFDMU `Insert` for `ProductUsageGrant` can report "1 records processed, 0 records failed" while the record never persists in the org. This was confirmed on multiple runs — even with all parent lookups resolving correctly (no `MissingParentRecordsReport.csv` entries), the PUG does not appear in the org. **Workaround:** after the rating load, query for the PUG. If missing, insert via Apex:

```bash
# Verify PUG exists
sf data query -q "SELECT Id, Quantity, Status FROM ProductUsageGrant \
  WHERE ProductUsageResource.Product.StockKeepingUnit = '<usage-sku>'" \
  --target-org <alias>

# If missing, insert via Apex (adjust fields for your customer):
sf apex run --target-org <alias> --file scripts/customer-demo/insert_pug_fallback.apex
```

The `activate_rating_records` script (Step 6) will activate the PUG once it exists. If you inserted via Apex after activation already ran, activate the PUG manually: `pug.Status = 'Active'; update pug;`.
- **Grant policy objects silently fail to create via SFDMU**: `UsageGrantRenewalPolicy`, `UsageGrantRolloverPolicy`, and `UsageOveragePolicy` Upserts can log "Inserted 1" while the records never persist. The downstream `ProductUsageGrant` and `ProductUsageResourcePolicy` then fail parent lookups (visible in `MissingParentRecordsReport.csv`). **Fix:** always reference **existing org policies** (e.g. `SF-DEMO-USG-RENEW`, `SF-DEMO-USG-ROLL`, `Default Usage Overage Policy`) instead of creating new ones. If you need a custom policy, create it via Apex or UI before running the SFDMU plan. **Symptom:** `MissingParentRecordsReport.csv` shows `RenewalPolicy.Code`, `RolloverPolicy.Code`, or `UsageOveragePolicy.Name` as missing parents for `ProductUsageGrant` or `ProductUsageResourcePolicy`.
- **Re-running after partial failure**: The PCM Upsert operations are safe to re-run — existing records match on `externalId` and are updated. Objects that failed on the first run will be inserted on the second. However, the flow will also re-run downstream steps (static resources, billing, pricebook), which is harmless but adds time.

## Related paths

- `docs/guides/customer-demo-usage-metered-products.md` — **durable guide** for usage-metered demo products (any customer); example **`SF-*`** data is ephemeral, patterns are not
- `docs/references/customer-template-usage-resource.md` — **UsageResource** field model and tier-1 vs full QB (`ProductUsageResourcePolicy`)
- `datasets/sfdmu/customer-template/en-US/customer-template-pcm/README.md`
- `datasets/sfdmu/customer-template/en-US/customer-template-rating/README.md`
- `datasets/sfdmu/customer-template/en-US/customer-template-rates/README.md`
- `docs/references/customer-template-rate-card-entry.md` — **RateCardEntry** stitches rate card, product, **UsageResource**, selling model, and UOMs; **Base** vs **Tier** (`RateAdjustmentByTier`) and effective dating
- `docs/references/customer-template-tier-rate-card-lessons-learned.md` — **CD-DEMO Tier** + **RABT**, SFDMU order, delete cascade, vs **`PriceAdjustmentTier`**
- `tasks/rlm_customer_demo.py` — pricebook API + `VerifyCustomerDemoCatalog` (`ProductTypeExpected`, `require_product_type`)
