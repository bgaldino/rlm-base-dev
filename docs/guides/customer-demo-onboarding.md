# Customer demo catalog onboarding

Runbook for loading the **customer-template** datasets and avoiding common SFDMU / org pitfalls. Agents should follow **`AGENTS.md` → Customer Demo Product Onboarding UX** for conversational onboarding; this document is the technical reference.

**Cursor:** the project skill **`.cursor/skills/rlm-customer-demo-usage-rates`** (`SKILL.md` + `reference.md`) summarizes load order, **UsageResource** / **ProductUsageResource** / **RateCardEntry** (base vs tiered), activations, and SFDMU cautions for assistants working in this repo.

## Flow and flag

```bash
# Set customer_demo_usage: true in cumulusci.yml project → custom (or org override) to include rating + rates + activations
cci flow run prepare_customer_demo_catalog --org <alias>
```

**Step order (summary):** purge (optional) → PCM → deploy `unpackaged/post_customer_demo/staticresources` → product-images SFDMU → billing SFDMU → `customer_demo_recreate_pricebook_via_api` → `customer_demo_verify_catalog` → (if usage) delete rates → delete rating → insert rating → insert rates → `activate_rating_records` → `activate_rates`.

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

- **PCM** must define **sellable** usage products (`UsageModelType=Pack` updated in rating plan), **usage-definition** `Product2` rows, and **UOM / UOM class** codes referenced by `UsageResource` (template uses `DATAVOL`, `SNFCRED`; keep names aligned across PCM, rating, and rates lookup CSVs).
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

Template list price for usage lines is often **0**; **overage** is illustrated via **`CD-DEMO Base Rate Card`** entries after rates activation.

## Related paths

- `docs/references/customer-template-usage-resource.md` — **UsageResource** field model and tier-1 vs full QB (`ProductUsageResourcePolicy`)
- `datasets/sfdmu/customer-template/en-US/customer-template-pcm/README.md`
- `datasets/sfdmu/customer-template/en-US/customer-template-rating/README.md`
- `datasets/sfdmu/customer-template/en-US/customer-template-rates/README.md`
- `docs/references/customer-template-rate-card-entry.md` — **RateCardEntry** stitches rate card, product, **UsageResource**, selling model, and UOMs; **Base** vs **Tier** (`RateAdjustmentByTier`) and effective dating
- `tasks/rlm_customer_demo.py` — pricebook API + `VerifyCustomerDemoCatalog` (`ProductTypeExpected`, `require_product_type`)
