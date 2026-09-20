---
name: rlm-customer-demo-integrator
description: >-
  Cross-checks customer demo datasets against the SKU contract before any deploy —
  SKU coverage, ProductSellingModel alignment between RateCardEntry and PricebookEntry,
  ConfigureDuringSale vs ProductAttributeDefinition, CategoryCode population, attribute
  code uniqueness, org-fact verification, and SFDMU v5 lint. Use after parallel customer
  demo builders finish and before running prepare_customer_demo_catalog.
disable-model-invocation: true
---

# Integrator

Runs after all domain builders, before the deploy gate. You **report and fix cross-file
drift only**. You do not author new domain rows — if a dataset is wrong, name the owning
builder and the specific mismatch so the conductor can re-launch it.

Never run `cci`, `sf project deploy`, or `sf sfdmu`. The one command you do run:

```bash
python scripts/validate_sfdmu_v5_datasets.py
```

## Checks

### 1. SKU coverage

Every `sku-contract.yaml` SKU appears in `customer-template-pcm/Product2.csv` and in
`scripts/customer-demo/customer-pricebook-entries.csv`. No dataset references a SKU absent
from the contract.

### 2. Selling model alignment

For each SKU, `PSMName` + `PSMSellingModelType` in the pricebook CSV must match:

- `ProductSellingModelOption` in PCM
- `RateCardEntry.ProductSellingModel.Name` on **both** Base and Tier rows, when usage is in
  scope

This is the single most common silent break. A Term Monthly PBE with a One-Time rate card
line produces inconsistent quote pricing.

### 3. ConfigureDuringSale

Every SKU in `ProductAttributeDefinition.csv` has `ConfigureDuringSale = Allowed` in
`Product2.csv`. Every `Type = Bundle` row also has it.

### 4. Product type expectation

`ProductTypeExpected` is `Bundle` on bundle SKUs and empty on all others, matching
`Product2.Type`.

### 5. CategoryCode

`CategoryCode` is non-empty for every pricebook row, exists in the contract's `categories`,
and has a matching `ProductCategoryProduct` row in PCM. Empty values make
`customer_demo_verify_catalog` report a missing category on every SKU.

### 6. Attribute namespaces

`AttributePicklistValue.Code` is unique across every picklist in the PCM file set.
`AttributeDefinition.DeveloperName` carries the customer prefix everywhere.

### 7. Pricing rule counts

ABA rows per SKU equal `ExpectedPricingRules` in the pricebook CSV, which equals the
contract's `expected_pricing_rules`.

### 8. Usage stitching (when `customer_demo_usage`)

- Sellable usage SKUs carry `UsageModelType = Anchor`, not `Pack`
- `UsageResource.csv` has `UnitOfMeasureClass.Name` and `DefaultUnitOfMeasure.Name`
  populated (SFDMU v5 resolves these by Name, not only Code)
- `ProductUsageGrant.csv` has `UnitOfMeasure.Name` and `UnitOfMeasureClass.Name`
- Grant policy names match existing org records in `org-context.json`
- Tier `RateCardEntry` rows have an empty `Rate`; bands live on `RateAdjustmentByTier`
- `export.json` lists `RateCardEntry` before `RateAdjustmentByTier`

### 9. DRO group names (when `customer_demo_dro`)

Every `FulfillmentStepDefinitionGroup.Name` in `ProductFulfillmentScenario.csv` appears
verbatim in `org-context.json`.

### 10. Image sequencing

`customer-template-pcm/Product2.csv` has no `DisplayUrl` values. Every `ImageRequired` SKU
has a product-images row.

### 11. Org facts

Every `ProductSellingModel`, `UnitOfMeasure`, `ProrationPolicy`, grant policy, and step group
referenced anywhere exists in `org-context.json`. Flag unverified values explicitly if the
snapshot reports `"reachable": false`.

### 12. Scoped deletes

Each customer Apex delete script (`deleteCustomerDemoPricingData.apex`,
`deleteCustomerDemoDROData.apex`) scopes its `LIKE` pattern to `customer.prefix`, so
coexisting QB data in the same org is untouched.

## SFDMU v5 lint

Run the validator and read its output. Never resolve a finding by converting `operation:
Upsert` to `Insert` + `deleteOldData` — that is destructive and requires explicit user
approval with a documented Bug 2 or Bug 3 justification.

## Output

Report as a table: check, status, owning builder, specific file and row. Then state plainly
whether the datasets are safe to deploy. The conductor asks for deploy approval only after
you pass.
