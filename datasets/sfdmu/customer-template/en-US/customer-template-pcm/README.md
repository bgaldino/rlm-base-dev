# customer-template-pcm Data Plan

Template SFDMU plan for onboarding customer-specific demo products.

## Scope

This template intentionally includes only the baseline records needed by the onboarding runbook:

1. `ProductSellingModel`
2. `Product2` (including `Type` or org-specific product type field)
3. `ProductSellingModelOption` (`IsDefault=true`)
4. `ProductCatalog` and `ProductCategory`
5. `ProductCategoryProduct`

Pricebook rows are intentionally excluded from this plan. Use API-based creation with explicit `ProductSellingModelId`.

## How to use

1. Copy this directory to a customer plan path, for example:
   - `datasets/sfdmu/acme/en-US/acme-pcm`
2. Populate CSV rows from your customer SKU matrix.
3. Wire `cumulusci.yml` anchors/tasks for the new customer plan.
4. Run the dedicated customer onboarding flow.
