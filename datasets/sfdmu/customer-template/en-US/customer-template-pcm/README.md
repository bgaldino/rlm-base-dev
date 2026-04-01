# customer-template-pcm Data Plan

Template SFDMU plan for onboarding customer-specific demo products.

## Scope

This template includes both baseline and advanced customer-specific PCM records needed for realistic demos:

1. Core products and selling models:
   - `ProductSellingModel`
   - `Product2` (including `Type` or org-specific product type field)
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
3. When bundles/configuration are in scope, populate component groups, related components, and attribute CSVs in the same pass as products.
4. Ensure `ProductSellingModel.Name` values used in `ProductSellingModelOption` and pricebook seed input exactly match selling models available in the target org.
5. Wire `cumulusci.yml` anchors/tasks for the new customer plan.
6. Run the dedicated customer onboarding flow.
