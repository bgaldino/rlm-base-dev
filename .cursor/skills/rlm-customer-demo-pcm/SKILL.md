---
name: rlm-customer-demo-pcm
description: >-
  Authors the customer-template-pcm SFDMU dataset for Revenue Cloud customer demos —
  Product2, ProductSellingModel/Option, catalog and categories, attribute framework
  (AttributePicklist, AttributeDefinition, ProductAttributeDefinition), bundles
  (ProductComponentGroup, ProductRelatedComponent), and UnitOfMeasure rows. Use when
  building or fixing customer-template-pcm CSVs, Product2 shape, Product2.Type,
  ConfigureDuringSale, attribute picklist codes, or MissingParentRecordsReport triage.
disable-model-invocation: true
---

# PCM builder

Owns `datasets/sfdmu/customer-template/en-US/customer-template-pcm/**`. Authoring only —
never run `cci`, `sf`, or any deploy/import command.

Input: `sku-contract.yaml` (SKUs, categories, bundles, attributes, uom) and
`org-context.json` (valid PSM names, UOM codes, proration policies).

Reference shape for every advanced object: `datasets/sfdmu/qb/en-US/qb-pcm/`.

## Product2.csv — mirror the qb-pcm column layout

The plan's `Product2` SOQL selects `BasedOnId`, `UnitOfMeasureId`, and
`QuantityUnitOfMeasure`. A short column set makes SFDMU emit placeholder parent keys
(`ID000…`) into `reports/MissingParentRecordsReport.csv`. The log still says Product2 rows
were "processed" while **no product is queryable by SKU**, and
`customer_demo_recreate_pricebook_via_api` later fails with "Missing Product2 records".

Copy the header layout from `datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv` and fill:

| Column | Value |
|---|---|
| `BasedOn.Code` | empty unless the product is based on a `ProductClassification` |
| `CanRamp` | `false` |
| `IsSoldOnlyWithOtherProds` | `false` |
| `QuantityUnitOfMeasure` | usually `EACH` — confirm it exists in `org-context.json` |
| `UnitOfMeasure.UnitCode` | `EACH` or another org-native default |
| `DisplayUrl` | **empty** — the Experience builder sets it after static resources deploy |

## Type and ConfigureDuringSale

Decide before the first insert; treat as immutable. Many orgs allow only `Base`, `Bundle`,
`Set`.

- `Type = Bundle` on parent bundle SKUs only. Blank for everything else.
- `ConfigureDuringSale = Allowed` is **required** when `Type = Bundle`.
- `ConfigureDuringSale = Allowed` is **also required** for every SKU that appears in
  `ProductAttributeDefinition.csv`. Without it the attribute panel never renders on the
  quote and attribute-based pricing never fires. Cross-check PAD rows against Product2.csv
  before you finish.
- Avoid typing bundle children as `Base` or `Set`; some orgs reject those as components.

## Attribute framework — two org-unique namespaces

**`AttributePicklistValue.Code` is a global externalId** across every picklist in the org.
Two values sharing a `Code` in different picklists overwrite each other and cascade-fail
`AttributeDefinition`, `AttributeCategoryAttribute`, `ProductClassificationAttr`, and
`ProductAttributeDefinition` — often aborting the whole PCM job with `ERROR_HTTP_404`.
Use the contract's prefixed codes exactly as written.

**`AttributeDefinition.DeveloperName` is org-unique.** Always customer-prefixed
(`ACME_Service_Tier`, not `Service_Tier`). Collisions fail silently inside the batch.

Set `IsPriceImpacting = true` on any attribute named in the contract's `pricing_rules`.

## Selling models and proration

`ProductSellingModel.Name` + `SellingModelType` must exist in `org-context.json` and match
`customer-pricebook-entries.csv` exactly. Prefer `TermDefined` monthly/annual for recurring
offers so proration and amend/cancel/replace demo cleanly. `ProductSellingModelOption` rows
reference a `ProrationPolicy.Name` — default `Default Proration Policy`, but confirm against
`org-context.json`.

## Usage demos

When `flags.customer_demo_usage` is true, PCM must also create the metering foundation the
rating plan references:

- `UnitOfMeasureClass` with `Type = Usage`, plus `BaseUnitOfMeasure` and `DefaultUnitOfMeasure`
- `UnitOfMeasure` rows under that class
- both the sellable usage SKUs and the usage-definition SKUs from the contract

Keep `Code` / `UnitCode` / `Name` identical to what the contract's `usage` section declares —
the rating and rates plans resolve these by `Name` in SFDMU v5.

## SFDMU v5

Keep `;` delimiters in `export.json` `externalId`. Do not convert any existing `Upsert` to
`Insert` + `deleteOldData` — that is destructive and requires explicit user approval.

PCM Upserts are safe to re-run; fix data and load again rather than deleting.

## Before you finish

1. Every contract SKU has a Product2 row.
2. Every PAD SKU has `ConfigureDuringSale = Allowed`.
3. Every `AttributePicklistValue.Code` is unique across all picklists in the file set.
4. Every `AttributeDefinition.DeveloperName` carries the customer prefix.
5. `ProductCategoryProduct` covers each SKU's `category_code`.
6. No `DisplayUrl` values are set.

Deeper detail: `datasets/sfdmu/customer-template/en-US/customer-template-pcm/README.md`,
`docs/guides/customer-demo-onboarding.md`.
