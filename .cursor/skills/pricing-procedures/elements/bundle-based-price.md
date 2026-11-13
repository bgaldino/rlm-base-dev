# Bundle-Based Price (`BundleDiscount`)

> Release 264 / API v68.0. Sources: `ind.pricing_add_bundle_based_price_element.htm`,
> `ind.pricing_calculate_bundle_based_discounts.htm`,
> `ind.pricing_create_bundle_based_adjustments.htm`; shipped XML: Default, Recalc,
> PRM_DISTI procedures; core source (behavior only).

Prices a bundle component using Bundle Based Adjustment records keyed on root bundle,
parent product and product. Also zeroes components flagged as inclusive.

## When to use it
- A product's price changes when sold inside a specific root bundle/parent. [Help]
- Not for quantity or attribute rules: see
  [volume-and-tier-discount.md](./volume-and-tier-discount.md) (stacking/waterfall),
  [attribute-based-price.md](./attribute-based-price.md).
- Creating the schedule and adjustment records: [`../../pricing-setup/price-adjustment-schedules.md`](../../pricing-setup/price-adjustment-schedules.md).

## Configuration
Declared by core: `InclusivePrice` (Boolean, optional), `Quantity` (Numeric, required),
`InputUnitPrice` (Currency, required), `AdjustmentTypeField` / `AdjustmentValueField`
(Text, optional) plus one input per decision-table input column; outputs `NetUnitPrice`,
`Subtotal`. Builder flags: lookup, contract pricing, hide waterfall, profile filter and
additional variables are all enabled. [Core]

| Builder field | Parameter name | Type | Notes |
|---|---|---|---|
| Lookup table | `LookUpName`, `LookUpApiName`, `LookUpId` | Literal | `Bundle Based Adjustment Entries` / `Bundle_Based_Adjustment_Decision_Table`. [Repo] |
| Price Adjustment Schedule | `PriceAdjustmentScheduleId` | Parameter | `BundlePASIdConstant` (`__BUNDLEPasID__`). [Repo] |
| Product / Selling Model | `ProductId`, `ProductSellingModelId` | Parameter | `Product`, `ProductSellingModel`. [Repo] |
| Parent Product / Selling Model | `ParentProductId`, `ParentProductSellingModelId` | Parameter | `MainItemProduct`, `MainItemProductSellingModel`. [Repo] |
| Root Bundle / Selling Model | `RootBundleId`, `RootProductSellingModelId` | Parameter | `RootItemProduct`, `RootProductSellingModel` (Help names the latter `RootItemProductSellingModel`; shipped XML differs). [Repo][Help] |
| Effective From / To | `EffectiveFrom`, `EffectiveTo` | Parameter | `EffectiveDate` in shipped XML (Help example maps `EffectiveFrom` to both). [Repo][Help] |
| Currency | `CurrencyIsoCode` | Parameter | A decision-table column; only the Default procedure's step maps `CurrencyIsoCode` (PRM and Recalc do not). [Repo] |
| Adjustment type/value field | `AdjustmentTypeField`, `AdjustmentValueField` | Parameter | Shipped: `Constant_AdjustmentType_Bundle_Based_Adjustment_Decision_Table_BBP` / `..Value..`. [Repo] |
| Inclusive Price | `InclusivePrice` | Parameter | Boolean tag; optional in core, mapped in all shipped copies. [Core][Repo] |
| Quantity, Input Unit Price | `Quantity`, `InputUnitPrice` | Parameter | `LineItemQuantity`, previous `NetUnitPrice`. [Repo] |
| Outputs | `NetUnitPrice`, `Subtotal` | Parameter (output) | `NetUnitPrice`, `ItemNetTotalPrice`. [Repo] |
| Boilerplate | `HideWaterfall`, `IsRealTime`, `IsContractEnabled=false`, `sectionCount`, `selectedFunction` | Literal | Shipped values. [Repo] |

Whether each decision-table column parameter is required is not verified; map them all
as shipped. [inferred]

## Placement and ordering
- Shipped after attribute, before volume. [Repo] Stacking: see
  [volume-and-tier-discount.md](./volume-and-tier-discount.md#placement-and-ordering).
- Needs bundle-position tags (root, parent) hydrated for each component line. [inferred]

## Rules and limits
- When `InclusivePrice` is true for any item in a bundle, the element sets the item's
  price to zero and later elements do not run for it. [Help] Core confirms net unit
  price and subtotal 0 and the line flagged inclusive; the skipping of later elements is
  not re-verified in core. [Core][Help]
- Prerequisites: product, root bundle, parent in a price book, with selling models for
  each. [Help]
- A `BundleBasedAdjustment` row inserted while its schedule was **active** succeeded, and after
  a decision-table refresh it priced the component [Measured: 2026-11-11, 264, fresh `ent-sb0`
  scratch org].
- A Bundle-Based Adjustment on a bundle whose root, parent and child selling models were all Term Defined
  Annual (root at 0.00) priced the child; the percentage showed in the waterfall between the attribute-based
  and volume steps [Measured: 2026-11-11, 264, scratch, one org; a configurable root with direct components, quote
  priced and ordered]. The adjustment validation has no check on the schedule's active flag, whereas adding or removing a tier and bound edits are refused while the schedule is active [Platform behaviour, traced]; do not treat this as a supported way to change an active schedule. Volume tiers behave differently: adding or removing a tier, or changing its bounds, fails while its schedule is active
  ([`volume-and-tier-discount.md`](volume-and-tier-discount.md) → Rules and limits, [Repo,
  measured]). Help still says to deactivate a
  schedule before adding records
  ([`../../pricing-setup/price-adjustment-schedules.md`](../../pricing-setup/price-adjustment-schedules.md)).
- Types: Percentage, Amount, Override. [Help] Core also accepts the legacy values
  `AdjustmentPercentage`, `AdjustmentAmount`, `OverrideAmount`, all case-insensitive. [Core]
- Lookup payload errors: "Unexpected error occurred while looking up {element}"
  (`UNEXPECTED_ERROR_DURING_LOOKUP`). More than one matching row: "Duplicate entries found
  while looking up {element}" (`DUPLICATE_VALUE_FOUND_IN_LOOKUP`). [Core]
- One row: Override replaces the unit price, Amount subtracts, Percentage multiplies by
  (100 - v)/100; no clamping or rounding, so an oversized Amount goes negative. Zero rows:
  price unchanged. [Core]
- A matched row with a blank type or a null value leaves the price unchanged and
  `IsContracted` false. [Core]
- A type that is not one of the strings above (or Amount/Percentage with a null input
  unit price) logs `INVALID_INPUT`: "Specify valid Adjustment Type and Adjustment Value
  field values for the {element} element and try again." For a null input unit price the
  message is "The adjustment type for this line item must be set to Override." Outputs are
  then not written. [Core]
- The step sets `IsContracted` false first; a successful single-row adjustment sets it
  true. [Core]
- When `InclusivePrice` is true the lookup result is ignored (even a matching row is not
  applied): net unit price 0, subtotal 0, line flagged inclusive. A duplicate-row error
  still fires first if the lookup returned two or more rows. Null `InclusivePrice` is
  treated as false. [Core]
- Matching keys are the decision-table input columns you map (product, parent, root
  bundle, selling models, dates, schedule). Nested bundles match per level: "parent" is
  the immediate parent, "root" the top bundle. A root bundle line has no root/parent
  context, so an adjustment only applies to components. [inferred]

### Feasibility / not supported
| Question | Answer |
|---|---|
| Discount the root bundle line itself? | Not with this element: rows key on root plus parent. Use Manual Discount or a matrix. [inferred] |
| Two rows for one component under the same root/parent? | No: `DUPLICATE_VALUE_FOUND_IN_LOOKUP`. Output Resolution is not available here. [Core][Help] |
| Free (bundled-in) component? | Yes: `InclusivePrice` true zeroes the line. Shipped also has a group `Assigntotallineamountforlineswithinclusiveprice` after proration. [Core][Repo] |
| Cumulative quantity or tier bands? | No; this element has none. [Core] |
| Percentage/Amount on a line with no input unit price? | No: `INVALID_INPUT`; only Override works. [Core] |

## Metadata shape
```xml
<steps>
  <actionType>BundleDiscount</actionType>
  <customElement>
    <parameters><input>true</input><name>PriceAdjustmentScheduleId</name><output>false</output><type>Parameter</type><value>BundlePASIdConstant</value></parameters>
    <parameters><input>true</input><name>ParentProductId</name><output>false</output><type>Parameter</type><value>MainItemProduct</value></parameters>
    <parameters><input>true</input><name>RootBundleId</name><output>false</output><type>Parameter</type><value>RootItemProduct</value></parameters>
    <parameters><input>true</input><name>InclusivePrice</name><output>false</output><type>Parameter</type><value>InclusivePrice</value></parameters>
    <parameters><input>true</input><name>LookUpApiName</name><output>false</output><type>Literal</type><value>Bundle_Based_Adjustment_Decision_Table</value></parameters>
    <parameters><input>true</input><name>LookUpId</name><output>false</output><type>Literal</type><value>__LOOKUPID_BUNDLE_BASED_ADJUSTMENT_DECISION_TABLE__</value></parameters>
    <!-- plus ProductId, ProductSellingModelId, ParentProductSellingModelId,
         RootProductSellingModelId, EffectiveFrom/To, Quantity, InputUnitPrice,
         AdjustmentTypeField/AdjustmentValueField, LookUpName -->
    <parameters><input>false</input><name>NetUnitPrice</name><output>true</output><type>Parameter</type><value>NetUnitPrice</value></parameters>
  </customElement>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
Placeholders resolve at deploy in the Default and PRM procedures; the Recalc procedure ships
literal source-org ids instead. See [../../pricing-wiring/SKILL.md](../../pricing-wiring/SKILL.md). [Repo]

## Shipped in this repo (snapshot)
Three `BundleDiscount` steps in the repo, one per procedure (none in the other 8
procedure files under the three `expressionSetDefinition/` folders). Each sits in
ListGroup `Applybundlebasedadjustments` after an `AdvancedListFilter` at seq 1
(`Filterlineswithoutlasttransactionpricingtoapplybundlebasedadjustments`). [Repo]

| Procedure | Group seq | Step (seq 2) |
|---|---|---|
| `RLM_DefaultPricingProcedure` | 19 | `Calculatenettotalpriceafterbundlebasedadjustments` |
| `RLM_Revenue_Management_Recalc_Procedure` | 13 | same name |
| `RLM_PRM_DISTI_Pricing_Procedure` | 17 | same name |

Snapshot only. Discover: `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify
Simulate a component line with root/parent set (Help example: Printer Bundle under
Laptop Pro Bundle, Override 20); check waterfall and refreshed Bundle Based Adjustment
Entries table.

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| No bundle price | Root/parent tags blank or table stale | Hydrate context; refresh table |
| Component priced 0 | `InclusivePrice` true | Intended; clear flag if not |
| Duplicate lookup error | Two rows for same root/parent/product | Remove duplicate |

## Settled notes
- Root selling model (settled): the Bundle Based Adjustment field is
  `RootProductSellingModel`, as in the shipped XML and the sfdmu CSVs. The context tag
  `RootItemProductSellingModel` (the Help name) is a separate, built-in sales
  transaction tag. Use the XML names above. [Repo]
