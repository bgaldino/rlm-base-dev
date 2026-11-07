# Attribute-Based Price (`AttributeDiscount`)

> Release 264 / API v68.0. Sources: `ind.pricing_add_attribute_based_price_element.htm`,
> `ind.pricing_calculate_attribute_based_discounts.htm`,
> `ind.pricing_create_attribute_based_adjustments.htm`,
> `ind.pricing_attribute_based_pricing_limits.htm`,
> `ind.pricing_define_price_impacting_attributes.htm`,
> `ind.pricing_considerations_for_migrating_attribute_based_adjustments.htm`; shipped
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
| Adjustment type/value | `AdjustmentType`, `AdjustmentValue` | Parameter | Yes | |
| Quantity, Input Unit Price | `Quantity`, `InputUnitPrice` | Parameter | Yes | |
| Contract | `IsContractEnabled`, `IsContracted` | Literal / Parameter | Contract step | |
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
  definition; use attributes that belong directly to the product classification, not
  inherited ones. [Help]
- Numeric (Number, Currency, Percentage) and number picklists are stored with a
  decimal; input must include `.0` (10.0) or no match. [Help]
- A picklist cannot map to Boolean; use Checkbox/Boolean attribute. [Help]
- Attributes with an overridden bundle context are not supported. [Help]
- Each attribute value must resolve to one row; fix ambiguous adjustment rows. Output
  Resolution is not available on this element (only List Price, Price Tracking and
  Price Adjustment Matrix). [Help]
- Core skips attributes whose price-impacting flag is false or whose name/value is
  null; with no qualifying attributes it uses a null-hash marker. [Core]
- AND/OR: all qualifying price-impacting attributes on a line are combined into one
  hash and matched against each adjustment rule's conditions hash. So the conditions of
  one rule are ANDed (the line's whole price-impacting attribute set must equal the
  rule's), and separate rules are alternatives; extra price-impacting attributes on the
  line that a rule does not list prevent that rule matching. [Core, inferred from the
  hash construction]
- Name, value and price-impacting are multi-valued tags (one per attribute row); all
  three must be mapped to the same list node. [Core]
- Migration: deploy Attribute Based Adjustment Rules, then Conditions, then
  Adjustments; load all Conditions of one Rule in one batch. Hash mismatch fix: open
  and re-save a Condition, then run a validation transaction. [Help]

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
         InputUnitPrice, AdjustmentType/Value(+Field), LookUpName, IsContractEnabled -->
    <parameters><input>false</input><name>NetUnitPrice</name><output>true</output><type>Parameter</type><value>NetUnitPrice</value></parameters>
  </customElement>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
`AttributePASIdConstant` is a constant variable whose `<value>` is `__ATTRIBUTEPasID__`;
`find_replace` in `cumulusci.yml` swaps it for the Id of the schedule named
`Standard Attribute Based Adjustment`. Do not duplicate; see
[../../pricing-wiring/SKILL.md](../../pricing-wiring/SKILL.md) section B. The same
pattern covers `__VOLUMEPasID__` and `__BUNDLEPasID__`. [Repo]

## Shipped in this repo (snapshot)
| Procedure | Step group | What it does |
|---|---|---|
| Default, Recalc, PRM_DISTI | `Setattributebasedpricingforlineswithoutderivedpricing`, `...withoutcontractpricing` (seq 2) | Attribute adjustment, non-contract and contract variants |

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
- AND/OR rule above is derived from reading the hash construction, not a live test with
  a partial-match line.
