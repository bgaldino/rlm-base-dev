# Attribute-Based Price (`AttributeDiscount`)

> Release 264 / API v68.0. Sources: `ind.pricing_add_attribute_based_price_element.htm`,
> `ind.pricing_calculate_attribute_based_discounts.htm`,
> `ind.pricing_create_attribute_based_adjustments.htm`,
> `ind.pricing_attribute_based_pricing_limits.htm`,
> `ind.pricing_define_price_impacting_attributes.htm`,
> `ind.pricing_considerations_for_migrating_attribute_based_adjustments.htm`,
> `ind.pricing_limits.htm`, `ind.pricing_create_price_adjustment_schedules.htm`; shipped
> XML: Default, Recalc, PRM_DISTI procedures; core source (behavior only).

Adjusts the unit price using Attribute Based Adjustment records that match the line's
price-impacting attribute values.

## When to use it
- Price depends on configured attributes (colour, resolution, plan tier). [Help]
- Not for quantity bands or bundle membership: see
  [volume-and-tier-discount.md](./volume-and-tier-discount.md) (stacking rules are
  there) and [bundle-based-price.md](./bundle-based-price.md).

## Configuration
| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Lookup table | `LookUpName`, `LookUpApiName`, `LookUpId` | Literal | Yes | `Attribute Discount Entries` / `Attribute_Based_Adjustment_Decision_Table`. [Repo] |
| Price Adjustment Schedule | `PriceAdjustmentScheduleId` | Parameter | Yes | `AttributePASIdConstant` (placeholder `__ATTRIBUTEPasID__`); contract step uses `ItemContractAttributePasId`. [Repo] |
| Product / Selling Model | `ProductId`, `ProductSellingModelId` | Parameter | Yes | |
| Effective From / To | `EffectiveFrom`, `EffectiveTo` | Parameter | Yes | `EffectiveDate` or `PricingDate`. [Repo] |
| Attribute Name | `AttributeName` | Parameter | Yes | `Attribute`; multi-valued per line. [Repo][Core] |
| Attribute Value | `AttributeValue` | Parameter | Yes | |
| Is Price Impacting | `IsPriceImpacting` | Parameter | Yes | `PriceImpactingAttribute`. |
| Adjustment type/value columns | `AdjustmentTypeField`, `AdjustmentValueField` | Parameter | Yes | Constants naming table columns. [Repo] |
| Adjustment type/value (output) | `AdjustmentType`, `AdjustmentValue` | Parameter, `input=false`, `output=true` | No | Outputs, shipped only in the Recalc procedure. Not inputs (unlike Manual Discount). [Repo] |
| Quantity, Input Unit Price | `Quantity`, `InputUnitPrice` | Parameter | Yes | |
| Contract | `IsContractEnabled`, `IsContracted` | Literal / Parameter | `IsContractEnabled` on every shipped step (`true` on the contract step) | [Repo] |
| Currency | `CurrencyIsoCode` | Parameter | Multi-currency | |
| Outputs | `NetUnitPrice`, `Subtotal` | Parameter (output) | Yes | |
| Boilerplate | `HideWaterfall`, `IsRealTime`, `sectionCount`, `selectedFunction` | Literal | Yes | |

## Placement and ordering
- Shipped two groups before bundle/volume/manual: without derived pricing, and without
  contract pricing. [Repo] See
  [volume-and-tier-discount.md](./volume-and-tier-discount.md#placement-and-ordering)
  for sequential stacking and waterfall.
- Attribute tags must be hydrated in the context before this step. The line's
  attribute rows are hashed at rule discovery and matched to the table's conditions
  hash. [Core]

## Rules and limits
- Attribute must be active, and Is Price Impacting selected on the product's attribute
  definition (Product > Related > Overridden Inherited Attributes; use Configure on an
  inherited attribute to move it there, then edit its Product Attribute Definition).
  Use attributes that belong directly to the product classification, not inherited
  ones: selecting an inherited one gives a validation error on save. [Help]
- Adjustment records: use or clone the Standard Attribute Based Adjustment schedule;
  deactivate it before adding records, reactivate after. Types Percentage, Amount,
  Override. Conditions are set on the Attribute Adjustment Condition object, which needs
  Pricing Manager; creating records needs Pricing Design Time. Prerequisites: a product
  selling model, products in a price book, at least one price-impacting attribute. [Help]
  Schedule and record setup: [`../../pricing-setup/price-adjustment-schedules.md`](../../pricing-setup/price-adjustment-schedules.md).
- Inserting an `AttributeBasedAdjustment` record directly (REST, schedule deactivated first as
  above) refuses `AttributeCount`,
  `PricingTerm`, `PricingTermUnit`, `ScheduleType` and `SellingModelType` with
  `INVALID_FIELD_FOR_INSERT_UPDATE`: the platform derives them. Send the rule, schedule, product,
  selling model, currency, `EffectiveFrom`, `AdjustmentType` and `AdjustmentValue`. With the
  rule's Attribute Adjustment Conditions already saved, the platform filled
  `AttributeAdjConditionsHash` on insert. A negative Percentage value is accepted and works as an
  uplift ([`root-answer-child-price.md`](root-answer-child-price.md) → Route 1 measured)
  [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]. The repo's SFDMU
  `AttributeBasedAdjustment.csv` files carry those derived columns; how SFDMU handles them was not
  checked here.
- The procedure's schedule input is a Text constant holding the schedule record Id (Help
  copies it from the record URL); refresh the Attribute Discount Entries table after
  activating. [Help]
- Numeric (Number, Currency, Percentage) and number picklists are stored with a
  decimal; input must include `.0` (10.0) or no match. [Help]
- A picklist cannot map to Boolean (for example text such as "Available" to true/false);
  saving one gives a design-time error. Use a Checkbox/Boolean attribute. [Help]
- Attributes with an overridden bundle context are not supported: the override stops the
  adjustment applying; for a product in a bundle, define the attribute once. [Help]
- Price-impacting attributes per product: default 25, minimum 1, maximum 50. [Help:
  `ind.pricing_limits.htm`]
- Each attribute value must resolve to one row; fix ambiguous adjustment rows. Output
  Resolution is not available on this element (only List Price, Price Tracking and
  Price Adjustment Matrix). [Help]
- Core skips attributes whose price-impacting flag is false or whose name/value is
  null; with no qualifying attributes it uses a null-hash marker. [Core]
- AND/OR: all qualifying price-impacting attributes on a line are combined into one
  hash and matched against each adjustment rule's conditions hash. So the conditions of
  one rule are ANDed (the line's whole price-impacting attribute set must equal the
  rule's), and separate rules are alternatives; extra price-impacting attributes on the
  line that a rule does not list prevent that rule matching. [Core: line side, all
  qualifying attributes go into one map hashed into a single lookup key (keys sorted),
  an empty map gives a null marker. Rule side, when Attribute Adjustment Conditions are
  saved, all conditions under one rule are collected into one map of attribute developer
  name to value and hashed with the same function into the rule's conditions hash, so
  equality of the two hashes means the attribute sets are identical.]
- [Core] If any of the three attribute tag lists is missing from the line, no hash is
  built and the line gets no adjustment. An attribute row whose name, value or flag is
  null is skipped; a false flag is skipped. Attribute name/value pairs form one map, so
  two rows with the same name collapse to the last value.
- [Core] Adjustment math is the shared one: Override replaces the unit price, Amount
  subtracts, Percentage multiplies by (100 - v)/100; two or more matching rows error
  `DUPLICATE_VALUE_FOUND_IN_LOOKUP`; zero rows leave the price unchanged. Amount or
  Percentage with a null input unit price, or an unknown type, errors `INVALID_INPUT`.
  [inferred] No clamping or rounding was found, so an oversized Amount may go negative.
- Name, value and price-impacting are multi-valued tags (one per attribute row); all
  three must be mapped to the same list node. [Core]
- Migration: deploy Attribute Based Adjustment Rules, then Conditions, then
  Adjustments; load all Conditions of one Rule in one batch. Hash mismatch fix: open
  and re-save a Condition (no changes; it regenerates the parent hash), then run a
  validation transaction. Do not split Conditions of one Rule across parallel batches
  (hash conflicts); keep parents before children. No single automated check exists:
  compare the hash in the Ops Console with the Condition's hash and validate in the
  Pricing Operations Console before finishing. [Help]

### Feasibility / not supported
| Question | Answer |
|---|---|
| Use inherited attributes? | Not supported; use attributes on the product's own classification. [Help] |
| Match on a subset (OR) of a line's price-impacting attributes? | No: the whole price-impacting set is one hash on both line and rule side. Add a rule per combination. [Core] |
| Overridden bundle-context attributes? | Not supported. [Help] |
| Boolean from a picklist? | No; use a Checkbox attribute. [Help] |
| Combine with another matching adjustment on the same line? | Not within this element (single match); stack with later elements. [Core] |

## Metadata shape
```xml
<steps>
  <actionType>AttributeDiscount</actionType>
  <customElement>
    <parameters><input>true</input><name>PriceAdjustmentScheduleId</name><output>false</output><type>Parameter</type><value>AttributePASIdConstant</value></parameters>
    <parameters><input>true</input><name>AttributeName</name><output>false</output><type>Parameter</type><value>Attribute</value></parameters>
    <parameters><input>true</input><name>AttributeValue</name><output>false</output><type>Parameter</type><value>AttributeValue</value></parameters>
    <parameters><input>true</input><name>IsPriceImpacting</name><output>false</output><type>Parameter</type><value>PriceImpactingAttribute</value></parameters>
    <parameters><input>true</input><name>LookUpApiName</name><output>false</output><type>Literal</type><value>Attribute_Based_Adjustment_Decision_Table</value></parameters>
    <parameters><input>true</input><name>LookUpId</name><output>false</output><type>Literal</type><value>__LOOKUPID_ATTRIBUTE_BASED_ADJUSTMENT_DECISION_TABLE__</value></parameters>
    <!-- plus ProductId, ProductSellingModelId, EffectiveFrom/To, Quantity,
         InputUnitPrice, AdjustmentTypeField/AdjustmentValueField, LookUpName, IsContractEnabled -->
    <parameters><input>false</input><name>NetUnitPrice</name><output>true</output><type>Parameter</type><value>NetUnitPrice</value></parameters>
  </customElement>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
`AttributePASIdConstant` is a constant variable whose `<value>` is `__ATTRIBUTEPasID__`;
`find_replace` in `cumulusci.yml` swaps it for the Id of the schedule named
`Standard Attribute Based Adjustment`. Do not duplicate; see
[../../pricing-wiring/SKILL.md](../../pricing-wiring/SKILL.md) section B. The same
pattern covers `__VOLUMEPasID__` and `__BUNDLEPasID__`. This holds for the Default and PRM
procedures; the Recalc procedure ships literal source-org schedule and `LookUpId` values that
no transform replaces. [Repo]

## Shipped in this repo (snapshot)
| Procedure | Step group | What it does |
|---|---|---|
| Default, Recalc, PRM_DISTI | `Setattributebasedpricingforlineswithoutderivedpricing` and `...withoutcontractpricing` groups (top-level seq: Default 17/18, Recalc 11/12, PRM_DISTI 15/16), each holding one AttributeDiscount step (seq 2) | Attribute adjustment, derived-free and non-contract variants. [Repo] |

Snapshot only. Discover: `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify
Simulate with `Attribute`, `AttributeValue`, `PriceImpactingAttribute=true` inputs
(Help example: Display = 4K Built-in Display); waterfall shows the attribute step.
Refresh the Attribute Discount Entries decision table first
(`../../decision-tables/SKILL.md`).

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| No adjustment | Stale table; `.0` missing; inherited/overridden attribute; hash mismatch | See limits above |
| Fine in source org, none after migration | Condition hash mismatch | Re-save a Condition [Help] |
| Placeholder error on deploy | `__ATTRIBUTEPasID__` unresolved | Standard schedule missing; check transform |

## Open questions
- AND/OR rule above is from reading both hash constructions, not a live test with a
  partial-match line.
