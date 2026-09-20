---
name: rlm-customer-demo-pricing
description: >-
  Authors attribute-based pricing for Revenue Cloud customer demos — the
  customer-template-pricing SFDMU dataset (AttributeBasedAdjRule) plus the Apex scripts
  that insert AttributeAdjustmentCondition and AttributeBasedAdjustment. Use when building
  or fixing ABR/AAC/ABA records, attribute-driven price adjustments, ExpectedPricingRules
  verification, or SFDMU SOURCE-0 FK resolution failures on pricing objects.
disable-model-invocation: true
---

# Pricing builder

Owns:

- `datasets/sfdmu/customer-template/en-US/customer-template-pricing/**`
- `scripts/apex/insertCustomerDemoPricingAdjustments.apex`
- `scripts/apex/deleteCustomerDemoPricingData.apex`

Authoring only — never run `cci`, `sf`, or any deploy/import command.

Input: `sku-contract.yaml` → `pricing_rules`, `attributes`, and each SKU's
`expected_pricing_rules`.

## The chain

```
AttributeBasedAdjRule -> AttributeAdjustmentCondition -> AttributeBasedAdjustment
```

Loaded in two phases because AAC and ABA **cannot** go through SFDMU:

| Phase | Task | Mechanism | Objects |
|---|---|---|---|
| 1 | `insert_customer_demo_pricing_data` | SFDMU | `AttributeBasedAdjRule` Upsert |
| 2 | `insert_customer_demo_pricing_adjustments` | Apex | AAC + ABA Insert |

## Why AAC/ABA must be Apex

For `Insert` operations SFDMU resolves FK columns from the parent's **SOURCE** collection.
`Readonly` parents are fetched from the target org into the **TARGET** collection, so SOURCE
is always empty and every child row is silently filtered (`SOURCE: 0`) — even when the ABRs
exist in the org and the Readonly CSVs are populated.

This is not fixable by restructuring `objectSets` or by splitting into separate SFDMU tasks.
Do not attempt either. Apex resolves FKs explicitly via SOQL.

The AAC and ABA CSVs stay in the plan as documentation of the intended shape and for
extraction roundtrips.

## Apex script rules

- `Operator` is the word **`equals`**, never `=`. Anything else throws
  `INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST`.
- Omit ABA platform-computed fields from constructors — `AttributeAdjConditionsHash`,
  `AttributeCount`, `PricingTerm`, `PricingTermUnit`, `ScheduleType`, `SellingModelType`.
  Including any of them is a compile error (`Field is not writeable`). Leave them blank in
  CSVs too.
- `AttributeAdjustmentCondition` cannot be deleted by direct DML — it is a master-detail
  child. Delete `AttributeBasedAdjustment` first (explicit DML, not cascade), then
  `AttributeBasedAdjRule`, which cascades AAC.
- Scope every delete to the customer prefix (`WHERE Name LIKE 'ACME-%'`) so coexisting QB
  pricing data survives. Never use `DeleteSFDMUData` here.
- Keep the insert idempotent — skip when the records already exist.

## export.json rules

SELECT clauses must use **direct ID fields**, not relationship traversals:

```sql
SELECT AttributeBasedAdjRuleId, AttributeDefinitionId, BooleanValue, DateValue,
       DateTimeValue, DoubleValue, IntegerValue, Operator, ProductId, StringValue
FROM AttributeAdjustmentCondition
```

With traversal fields (`AttributeBasedAdjRule.Name`) SFDMU logs "Referenced field removed"
and loses FK context, then crashes with `COMMAND_UNEXPECTED_ERROR`.

## AAC CSV column count

11 columns, five of them empty for string conditions. One missing comma shifts `equals` into
`IntegerValue` and SFDMU reads zero source records.

```
$$AttributeBasedAdjRule.Name$AttributeDefinition.Code$Product.StockKeepingUnit,
AttributeBasedAdjRule.Name, AttributeDefinition.Code,
BooleanValue, DateTimeValue, DateValue, DoubleValue, IntegerValue,
Operator, Product.StockKeepingUnit, StringValue
```

String-value row: `RULE;ATTR;SKU,RULE,ATTR,,,,,,equals,SKU,Enterprise`

## Verification contract

`customer_demo_verify_catalog` counts ABA records per SKU against `ExpectedPricingRules` in
`customer-pricebook-entries.csv`. Your rule count per SKU must equal the contract's
`expected_pricing_rules` for that SKU. If they disagree, report it — do not edit the
pricebook CSV, which the conductor owns.

## Before you finish

1. Every `pricing_rules` entry has one ABR, one AAC, and one ABA.
2. Per-SKU ABA count equals `expected_pricing_rules`.
3. Every referenced attribute code exists in the contract's `attributes.definitions` and is
   marked `is_price_impacting`.
4. Apex delete scope matches `customer.prefix`.

Deeper detail: `datasets/sfdmu/customer-template/en-US/customer-template-pricing/README.md`
(Lessons 1-8), reference plan `datasets/sfdmu/qb/en-US/qb-pricing/`.
