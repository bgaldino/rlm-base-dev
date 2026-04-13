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
6. **Unit of measure for usage demos:** this template’s `UnitOfMeasureClass.csv` / `UnitOfMeasure.csv` seed **`DATAVOL`** (GB, TB) and **`SNFCRED`** (CRD) with **`Type = Usage`** on the class so they pair with **`UsageResource.Category = Usage`**. Set **`BaseUnitOfMeasure`** and **`DefaultUnitOfMeasure`** on the class; each **`UsageResource.DefaultUnitOfMeasure`** (e.g. TB, GB, CRD) must be a **`UnitOfMeasure`** row under that class. See **`docs/references/customer-template-usage-resource.md`**. If your org already defines the same `Code` values differently, reconcile before loading or adjust codes consistently across PCM + rating + rates lookup CSVs.
7. Wire `cumulusci.yml` anchors/tasks for the new customer plan.
8. Run the dedicated customer onboarding flow.
