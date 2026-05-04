# Customer demo catalog onboarding

Runbook for loading the **customer-template** datasets and avoiding common SFDMU / org pitfalls. Agents should follow **`AGENTS.md` → Customer Demo Product Onboarding UX** for conversational onboarding; this document is the technical reference.

**Ephemeral vs durable:** The concrete **Snowflake-style `SF-*` SKUs**, logos, and rate-card names in `datasets/sfdmu/customer-template/` can be **replaced or purged** when switching to another customer or practice. **`docs/guides/customer-demo-usage-metered-products.md`** captures **transferable** rules for **any** usage-metered demo ( **`UsageModelType`**, SFDMU **Name** columns, PURP/PUG, QLIURG, quotes); **`qb-rating`** remains the **canonical product-shape reference**.

**Cursor:** the project skill **`.cursor/skills/rlm-customer-demo-usage-rates`** (`SKILL.md` + `reference.md`) summarizes load order, **UsageResource** / **ProductUsageResource** / **RateCardEntry** (**CD-DEMO Base** flat **`Rate`** vs **CD-DEMO Tier** + **`RateAdjustmentByTier`**), **`delete_customer_demo_rates_data`** scope (**Base + Tier** + cascade **RABT**), activations, and SFDMU cautions. **`SKILL.md` → “Field-tested findings”** and **`reference.md` → “Findings and triage”** capture lessons from real deploys (RCE **ProductSellingModel** = Standard PBE on **all** RCE rows, **RABT** vs **`PriceAdjustmentTier`**, **UsageResource** UOM **Name** columns for v5, pricebook API upsert / quotes / FLS, CCI **`--org`** on **`activate_*`** tasks). Tier-specific consolidation: **`docs/references/customer-template-tier-rate-card-lessons-learned.md`**.

## Flow and flag

```bash
# Set customer_demo_usage: true in cumulusci.yml project → custom (or org override) to include rating + rates + activations
cci flow run prepare_customer_demo_catalog --org <alias>
```

**Step order (summary):**

| Step | Task | Notes |
|---|---|---|
| 1 | `customer_demo_purge_records` | Clears QLIURG / OrderItemUsageRsrcGrant blocks on SF-UR-* so rating delete can run |
| 2 | `insert_customer_demo_pcm_data` | Products, classifications, attributes, bundles, catalog |
| 3 | `deploy_customer_demo_staticresources` | Logos; must precede product-images |
| 4 | `deploy_customer_demo_branding` | Conditional (`customer_demo_branding: true`) |
| 5 | `insert_customer_demo_product_images_data` | Sets `Product2.DisplayUrl` |
| 6 | `insert_customer_demo_billing_data` | Billing policy, treatment, product assignment |
| 6b | `activate_customer_demo_billing` | Activate BillingTreatmentItem → BillingTreatment → BillingPolicy in order (platform requires Draft on create) |
| 7 | `customer_demo_recreate_pricebook_via_api` | Standard PBE with explicit `ProductSellingModelId` |
| 8 | `delete_customer_demo_pricing_data` | Apex-scoped delete of customer-prefix ABR+ABA (ABR cascade-deletes AAC) |
| 9 | `insert_customer_demo_pricing_data` | **Phase 1**: SFDMU — `AttributeBasedAdjRule` Upsert only |
| 9b | `insert_customer_demo_pricing_adjustments` | **Phase 2**: Apex — `AttributeAdjustmentCondition` + `AttributeBasedAdjustment` Insert (idempotent) |
| 10 | `customer_demo_verify_catalog` | Go/no-go: images, billing, PSM, PBE, category, ABA count |
| 11–16 | Usage steps | Conditional (`customer_demo_usage: true`) — rates delete → rating delete → rating → rates → activate_rating_records → activate_rates |

**Why pricing (steps 8–9b) runs after pricebook (step 7):** `AttributeBasedAdjustment` has no FK to `PricebookEntry`, so it could load earlier. Placement after pricebook recreation keeps logical flow — list prices first, adjustments second. The platform resolves ABA at quote time through `PriceAdjustmentSchedule`, not a stored PBE FK.

**Why AAC/ABA use Apex (step 9b) instead of SFDMU:** SFDMU resolves FK columns in `Insert` operations using the parent object's SOURCE collection. For `Readonly` parents, SFDMU stores fetched IDs in the TARGET collection — not SOURCE — so FK resolution silently filters all child rows (SOURCE count: 0) even when the parent records exist in the org and the CSVs are populated. This applies regardless of whether AAC/ABA share an objectSet with ABR or run as a separate SFDMU task. Apex resolves all FKs explicitly via SOQL and is unaffected by this limitation. See `customer-template-pricing/README.md` → Lesson 7.

**Why delete runs before insert (step 8):** AAC and ABA use Insert (not Upsert) because their externalIds are all-relationship-traversal (SFDMU Bug 3 would cause Upsert to always insert, creating duplicates). The Apex insert script is idempotent (skips if records already exist), but running the delete first keeps re-runs clean. The delete is an Apex script (not `DeleteSFDMUData`) so it is scoped to the customer prefix (e.g. `OAI-%`, `BULLS-%`) and does not affect QB pricing data in the same org.

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

## Attribute-based pricing

The `customer-template-pricing` plan loads **attribute-driven Percentage adjustments** on configurable products via the RLM three-object chain:

```
AttributeBasedAdjRule → AttributeAdjustmentCondition → AttributeBasedAdjustment
```

A price-impacting attribute (e.g. `OAI-MODEL-TIER` for API tier, `BULLS-SEAT-SECTION` for seat location) is defined with `IsPriceImpacting=true` on `ProductAttributeDefinition`. When a rep configures the attribute on the quote, the platform evaluates matching `AttributeBasedAdjRule` records and applies the corresponding adjustment.

**Extending:** add rows to `AttributeBasedAdjRule.csv`, `AttributeAdjustmentCondition.csv`, and `AttributeBasedAdjustment.csv` for additional rules, then update `scripts/apex/insertCustomerDemoPricingAdjustments.apex` to match. Update `ExpectedPricingRules` in `customer-pricebook-entries.csv`. See `customer-template-pricing/README.md` for full details.

**Verification:** `customer_demo_verify_catalog` checks `ExpectedPricingRules` per SKU.

```bash
# Verify pricing records manually (adjust LIKE scope to customer prefix)
sf data query -q "SELECT AttributeBasedAdjRule.Name, AdjustmentType, AdjustmentValue, Product.StockKeepingUnit FROM AttributeBasedAdjustment WHERE AttributeBasedAdjRule.Name LIKE 'OAI-%' ORDER BY AttributeBasedAdjRule.Name" --target-org <username>
```

### Attribute-based pricing — critical SFDMU v5 pitfalls

**Pitfall 1 — Two-objectSet architecture is required when ABR is freshly inserted**

SFDMU builds its parent FK lookup map during STAGE 2 (before the UPDATE/insert phase). If `AttributeBasedAdjRule` records were deleted before the run, the STAGE 2 query returns 0 ABR records → the FK map for ABR is empty → `AttributeBasedAdjustment` insert crashes with `COMMAND_UNEXPECTED_ERROR` (SFDMU internal null pointer) because it cannot resolve `AttributeBasedAdjRuleId`.

The nominal fix is two `objectSets`: Set 1 Upserts ABR only; Set 2 lists ABR as `Readonly` so SFDMU re-queries the org after Set 1 completes. **However, see Pitfall 5 below — even the two-objectSet / two-task approach fails for AAC/ABA inserts in SFDMU.**

**Pitfall 2 — SELECT queries must use direct ID fields, not relationship-traversal**

SFDMU v5 generates a warning when relationship-traversal fields (e.g. `AttributeBasedAdjRule.Name`) appear in the SELECT query: `Referenced field removed from the script query`. It then removes those fields from its internal FK resolution context for the INSERT phase, causing a crash.

Use direct ID fields in the SELECT — exactly as QB's export.json does:
```sql
-- CORRECT
SELECT AttributeBasedAdjRuleId, AttributeDefinitionId, ProductId, ... FROM AttributeAdjustmentCondition
-- WRONG (triggers SFDMU crash)
SELECT AttributeBasedAdjRule.Name, AttributeDefinition.Code, Product.StockKeepingUnit, ... FROM AttributeAdjustmentCondition
```

**Pitfall 3 — AAC CSV column count: 5 empty fields require 6 commas**

`AttributeAdjustmentCondition` has 11 CSV columns. Columns 4–8 (BooleanValue through IntegerValue) are all empty for string-value conditions. Missing one comma silently shifts `equals` into `IntegerValue`, making all rows unresolvable (SFDMU reads 0 source records). Validate with Python before loading:

```python
import csv
with open('AttributeAdjustmentCondition.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        assert row['Operator'] == 'equals', f"Misaligned: Operator={row['Operator']!r}"
```

**Pitfall 4 — `AttributeAdjustmentCondition` cannot be deleted via direct DML**

`AttributeAdjustmentCondition` is a master-detail child of `AttributeBasedAdjRule`. `delete [SELECT Id FROM AttributeAdjustmentCondition WHERE ...]` fails with `DML operation Delete not allowed`. Deletion is cascade-only — deleting `AttributeBasedAdjRule` automatically cascades to AAC. Delete `AttributeBasedAdjustment` (which IS directly deletable) first, then ABR.

**Pitfall 5 — SFDMU cannot load AAC/ABA inserts regardless of objectSet architecture or task sequencing**

**Root cause:** For `Insert` operations, SFDMU resolves FK columns (e.g. `AttributeBasedAdjRule.Name` → `AttributeBasedAdjRuleId`) using the parent object's **SOURCE** ID collection. For `Readonly` parent objects, SFDMU fetches IDs from the TARGET org and stores them in the **TARGET** collection — not SOURCE. FK resolution for child objects uses SOURCE, so the mapping is always empty. All child rows are silently filtered (reported SOURCE count: 0) even when:
- ABR records exist in the org
- ABR is listed as `Readonly` in the same objectSet as AAC/ABA
- ABR SFDMU upsert ran as a completely separate CCI task beforehand
- The `Readonly` CSVs are populated with actual data rows

**Symptom:** `{AttributeAdjustmentCondition} The total amount of the retrieved records from SOURCE by 1 queries: 0.` — despite the CSV having data rows and the `_source.csv` internal file showing those rows were read.

**Fix (authoritative):** Use **Apex** for all AAC and ABA inserts. Apex resolves all FKs via SOQL explicitly and is unaffected by SFDMU's SOURCE/TARGET collection distinction. This is why step 9b uses `AnonymousApexTask` with `scripts/apex/insertCustomerDemoPricingAdjustments.apex` rather than SFDMU.

**Pitfall 6 — ABA read-only fields cause Apex compile error**

`AttributeBasedAdjustment` has several platform-computed read-only fields: `AttributeAdjConditionsHash`, `AttributeCount`, `PricingTerm`, `PricingTermUnit`, `ScheduleType`, `SellingModelType`. Including any of these in an Apex SObject constructor causes a compile error (`Field is not writeable`). Omit them — the platform populates them automatically on insert.

**Pitfall 7 — `AttributeAdjustmentCondition.Operator` picklist uses `equals`, not `=`**

The `Operator` field is a restricted picklist. The value is `equals` (the word), not `=` (the symbol). Using `=` causes `INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST` at INSERT time from both Apex and SFDMU. Query the org to confirm: `SELECT Operator FROM AttributeAdjustmentCondition LIMIT 1`.

## Troubleshooting

- **`BillingPolicy has an invalid status` on order save:** The billing stack (BillingTreatmentItem, BillingTreatment, BillingPolicy) is loaded as `Draft` — the platform rejects `Status=Active` on create. Step 6b (`activate_customer_demo_billing`) activates them in dependency order after load. If you see this error, run: `cci task run activate_customer_demo_billing --org <alias>`. Also note: `BillingTreatmentItem.CurrencyIsoCode` is **read-only** (platform derives it); including it in the SFDMU SELECT causes a silent insert failure for the entire BTI record.
- **Deleting an Active billing stack silently fails without deactivation:** `deleteCustomerDemoCatalogData.apex` uses `Database.delete(..., false)` (allOrNone=false). If `BillingPolicy`, `BillingTreatment`, or `BillingTreatmentItem` are `Active`, the platform blocks the delete and the error is swallowed — records remain in the org with no indication of failure. The delete script now deactivates in reverse order first (Policy → Draft + clear `DefaultBillingTreatmentId`, Treatment → Draft, TreatmentItem → Draft) before deleting. If you run into stuck billing records after a catalog delete, set each to Draft manually and re-run the delete task.
- **`prepare_customer_demo_branding` logo download blocked (403/timeout):** The `--logo-url` option downloads the image directly from the URL. Corporate or CDN URLs often block server-side requests (403 Forbidden). **Fix:** download the logo manually, then use `--logo-path /path/to/logo.png` instead of `--logo-url`. Any image format works — the script auto-resizes to 600×120 PNG for the brand asset and accepts a second `--bg-color` for letterboxing. If no logo is available, generate a placeholder with Pillow: `python3 -c "from PIL import Image, ImageDraw, ImageFont; img=Image.new('RGB',(600,120),(0,0,0)); d=ImageDraw.Draw(img); d.text((50,40),'CompanyName',fill='white'); img.save('/tmp/logo.png')"`.
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
- **Silent Product2 insert failures — always check for unquoted commas in CSV fields**: If some Product2 records load and others silently fail (SFDMU reports "processed" but the record is absent from the org), compare which SKUs failed against their `Description` values. Any CSV field containing a comma **must** be wrapped in double-quotes (`"value, with comma"`). Without quoting, SFDMU misparsed the row and all subsequent column values shift — the platform rejects the INSERT but SFDMU still logs it as processed. Run `python3 -c "import csv,os; [print(f'{f} row {i}') for f in os.listdir('.') if f.endswith('.csv') for i,r in enumerate(list(csv.reader(open(f)))[1:],2) if len(r)!=len(list(csv.reader(open(f)))[0])]"` (or the project CSV validator) to detect mismatches before loading.
- **`AttributePicklist` silent insert failure — DataType must be Text**: If `AttributePicklist` records fail to appear in the org despite SFDMU reporting success, check that `DataType` is `Text` (or `Number`) — **not** `Picklist`. `Picklist` is not a valid value for the container object's DataType field. This cascades to `AttributePicklistValue`, `AttributeDefinition`, `AttributeCategoryAttribute`, and `ProductAttributeDefinition` all failing with missing-parent lookups.
- **`ProductCatalog` silent insert failure — CatalogType must be Sales**: `CatalogType=Standard` is not a valid picklist value. Use `Sales` (matching the qb-pcm reference). If the catalog record fails to create, all `ProductCategory` and `ProductCategoryProduct` records fail with missing-parent lookups.
- **`BillingPolicy` / `BillingTreatment` / `BillingTreatmentItem` silent insert failure — Status must be Draft**: Creating these objects with `Status=Active` is rejected by the platform. SFDMU still logs "Totally processed 1 records" but the record never appears in the org. Set `Status=Draft` in all three CSVs. A failed BillingPolicy INSERT leaves SFDMU's lookup cache empty, so the downstream `Product2` Update step sees "Same data: N" (null matches null) — a misleading success log that masks the root failure. After fixing, the billing load updates all 13 Product2 records with the correct `BillingPolicyId` in one pass.
- **`customer_demo_verify_catalog` crashes with `NoneType.get` — Salesforce returns null relationships as None, not absent keys**: When `Product2.BillingPolicyId` is null, the Salesforce REST API returns `{"BillingPolicy": null}` — the key is present but the value is `None`. `dict.get("BillingPolicy", {})` does not apply the default when the key exists with a `None` value, so `.get("Name")` then fails. Use `(record.get("BillingPolicy") or {}).get("Name")` for any relationship field that may be null. This is fixed in `tasks/rlm_customer_demo.py`.

## Related paths

- `docs/guides/customer-demo-usage-metered-products.md` — **durable guide** for usage-metered demo products (any customer); example **`SF-*`** data is ephemeral, patterns are not
- `docs/references/customer-template-usage-resource.md` — **UsageResource** field model and tier-1 vs full QB (`ProductUsageResourcePolicy`)
- `datasets/sfdmu/customer-template/en-US/customer-template-pcm/README.md`
- `datasets/sfdmu/customer-template/en-US/customer-template-pricing/README.md` — attribute-based pricing plan; SFDMU pitfalls (two-objectSet, direct ID fields, AAC column count, AAC cascade-delete)
- `datasets/sfdmu/customer-template/en-US/customer-template-rating/README.md`
- `datasets/sfdmu/customer-template/en-US/customer-template-rates/README.md`
- `docs/references/customer-template-rate-card-entry.md` — **RateCardEntry** stitches rate card, product, **UsageResource**, selling model, and UOMs; **Base** vs **Tier** (`RateAdjustmentByTier`) and effective dating
- `docs/references/customer-template-tier-rate-card-lessons-learned.md` — **CD-DEMO Tier** + **RABT**, SFDMU order, delete cascade, vs **`PriceAdjustmentTier`**
- `tasks/rlm_customer_demo.py` — pricebook API + `VerifyCustomerDemoCatalog` (`ProductTypeExpected`, `require_product_type`, `ExpectedPricingRules`)
