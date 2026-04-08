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

## Usage and rates prerequisites

- **PCM** must define **sellable** usage products (**`SF-USG-*`**), **usage-definition** `Product2` rows (**`SF-BLNG-*`**), and **UOM / UOM class** codes referenced by `UsageResource` (template uses `DATAVOL`, `SNFCRED`; keep names aligned across PCM, rating, and rates lookup CSVs).
- **`UsageModelType` on sellable usage SKUs (`SF-USG-*`):** the **`customer-template-rating`** and **`customer-template-rates`** plans set **`Anchor`** (same as QuantumBit **`QB-DB`**). **`Pack`** is invalid for this shape: the platform **rejects `ProductUsageResourcePolicy`** (“pack usage model type” error), **PURP** never persists, and quote save can fail with **`PlaceSalesTransactionPersistException`** (e.g. index / persist errors). Do not change **`SF-USG-*`** back to **`Pack`** for tier-1 usage demos.
- **`UsageResource` design:** see **`docs/references/customer-template-usage-resource.md`** — **`Category = Usage`**, **default UOM ∈ UOM class**, **`UsageDefinitionProduct`** (`SF-BLNG-*`), **`UsageResourceBillingPolicy`** (template Upserts **`monthlypeak`** + **`monthlytotal`**; shared policies are **not** deleted by `delete_customer_demo_rating_data`).
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

## Related paths

- `docs/guides/customer-demo-usage-metered-products.md` — **durable guide** for usage-metered demo products (any customer); example **`SF-*`** data is ephemeral, patterns are not
- `docs/references/customer-template-usage-resource.md` — **UsageResource** field model and tier-1 vs full QB (`ProductUsageResourcePolicy`)
- `datasets/sfdmu/customer-template/en-US/customer-template-pcm/README.md`
- `datasets/sfdmu/customer-template/en-US/customer-template-rating/README.md`
- `datasets/sfdmu/customer-template/en-US/customer-template-rates/README.md`
- `docs/references/customer-template-rate-card-entry.md` — **RateCardEntry** stitches rate card, product, **UsageResource**, selling model, and UOMs; **Base** vs **Tier** (`RateAdjustmentByTier`) and effective dating
- `docs/references/customer-template-tier-rate-card-lessons-learned.md` — **CD-DEMO Tier** + **RABT**, SFDMU order, delete cascade, vs **`PriceAdjustmentTier`**
- `tasks/rlm_customer_demo.py` — pricebook API + `VerifyCustomerDemoCatalog` (`ProductTypeExpected`, `require_product_type`)
