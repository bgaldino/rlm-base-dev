# Agent Operating Rules

## Customer Demo Product Onboarding UX

When a user asks to set up products for a customer demonstration:

1. Treat this as onboarding intent.
2. Ask for **either**:
   - a company description, or
   - a company website URL.
3. Ask for additional context when available (services, pricing model, recurring vs one-time offers, add-ons, known SKUs, billing expectations, and product image preferences/URLs). If product images are requested, ask for a preferred customer logo URL and confirm it can be used.
4. Research the customer inputs and propose a product vision:
   - categories/families,
   - 10-15 SKU set,
   - selling model assumptions (prefer term-defined subscriptions over evergreen for recurring offers),
   - bundle assumptions (parent bundles, component groups, required vs optional components),
   - initial Product2 typing assumptions (which SKUs are `Type=Bundle` vs `Type` blank/null),
   - attribute/configuration assumptions (definitions, picklists, product attribute behavior),
   - relationship assumptions (relationship types, related components, qualification/disqualification rules when needed),
   - pricing assumptions,
   - billing assumptions (for example payment term and billing policy intent),
   - image coverage assumptions (which SKUs require product images).
5. Ask the user to confirm the vision before creating or deploying records.
6. After confirmation, use repo assets:
   - **Dataset templates** (paths under `datasets/sfdmu/customer-template/en-US/`):
     - `customer-template-pcm` — products, catalog, bundles, **and (for usage demos) `UnitOfMeasureClass` / `UnitOfMeasure`** rows referenced by `UsageResource` (template codes include `DATAVOL` + `SNFCRED`; keep codes aligned if you rename)
     - `customer-template-product-images` — `Product2.DisplayUrl` by SKU (typically `/resource/<StaticResourceApiName>` after deploy)
     - `customer-template-billing` — legal entity, billing policy/treatment, `Product2` billing assignment
     - **Optional usage + rates:** `customer-template-rating` + `customer-template-rates` — enable with `customer_demo_usage: true` (project `custom`) **or** run `prepare_customer_demo_usage` **after** catalog steps through pricebook + verify (products must already exist). **`UsageResource`** binds **Category=Usage**, **UnitOfMeasureClass**, **DefaultUnitOfMeasure** (unit must belong to the class), **UsageDefinitionProduct** (`SF-BLNG-*`), and **UsageResourceBillingPolicy** (`monthlypeak` / `monthlytotal` in template). Full model: **`docs/references/customer-template-usage-resource.md`**. Rating also loads **`ProductUsageResource`**; rates need active PUR/UR after **`activate_rating_records`**, then **`activate_rates`**. **RateCardEntry** stitching (base vs tiered, effective dates): **`docs/references/customer-template-rate-card-entry.md`**.
   - **Order of operations (`prepare_customer_demo_catalog`):** (1) optional Apex purge `customer_demo_purge_records`, (2) `insert_customer_demo_pcm_data`, (3) `deploy_customer_demo_staticresources`, (4) `insert_customer_demo_product_images_data`, (5) `insert_customer_demo_billing_data`, (6) `customer_demo_recreate_pricebook_via_api` (`scripts/customer-demo/customer-pricebook-entries.csv`), (7) `customer_demo_verify_catalog`, (8–13) **if `customer_demo_usage`:** `delete_customer_demo_rates_data` → `delete_customer_demo_rating_data` → `insert_customer_demo_rating_data` (two-pass object set; activates `UsageResource` in pass 2) → `insert_customer_demo_rates_data` → `activate_rating_records` → `activate_rates`. Never load rating before PCM has created the SKUs and UoM rows the plan references.
   - Model customer-specific PCM using `datasets/sfdmu/qb/en-US/qb-pcm` as the reference shape for advanced objects (attributes, classifications, bundles, related components, ramp/proration, qualifications).
   - Before import/deploy, validate that all `ProductSellingModel.Name` + `SellingModelType` values used in customer CSVs **and** in `customer-pricebook-entries.csv` exist in the target org; align `ProductSellingModelOption` **ProrationPolicy.Name** (template defaults to **`Default Proration Policy`**) with the org or change the CSV.
   - Default recurring offers to term-based models (for example `TermDefined` monthly/annual) so proration and cancel/replace/amend can be demonstrated; use evergreen only when the org lacks usable term models and call out that trade-off.
   - Decide `Product2.Type` before first insert for each SKU; treat it as effectively immutable in onboarding runs. **Many RLM orgs restrict `Product2.Type` to `Base`, `Bundle`, and `Set` only** — in customer-template flows the convention is: **`Type=Bundle` only for parent bundle SKUs; leave `Type` blank (null) for everything else** (do not use `Base` or `Set` for that template unless the org requires it). `scripts/customer-demo/customer-pricebook-entries.csv` can include **`ProductTypeExpected`**: `Bundle` for bundle SKUs, empty for all others — `customer_demo_verify_catalog` then enforces Bundle vs blank per row instead of “any non-null type”.
     - For any SKU with `Type=Bundle`, set `Product2.ConfigureDuringSale=Allowed` in the initial PCM row
     - Bundle **child** products must still satisfy org rules (some orgs reject certain types as bundle components)
   - **Logo:** run `prepare_customer_demo_logo_staticresource` (URL) **or** add files under `unpackaged/post_customer_demo/staticresources/`; deploy via `deploy_customer_demo_staticresources` **before** the product-images SFDMU step so `DisplayUrl` resolves.
   - **Product2 + SFDMU (failure mode we hit in the wild):** the PCM `Product2` query includes **`BasedOnId` / `UnitOfMeasureId` / `QuantityUnitOfMeasure`**. CSVs that only list a short set of columns can cause SFDMU to emit **invalid parent keys** (`ID000…` placeholders) in **`customer-template-pcm/reports/MissingParentRecordsReport.csv`**. The job may still log Product2 “processed” rows while **products never become queryable by SKU**, and **`customer_demo_recreate_pricebook_via_api`** then errors with **Missing Product2 records**. **Fix:** mirror **`datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv`** headers and fill **`BasedOn.Code`** (empty), **`CanRamp=false`**, **`IsSoldOnlyWithOtherProds=false`**, **`QuantityUnitOfMeasure` + `UnitOfMeasure.UnitCode`** (commonly **`EACH`** — confirm that UOM exists in the target org). After a load, spot-check: `sf data query` on a few SKUs from `customer-pricebook-entries.csv`.
   - **Human / reviewer runbook:** `docs/guides/customer-demo-onboarding.md` (flow, Product2 shape, troubleshooting, quote-testing SKUs).
   - **Quote / CPQ testing (usage demos):** user-facing usage lines are the **Pack** products (e.g. **`SF-USG-STORAGE`**, **`SF-USG-EGRESS`**, **`SF-USG-COMPUTE`**). Do **not** tell testers to add **`SF-BLNG-*`** usage-definition-only products to a quote for normal metering demos.
   - Primary flow: `prepare_customer_demo_catalog`; verification: `customer_demo_verify_catalog`.
7. Do not run deployment/import steps without explicit user approval.
