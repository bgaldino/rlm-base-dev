# customer-template-pcm Data Plan

Template SFDMU plan for onboarding customer-specific demo products.

## Scope

This template includes both baseline and advanced customer-specific PCM records needed for realistic demos:

1. Core products and selling models:
   - `ProductSellingModel`
   - `Product2` (including `Type`, `ConfigureDuringSale`, or org-specific product type/config fields)
   - `ProductSellingModelOption` (`IsDefault=true`)
   - `ProrationPolicy` and `ProductRampSegment` (when recurring/ramp behavior is needed)
2. Catalog and categorization:
   - `ProductCatalog`
   - `ProductCategory`
   - `ProductCategoryProduct`
   - `ProductCategoryQualification` / `ProductCategoryDisqual` (optional eligibility scaffolding)
3. Attribute framework (for configurable products):
   - `AttributePicklist` / `AttributePicklistValue`
   - `UnitOfMeasureClass` / `UnitOfMeasure`
   - `AttributeDefinition`
   - `AttributeCategory` / `AttributeCategoryAttribute`
   - `ProductClassification` / `ProductClassificationAttr`
   - `ProductAttributeDefinition`
   - `ProdtAttrScope`
4. Bundle structure and component relationships:
   - `ProductRelationshipType`
   - `ProductComponentGroup`
   - `ProductRelatedComponent`
   - `ProductQualification` / `ProductDisqualification` (optional product-level eligibility scaffolding)

Pricebook rows are intentionally excluded from this plan. Use API-based creation with explicit `ProductSellingModelId`.

This template is part of a hybrid customer onboarding set:

- `customer-template-pcm` (this folder): product/catalog foundation
- `customer-template-product-images`: `Product2.DisplayUrl` updates by SKU
- `customer-template-billing`: lightweight billing foundation + product billing assignment

## How to use

1. Copy this directory to a customer plan path, for example:
   - `datasets/sfdmu/acme/en-US/acme-pcm`
2. Populate CSV rows from your customer SKU matrix.
3. **`Product2.csv` and SFDMU:** the plan’s `Product2` SOQL includes **`BasedOnId`**, **`UnitOfMeasureId`**, and **`QuantityUnitOfMeasure`**. Omitting the relationship columns SFDMU resolves from CSV can produce **bad lookups** (see **`reports/MissingParentRecordsReport.csv`**) and **missing SKUs in the org** even when the log shows Product2 activity. **Copy the column layout from `datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv`** (e.g. empty **`BasedOn.Code`**, **`CanRamp=false`**, **`IsSoldOnlyWithOtherProds=false`**, **`QuantityUnitOfMeasure` / `UnitOfMeasure.UnitCode`** such as **`EACH`** when the org has that unit). See **`docs/guides/customer-demo-onboarding.md`**.
4. When bundles/configuration are in scope, populate component groups, related components, and attribute CSVs in the same pass as products.
   - Decide `Product2.Type` before first insert:
     - parent bundle products: `Type=Bundle` (and `ConfigureDuringSale=Allowed`)
     - all other products in this template: **`Type` blank/null** (many orgs allow only `Base`/`Bundle`/`Set`; null avoids picking the wrong one)
   - for any product with `Type=Bundle`, set `ConfigureDuringSale=Allowed` on initial insert
   - avoid setting bundle children to `Base`/`Set` in orgs that enforce child-type restrictions
5. Ensure `ProductSellingModel.Name` values used in `ProductSellingModelOption` and pricebook seed input exactly match selling models available in the target org.
   - Prefer term-based recurring models (`SellingModelType=TermDefined`) so demo flows can show proration and cancel/replace/amend behavior.
   - Use evergreen recurring models only when no suitable term model exists in the target org.
   - Default `ProductSellingModelOption` rows reference **`Default Proration Policy`** by name — ensure that proration policy exists in the target org (typical after RLM base setup), or change the CSV to an org-native policy name.
6. **Unit of measure for usage demos:** add **`UnitOfMeasureClass`** / **`UnitOfMeasure`** rows for each consumption family you meter (e.g. data volume + a dedicated credit unit), with **`Type = Usage`** on the class where required so they pair with **`UsageResource.Category = Usage`**. Set **`BaseUnitOfMeasure`** and **`DefaultUnitOfMeasure`** on the class; each **`UsageResource.DefaultUnitOfMeasure`** must be a **`UnitOfMeasure`** under that class. See **`docs/references/customer-template-usage-resource.md`**. Keep **`Code` / `UnitCode` / `Name`** aligned across PCM, rating, and rates lookup CSVs.
7. Wire `cumulusci.yml` anchors/tasks for the new customer plan.
8. Run the dedicated customer onboarding flow.

## Known pitfalls (from real customer onboardings)

### AttributePicklistValue — Code must be globally unique

`AttributePicklistValue.Code` is the **externalId** used for Upsert matching across **all** picklists in the org. If two values share the same `Code` (even in different picklists), the second one overwrites the first. This causes a cascade failure: `AttributeDefinition`, `AttributeCategoryAttribute`, `ProductClassificationAttr`, and `ProductAttributeDefinition` all lose their parent references and fail to load, potentially aborting the entire PCM job.

**Example:** A "Service Tier" picklist and a "Property Size" picklist both used `Code = Enterprise`. Fix: rename the property-size entry to `Code = XLarge`.

### AttributeDefinition — DeveloperName must be org-unique

`DeveloperName` on `AttributeDefinition` is unique across the org. Packages, prior demos, or RLM base setup may already define names like `Service_Tier` or `Property_Size`. If a collision occurs, the insert fails silently within the SFDMU batch, and downstream objects referencing that definition cascade-fail.

**Fix:** prefix customer-specific developer names (e.g. `RK_Service_Tier`, `RK_Property_Size`).

### Product images — static resources must deploy first

`Product2.DisplayUrl` resolves to `/resource/<StaticResourceName>`. If set in the PCM `Product2.csv` before static resources exist in the org, the URL is broken until resources deploy. The intended flow order handles this:
1. Step 2: PCM load (leave `DisplayUrl` empty in `Product2.csv`)
2. Step 3: `deploy_customer_demo_staticresources` (deploys `.resource` + `-meta.xml` files)
3. Step 5: `customer-template-product-images` SFDMU step (sets `DisplayUrl` on each product)

### UnitOfMeasure updates on re-run are benign

When UOMs like `USD` or `EACH` already exist in the org (from `qb-pcm` or base setup), the Upsert Update phase may log errors because fields like `ConversionFactor` or `Type` are not updatable after creation. These errors are **benign** — the existing UOM is correct. Only truly new UOMs (e.g. a customer-specific `EVENT` unit) need the Insert to succeed.

### CategoryCode in customer-pricebook-entries.csv

`customer_demo_verify_catalog` uses the `CategoryCode` column in `scripts/customer-demo/customer-pricebook-entries.csv` to verify that `ProductCategoryProduct` records exist for each SKU. Leaving `CategoryCode` empty causes the verify step to report **"ProductCategoryProduct missing for category"** on every SKU, even when all catalog objects loaded correctly. Always populate `CategoryCode` with the matching `ProductCategory.Code`.

### Rating grant policies — reference existing org records, don't create new ones

`UsageGrantRenewalPolicy`, `UsageGrantRolloverPolicy`, and `UsageOveragePolicy` are setup-like objects that SFDMU silently fails to create — the REST API Insert logs "processed 1" but the records never persist in the org. Downstream `ProductUsageGrant` and `ProductUsageResourcePolicy` then fail parent lookups. **Always reference policies that already exist in the org** (e.g. `SF-DEMO-USG-RENEW`, `SF-DEMO-USG-ROLL`, `Default Usage Overage Policy`). Query the org before populating the rating CSVs. See `customer-template-rating/README.md` for full details.

### ProductUsageGrant — always verify after load

SFDMU's `Insert` for `ProductUsageGrant` has a confirmed silent-failure bug: it reports success but the record never appears in the org. After every rating load, verify PUG existence via SOQL. If missing, insert via Apex. See `docs/guides/customer-demo-onboarding.md` → Troubleshooting.
