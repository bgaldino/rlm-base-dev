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
| Hide in waterfall | `HideWaterfall` | Literal | Yes | `false` shows in waterfall. Include in Output is the separate step field `resultIncluded` [Dev guide][Repo] |
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
- Core declares four inputs, all required: `AdjustmentType` (Text), `AdjustmentValue`
  (Numeric), `Quantity` (Numeric), `InputUnitPrice` (Currency); outputs `NetUnitPrice`,
  `Subtotal`. Builder flags: lookup off, contract pricing off, hide waterfall on, profile
  filter and additional variables on. [Core]
- No lookup table: values come from the line's context tags, so the tags must be
  mapped in the context definition (`../../context-service/SKILL.md`). [Help]
- Accepted `AdjustmentType` strings, matched case-insensitively: `Percentage`, `Amount`,
  `Override`, and the legacy tier-type values `AdjustmentPercentage`, `AdjustmentAmount`,
  `OverrideAmount`. Percentage is a whole number. Override replaces the unit price with the
  value; Amount subtracts it; Percentage multiplies by (100 - v)/100. [Core]
- Core reads `AdjustmentType`/`AdjustmentValue` straight from the line's tags into the
  calculation payload; a tag that is not mapped for the element is not guarded, so the
  step can fail. [Core][inferred for the failure mode]
- A type string that matches none of the above logs `INVALID_INPUT` and leaves the price
  unchanged (outputs not written). Message: "Specify valid Adjustment Type and Adjustment
  Value field values for the Manual Discount element and try again." Keep types to the
  strings above. [Core]
- Amount and Percentage need a non-null input unit price. With a null `InputUnitPrice`
  only Override works; any other type logs `INVALID_INPUT`: "The adjustment type for this
  line item must be set to Override." [Core]
- A blank type or a null value on the line is not an error: the step leaves the price
  unchanged and `IsContracted` false (so an unset line discount field is a no-op). [Core]
- A successful adjustment sets `IsContracted` true on the line. [Core]
- Scope: only `AdjustmentType` and `AdjustmentValue` are read, so "amount vs percent" is
  decided by the type string, not by which field is populated; to honour both a percent
  and an amount field, use two steps (shipped: amount seq 2, then percent seq 3). [Core][Repo]
- No clamping or rounding: Amount above the unit price or Percentage above 100 gives a
  negative price; Override accepts any value including 0 or negative. Add Rounding
  Values and, if needed, a price floor. Either add a Formula-Based Pricing step after the
  discount that clamps the unit price (for example `IF(NetUnitPrice < 0, 0, NetUnitPrice)`)
  and recomputes the subtotal from it (functions known to work:
  [formula-based-pricing.md](./formula-based-pricing.md)), or put a List Group condition
  around the discount so an oversized one never runs. Stop Pricing is not a floor: it makes
  the current, already negative price final [Help]. [Price Tracking](./price-tracking.md)
  only records historical min/max. [Core][inferred for the floor]
- Applies per line; for a bundle component the same rules apply. Whether a manual
  discount on a bundle parent propagates to children is not verified. [inferred]

### Feasibility / not supported
| Question | Answer |
|---|---|
| Discount at header level? | No: this element is per line. Use Discount Distribution for spreading. [Help][Repo] |
| Cap a manual discount (maximum percent)? | Not in the element; enforce with approvals, validation or a Formula step. [inferred] |
| Both percent and amount on one line? | Two steps in the order you want (amount then percent in shipped XML). [Repo] |
| Lookup-driven values? | No lookup; Builder lookup and contract-pricing options are off. Use Volume/Attribute/Bundle or a matrix. [Core] |
| Percentage/Amount when the incoming unit price is null? | No: `INVALID_INPUT`; only Override. [Core] |
| Output Resolution (multiple rows)? | Not applicable: the payload is one row built from the line. [inferred] |

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
Three `ManualDiscount` steps in each of three procedures (none in the other 8 procedure
files under the three `expressionSetDefinition/` folders). Group sequence is the
top-level order; step sequence is inside the group. [Repo]

| Procedure | Group (seq) | Step (seq) | Type / value mapping |
|---|---|---|---|
| `RLM_DefaultPricingProcedure` | `Applymanualdiscountstolineswithoutderivedpricing` (22) | `Calculatenetunitanditemnettotalpricesaftermanualdiscount` (2) | `ItemContractDiscountType` / `ItemContractDiscountValue` |
| same | `Applyamountbasedandpercentagebaseddiscounts` (23) | `...afteramountbaseddiscount` (2) | `AmountStringConstant` / `ItemDiscountAmount` |
| same | same (23) | `...afterpercentagebaseddiscount` (3) | `PercentageStringConstant` / `ItemDiscountPercentage` |
| `RLM_Revenue_Management_Recalc_Procedure` | groups 16 and 17 | same names, seq 2, 2, 3 | same |
| `RLM_PRM_DISTI_Pricing_Procedure` | groups 20 and 21 | same names, seq 2, 2, 3 | same |

Step names above omit the common prefix `Calculatenetunitanditemnettotalpricesafter`.

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
