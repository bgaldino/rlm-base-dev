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

## Configuration
| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Lookup table | `LookUpName`, `LookUpApiName`, `LookUpId` | Literal | Yes | `Bundle Based Adjustment Entries` / `Bundle_Based_Adjustment_Decision_Table`. [Repo] |
| Price Adjustment Schedule | `PriceAdjustmentScheduleId` | Parameter | Yes | `BundlePASIdConstant` (`__BUNDLEPasID__`). [Repo] |
| Product / Selling Model | `ProductId`, `ProductSellingModelId` | Parameter | Yes | |
| Parent Product / Selling Model | `ParentProductId`, `ParentProductSellingModelId` | Parameter | Yes | `MainItemProduct`, `MainItemProductSellingModel`. [Repo] |
| Root Bundle / Selling Model | `RootBundleId`, `RootProductSellingModelId` | Parameter | Yes | `RootItemProduct`, `RootProductSellingModel` (Help names the latter `RootItemProductSellingModel`; shipped XML differs). [Repo][Help] |
| Effective From / To | `EffectiveFrom`, `EffectiveTo` | Parameter | Yes | `EffectiveDate` |
| Adjustment type/value (+Field) | `AdjustmentType`, `AdjustmentValue`, `AdjustmentTypeField`, `AdjustmentValueField` | Parameter | Yes | |
| Inclusive Price | `InclusivePrice` | Parameter | Yes | Boolean tag. [Repo] |
| Quantity, Input Unit Price | `Quantity`, `InputUnitPrice` | Parameter | Yes | |
| Outputs | `NetUnitPrice`, `Subtotal` | Parameter (output) | Yes | |
| Boilerplate | `HideWaterfall`, `IsRealTime`, `IsContractEnabled=false`, `sectionCount`, `selectedFunction` | Literal | Yes | |

## Placement and ordering
- Shipped after attribute, before volume. [Repo] Stacking: see
  [volume-and-tier-discount.md](./volume-and-tier-discount.md#placement-and-ordering).
- Needs bundle-position tags (root, parent) hydrated for each component line.

## Rules and limits
- When `InclusivePrice` is true for any item in a bundle, the element sets the item's
  price to zero and later elements do not run for it. [Help][Core: net and subtotal
  set to 0, line flagged inclusive]
- Prerequisites: product, root bundle, parent in a price book, with selling models for
  each. [Help]
- Types: Percentage, Amount, Override. [Help] Formal inputs include `InclusivePrice`
  (Boolean), `Quantity`, `InputUnitPrice`, `AdjustmentTypeField`, `AdjustmentValueField`
  plus one input per decision-table column; supports lookup, contract and hide-waterfall
  options. [Core]
- [Core] If the lookup errors or returns more than one row: `DUPLICATE_VALUE_FOUND_IN_LOOKUP`
  / `UNEXPECTED_ERROR_DURING_LOOKUP`; one row applies via the shared discount math; zero
  rows leaves price unchanged. Bundle path is not marked contracted.

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
         AdjustmentType/Value(+Field), LookUpName -->
    <parameters><input>false</input><name>NetUnitPrice</name><output>true</output><type>Parameter</type><value>NetUnitPrice</value></parameters>
  </customElement>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
Placeholders resolve at deploy; see [../../pricing-wiring/SKILL.md](../../pricing-wiring/SKILL.md). [Repo]

## Shipped in this repo (snapshot)
| Procedure | Step group | What it does |
|---|---|---|
| Default, Recalc, PRM_DISTI | `Applybundlebasedadjustments` (seq 2) | Bundle-based adjustment per component |

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

## Open questions
- Root selling model parameter name: Help says `RootItemProductSellingModel`, XML uses
  `RootProductSellingModel`; confirm which tag exists in your context definition.
