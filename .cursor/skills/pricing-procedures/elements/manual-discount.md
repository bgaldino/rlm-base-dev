# Manual Discount (`ManualDiscount`)

> Release 264 / API v68.0. Sources: `ind.pricing_add_manual_discount_element.htm`,
> `ind.pricing_pricing_discount_calendar.htm`; shipped XML:
> RLM_DefaultPricingProcedure, RLM_Revenue_Management_Recalc_Procedure,
> RLM_PRM_DISTI_Pricing_Procedure; core source (behavior only).

Applies a discretionary discount (percentage, amount or override) taken directly from
line-item values, with no decision table. [Help][Repo]

## When to use it
- Rep-entered or contract-supplied discounts: line discount percent/amount fields. [Help]
- Rule-driven discounts keyed on quantity, attribute or bundle: use
  [volume-and-tier-discount.md](./volume-and-tier-discount.md),
  [attribute-based-price.md](./attribute-based-price.md),
  [bundle-based-price.md](./bundle-based-price.md).
- The Pricing Discount calendar (volume/attribute/bundle schedule view on the product)
  does not show manual discounts; it reports price adjustment schedule types only. [Help
  `ind.pricing_pricing_discount_calendar.htm`]
- Stacking and waterfall rules: see "Placement" in
  [volume-and-tier-discount.md](./volume-and-tier-discount.md#placement-and-ordering).

## Configuration
| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Adjustment Type | `AdjustmentType` | Parameter | Yes | Context value or constant. Shipped maps `PercentageStringConstant`, `AmountStringConstant`, `ItemContractDiscountType`. [Repo] |
| Adjustment Value | `AdjustmentValue` | Parameter | Yes | `ItemDiscountPercentage`, `ItemDiscountAmount`, `ItemContractDiscountValue`. [Repo] |
| Quantity | `Quantity` | Parameter | Yes | `LineItemQuantity` |
| Input Unit Price | `InputUnitPrice` | Parameter | Yes | previous `NetUnitPrice` |
| Output: net unit price | `NetUnitPrice` | Parameter (output) | Yes | |
| Output: subtotal | `Subtotal` | Parameter (output) | Yes | `ItemNetTotalPrice` |
| Include in Output | `HideWaterfall` | Literal | Yes | `false` shows in waterfall |
| Boilerplate | `sectionCount=0`, `selectedFunction=Get`, `IsRealTime=false` | Literal | Yes | |

## Placement and ordering
- Shipped after volume (and bundle/attribute), before price revision. Two shapes:
  group `Applymanualdiscountstolineswithoutderivedpricing` (1 element), and group
  `Applyamountbasedandpercentagebaseddiscounts` (2 elements: amount-based seq 2, then
  percentage-based seq 3, so amount is deducted first, then percent applied). [Repo]
- Each lives under a ListGroup with an `AdvancedListFilter` at seq 1. [Repo]
- Header/line-level discounts spread later by DiscountDistribution are separate; see
  [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).

## Rules and limits
- No lookup table: values come from the line's context tags, so the tags must be
  mapped in the context definition (`../../context-service/SKILL.md`). [Help]
- Accepted `AdjustmentType` strings, matched case-insensitively: `Percentage`, `Amount`,
  `Override`, and the legacy tier-type values `AdjustmentPercentage`, `AdjustmentAmount`,
  `OverrideAmount`. [Core] Percentage is a whole number. Override replaces the unit
  price with the value; Amount subtracts it; Percentage multiplies by (100 - v)/100. [Core]
- Formal inputs are `AdjustmentType` (text), `AdjustmentValue` (numeric), `Quantity`,
  `InputUnitPrice`; the element has no lookup and no contract pricing. [Core]
- Core reads `AdjustmentType`/`AdjustmentValue` straight into the calculation payload
  during rule discovery; both tags must resolve or the step fails. [Core]
- A line whose type string matches none of the above, on a null input unit price, logs
  `INVALID_INPUT` (adjustment type error). Keep types to the strings above. [Core]

## Metadata shape
```xml
<steps>
  <actionType>ManualDiscount</actionType>
  <customElement>
    <parameters><input>true</input><name>AdjustmentType</name><output>false</output><type>Parameter</type><value>PercentageStringConstant</value></parameters>
    <parameters><input>true</input><name>AdjustmentValue</name><output>false</output><type>Parameter</type><value>ItemDiscountPercentage</value></parameters>
    <parameters><input>true</input><name>Quantity</name><output>false</output><type>Parameter</type><value>LineItemQuantity</value></parameters>
    <parameters><input>true</input><name>InputUnitPrice</name><output>false</output><type>Parameter</type><value>NetUnitPrice</value></parameters>
    <parameters><input>true</input><name>HideWaterfall</name><output>false</output><type>Literal</type><value>false</value></parameters>
    <parameters><input>true</input><name>sectionCount</name><output>false</output><type>Literal</type><value>0</value></parameters>
    <parameters><input>true</input><name>selectedFunction</name><output>false</output><type>Literal</type><value>Get</value></parameters>
    <parameters><input>true</input><name>IsRealTime</name><output>false</output><type>Literal</type><value>false</value></parameters>
    <parameters><input>false</input><name>NetUnitPrice</name><output>true</output><type>Parameter</type><value>NetUnitPrice</value></parameters>
    <parameters><input>false</input><name>Subtotal</name><output>true</output><type>Parameter</type><value>ItemNetTotalPrice</value></parameters>
  </customElement>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
`PercentageStringConstant` / `AmountStringConstant` are procedure constant resources
holding the type strings. [Repo]

## Shipped in this repo (snapshot)
| Procedure | Step group | What it does |
|---|---|---|
| Default, Recalc, PRM_DISTI | `Applyamountbasedandpercentagebaseddiscounts` (seq 2, 3) | Amount then percent line discounts |
| same | `Applymanualdiscountstolineswithoutderivedpricing` (seq 2) | Contract discount type/value (`ItemContract*`) |

Snapshot only. Discover: `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify
Simulate with the discount tags populated; waterfall shows the manual step. Check
`NetUnitPrice` on the quote line after entering a line discount.

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| Discount ignored | Type constant or value tag unmapped / null | Map context tags; check constants |
| Wrong discount size | Percent entered as fraction | Use whole number |
| Applied before volume | Step order | Reorder (sequence is element order) |

## Open questions
- Behavior for an unrecognized type on a non-null unit price was not fully traced; confirm
  live.
