# Volume Discount (`VolumeDiscount`) and Tier Discount (`VolumeTierDiscount`)

> Release 264 / API v68.0. Sources: `ind.pricing_add_volume_discount_element.htm`,
> `ind.pricing_add_tier_discount_element.htm`,
> `ind.pricing_calculate_cumulative_discounts_for_volume_and_tier.htm`,
> `ind.pricing_calculate_volume_or_tiered_discounts_with_cumulative_pricing.htm`,
> `ind.pricing_create_price_adjustment_tiers_volume_discounts.htm`,
> `ind.pricing_price_adjustment_schedules_salesforce_pricing.htm`,
> `ind.pricing_create_price_adjustment_schedules.htm`,
> `ind.pricing_example_apply_discounts_sequentially_for_a_product.htm`,
> `ind.pricing_determine_the_best_price_using_a_pricing_procedure.htm`;
> `meta_expressionsetdefinition.htm` (actionType enum); shipped XML: Volume
> Discount only; core source (behavior only).

Both elements look up quantity-banded price adjustment tiers (a decision table over
Price Adjustment Tier records) and reduce the unit price. Volume gives one rate to
the whole quantity; Tier prices each quantity band at its own rate.

## When to use it
- Volume Discount: one reduced per-unit price once a threshold is reached. [Help]
- Tier Discount: progressive pricing across quantity bands in one purchase. [Help]
- Contract-negotiated volume/tier pricing: set `IsContractEnabled` and pass the
  pricing contract id (`Id`). [Repo]
- Not for attribute, bundle or free-form conditions: use
  [attribute-based-price.md](./attribute-based-price.md),
  [bundle-based-price.md](./bundle-based-price.md) or
  [price-adjustment-matrix.md](./price-adjustment-matrix.md).

### Volume vs tier, worked example (Help)
Help example: 25 laptops, list price $200. Tiers: 1-9 none, 10-19 10% off,
20-29 15% off. [Help `ind.pricing_add_tier_discount_element.htm`]

| Element | Calculation | Total |
|---|---|---|
| Tier | (9 x $200) + (10 x $180) + (6 x $170) | $4,620 |
| Volume (inferred, same tiers) | 25 units all fall in the 20-29 band: 25 x $170 | $4,250 |

Arithmetic re-checked: 1,800 + 1,800 + 1,020 = 4,620; 25 x 170 = 4,250.

Help's own volume statement: buying 60 with a threshold at 40 prices all 60 at the
lower rate. [Help] The volume row above is derived arithmetic, not a Help figure.

## Configuration
Builder fields map to the parameters below (Volume names are from shipped XML;
Tier names are from core, no Tier step ships in this repo).

| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Lookup table | `LookUpName`, `LookUpApiName`, `LookUpId` | Literal | Yes | Shipped: `Volume Discount Entries` / `Price_Adjustment_Tier_Decision_Table`; contract variant `Contract Pricing Volume Tiers` / `Contract_Pricing_Volume_Tiers`. [Repo] |
| Price Adjustment Schedule (rule var) | `PriceAdjustmentScheduleId` | Parameter | Non-contract step | Constant resource holding the schedule id (`VolumePASIdConstant`, placeholder `__VOLUMEPasID__`). [Repo] |
| Product | `ProductNId` (non-contract) / `ItemId` (contract) | Parameter | Yes | `Product`. [Repo] |
| Product Selling Model | `ProductSellingModelId` | Parameter | Yes | |
| Lower Bound / Upper Bound | `LowerBound`, `UpperBound` | Parameter | Yes | Both mapped to `LineItemQuantity` (Help maps both to quantity; with Use Cumulative Pricing map both to `AggregatedQuantity_std`). [Repo][Help] |
| Effective From / To | `EffectiveFrom`, `EffectiveTo` (non-contract); `StartDate`, `EndDate` (contract) | Parameter | Yes | `EffectiveDate` / `PricingDate`. [Repo] |
| Currency | `CurrencyIsoCode` | Parameter | Multi-currency | |
| Tier type / value column | `TierTypeField`, `TierValueField` | Parameter | Contract step | Constants naming the table's type/value columns. [Repo] |
| Tier type / value | `TierType`, `TierValue` | Parameter | Non-contract step | Mapped to `AdjustmentType`, `AdjustmentValue`. [Repo] |
| Quantity | `Quantity` | Parameter | Yes | |
| Input Unit Price | `InputUnitPrice` | Parameter | Yes | Previous `NetUnitPrice`. [Repo] |
| Contract id | `Id` | Parameter | Contract step | `ItemPricingContract`. [Repo] |
| Contract enabled | `IsContractEnabled` | Literal | Yes | `true` on the contract step, `false` otherwise. [Repo] |
| Output: net unit price, subtotal | `NetUnitPrice`, `Subtotal` | Parameter (output) | Yes | |
| Output: contracted flag | `IsContracted` | Parameter (output) | Contract step | [Repo] |
| Cumulative Tier Quantity (Tier) | `CumulativeTierQuantity` | Parameter | Only when Use Cumulative Pricing is on | Numeric input, mapped to the aggregated-quantity tag. Present only when cumulative pricing is enabled for the step. [Core][Help] |
| Include in Output / waterfall | `HideWaterfall` | Literal | Yes | `false` = shown. [Repo] |
| Tier Discount: tier type / value columns | `TierTypeField`, `TierValueField` | Parameter | Yes | Constants naming the table's type/value columns (same names as the contract Volume step). [Core] |
| Tier Discount: bound columns | `LowerBoundField`, `UpperBoundField` | Parameter | Yes | Constants naming the table's lower/upper bound columns; distinct from Volume's `LowerBound`/`UpperBound` inputs. [Core] |
| Tier Discount: fixed inputs | `Quantity`, `InputUnitPrice` | Parameter | Yes | Plus one input per decision-table input column (dynamic, from the lookup). [Core] |
| Tier Discount actionType | `VolumeTierDiscount` | | | Builder "Tier Discount" element. Tier Discount supports lookup, cumulative pricing, contract pricing, hide-waterfall and profile filter. [Dev guide][Core] |
| Boilerplate | `sectionCount=0`, `selectedFunction=Get`, `IsRealTime=false` | Literal | Yes | [Repo] |

## Placement and ordering
- Shipped order in the Default procedure: List Price, input-price setup, attribute
  (17-18), bundle (19), **volume (20-21)**, manual (22-23), price revision (24).
  Each element's `InputUnitPrice` is the previous `NetUnitPrice`. [Repo]
- Each element sits inside its own ListGroup after an `AdvancedListFilter` step
  (seq 1), element at seq 2; the group filter selects which lines it applies to
  (contract vs non-contract). See [list-group-and-list-operation.md](./list-group-and-list-operation.md)
  and [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).
- Decision table must be refreshed after tier records change. [Help]

### Stacking, sequencing and the waterfall (shared by all discount elements)
- Default behavior is sequential: the first discount is computed from list price and
  each later discount applies to the already-discounted price. [Help
  `ind.pricing_example_apply_discounts_sequentially_for_a_product.htm`] In shipped
  XML this is the chain of `InputUnitPrice = NetUnitPrice` mappings. [Repo]
- Ordering is element order in the procedure; there is no separate priority field
  on these elements. [inferred from Repo]
- Each element writes `NetUnitPrice`/`Subtotal`; with `HideWaterfall=false` its step
  shows in the price waterfall (tier steps list each band with lower/upper bound,
  type, value and discounted price). [Repo][Core]
- Several matching rows for one element (e.g. many tiers/adjustments on one line)
  need Output Resolution: create a Procedure Output Resolution record
  (`SEQUENCE(<col>)` or `STACK`) and map Resolution Strategy and "Use As List"; the
  list column must have unique values per row. Without it a multi-row match errors
  `DUPLICATE_VALUE_FOUND_IN_LOOKUP`. [Help][Core] Core supports only SEQUENCE and
  STACK. [Core]
- "Best price" selection (e.g. `MIN(ListPrice)` on List Price across price books) is
  also a resolution strategy, not element order. [Help
  `ind.pricing_example_calculate_the_lowest_price_of_a_product.htm`]

## Rules and limits
- Tier bounds are inclusive and must not overlap; same-effective-date tiers must be
  consecutive with no gaps. [Help]
- No duplicate tier rows for one Product + Selling Model + Schedule + Currency +
  effective range. [Help]
- Tiers must belong to a price adjustment schedule of type Volume; you cannot create
  standalone tiers. Deactivate the schedule before adding records, reactivate after. [Help]
- Tier type: Percentage, Amount (flat per-unit deduction) or Override. [Help]
  Percentage is entered as a whole number (10 for 10%). [Help, matrix article]
- Adjustment Method on the schedule: Range (same discount for all) or Slab. [Help]
- Cumulative: aggregated quantity comes from `AggregatedQuantity_std` (Volume) or the
  Cumulative Tier Quantity input (Tier); on real orders/assets it needs a pricing
  contract with aggregation strategy Cumulative; Simulate can use it without a
  contract. [Help]
- [Core] Tier calc: bound of 0 is treated as 1; unit price = total / quantity; zero
  quantity yields an empty waterfall entry; tier with a null upper bound is open
  ended; overlapping tiers log `OVERLAPPING_ADJUSTMENT_TIERS`; cumulative quantity
  fills lowest bands first at zero contribution.
- [Core] Volume (`VolumeDiscount`) uses the generic single-outcome path: one matching
  row, else error; Override replaces unit price, Amount subtracts, Percentage
  multiplies by (100 - v)/100.

## Metadata shape
```xml
<steps>
  <actionType>VolumeDiscount</actionType>
  <customElement>
    <parameters><input>true</input><name>PriceAdjustmentScheduleId</name><output>false</output><type>Parameter</type><value>VolumePASIdConstant</value></parameters>
    <parameters><input>true</input><name>ProductNId</name><output>false</output><type>Parameter</type><value>Product</value></parameters>
    <parameters><input>true</input><name>ProductSellingModelId</name><output>false</output><type>Parameter</type><value>ProductSellingModel</value></parameters>
    <parameters><input>true</input><name>LowerBound</name><output>false</output><type>Parameter</type><value>LineItemQuantity</value></parameters>
    <parameters><input>true</input><name>UpperBound</name><output>false</output><type>Parameter</type><value>LineItemQuantity</value></parameters>
    <parameters><input>true</input><name>InputUnitPrice</name><output>false</output><type>Parameter</type><value>NetUnitPrice</value></parameters>
    <parameters><input>true</input><name>LookUpApiName</name><output>false</output><type>Literal</type><value>Price_Adjustment_Tier_Decision_Table</value></parameters>
    <parameters><input>true</input><name>LookUpId</name><output>false</output><type>Literal</type><value>__LOOKUPID_PRICE_ADJUSTMENT_TIER_DECISION_TABLE__</value></parameters>
    <!-- plus EffectiveFrom/EffectiveTo, Quantity, CurrencyIsoCode, TierType, TierValue,
         TierTypeField, TierValueField, LookUpName, IsContractEnabled=false,
         HideWaterfall, sectionCount, selectedFunction, IsRealTime -->
    <parameters><input>false</input><name>NetUnitPrice</name><output>true</output><type>Parameter</type><value>NetUnitPrice</value></parameters>
    <parameters><input>false</input><name>Subtotal</name><output>true</output><type>Parameter</type><value>ItemNetTotalPrice</value></parameters>
  </customElement>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
The `PriceAdjustmentScheduleId` constant resource is a procedure variable whose value is
`__VOLUMEPasID__` placeholder resolved at deploy by `find_replace` (see
[../../pricing-wiring/SKILL.md](../../pricing-wiring/SKILL.md) section B and
`cumulusci.yml`). `__LOOKUPID_*__` placeholders are likewise deploy-time. [Repo]

## Shipped in this repo (snapshot)
| Procedure | Step (parent group) | What it does |
|---|---|---|
| RLM_DefaultPricingProcedure, RLM_Revenue_Management_Recalc_Procedure, RLM_PRM_DISTI_Pricing_Procedure | `...volume...contract and without derived pricing` (VolumeDiscount, seq 2) | Contract volume tiers (`Contract_Pricing_Volume_Tiers`), sets `IsContracted` |
| same | `...volume...without contract or last trxn pricing` (VolumeDiscount, seq 2) | Standard schedule tiers (`Price_Adjustment_Tier_Decision_Table`) |
| any | `VolumeTierDiscount` | none shipped |

Snapshot only. Discover: `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify
- Simulate in Builder with quantity inside and outside each band; waterfall shows the
  volume/tier step. [Help]
- Persisted line: check `NetUnitPrice`/`TotalPrice` on the quote line and, for contract
  tiers, the contracted flag. Refresh the tier decision table first
  (`../../decision-tables/SKILL.md`).

## Troubleshooting
| Symptom / error | Cause | Fix |
|---|---|---|
| No discount | Tier table stale, schedule inactive, or selling model/date outside tier | Reactivate schedule, refresh decision table |
| `DUPLICATE_VALUE_FOUND_IN_LOOKUP` | More than one matching tier row, no Output Resolution | Remove overlap or add resolution strategy [Core] |
| `OVERLAPPING_ADJUSTMENT_TIERS` | Overlapping bounds | Fix bounds [Core] |
| Cumulative ignored | Contract aggregation not Cumulative | Set strategy; check `AggregatedQuantity_std` mapping [Help] |

## Open questions
- Tier Discount parameter names are from core, not a live Builder export; confirm on a
  live org before relying on them for a hand-authored step.
