# Volume Discount (`VolumeDiscount`) and Tier Discount (`VolumeTierDiscount`)

> Release 264 / API v68.0. Sources: `ind.pricing_add_volume_discount_element.htm`
> and its child articles (tier difference, cumulative, tiers, schedules, sequential
> example), `ind.qocal_manage_sequencing_for_tiered_volume_discounts.htm`,
> `ind.qocal_use_tiered_volume_and_pricing_in_contract_pricing.htm`,
> `ind.pricing_perform_pricing_adjustment_batch_job.htm`,
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
- Not for attribute, bundle or free-form conditions: use [attribute-based-price.md](./attribute-based-price.md),
  [bundle-based-price.md](./bundle-based-price.md) or [price-adjustment-matrix.md](./price-adjustment-matrix.md).

### Volume vs tier, worked example (Help)
Help example: 25 laptops, list price $200. Tiers: 1-9 none, 10-19 10% off,
20-29 15% off. [Help `ind.pricing_add_tier_discount_element.htm`]

| Element | Calculation | Total |
|---|---|---|
| Tier | (9 x $200) + (10 x $180) + (6 x $170) | $4,620 |
| Volume (inferred, same tiers) | 25 units all fall in the 20-29 band: 25 x $170 | $4,250 |

Help's volume statement: buying 60 with a threshold at 40 prices all 60 at the lower
rate. [Help] The volume row above is derived arithmetic, not a Help figure.

## Configuration
Builder fields map to the parameters below (Volume names are from shipped XML;
Tier names are from core's element registration, no Tier step ships in this repo).

| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Lookup table | `LookUpName`, `LookUpApiName`, `LookUpId` | Literal | Yes | Shipped: `Volume Discount Entries` / `Price_Adjustment_Tier_Decision_Table`; contract variant `Contract Pricing Volume Tiers` / `Contract_Pricing_Volume_Tiers`. [Repo] |
| Price Adjustment Schedule (rule var) | `PriceAdjustmentScheduleId` | Parameter | Non-contract step | Constant resource holding the schedule id (`VolumePASIdConstant`, placeholder `__VOLUMEPasID__`). [Repo] |
| Product | `Product2Id` (non-contract) / `ItemId` (contract) | Parameter | Yes | `Product`. Shipped non-contract steps use `Product2Id`, contract steps `ItemId`. [Repo] |
| Product Selling Model | `ProductSellingModelId` | Parameter | Yes | |
| Lower Bound / Upper Bound | `LowerBound`, `UpperBound` | Parameter | Yes | Both mapped to `LineItemQuantity` (Help maps both to quantity; with Use Cumulative Pricing map both to `AggregatedQuantity_std`). [Repo][Help] |
| Effective From / To | `EffectiveFrom`, `EffectiveTo` (non-contract); `StartDate`, `EndDate` (contract) | Parameter | Yes | `EffectiveDate` / `PricingDate`. [Repo] |
| Currency | `CurrencyIsoCode` | Parameter | Multi-currency | Shipped in the default procedure only. [Repo] |
| Tier type / value column | `TierTypeField`, `TierValueField` | Parameter | Both steps | Constants naming the table's type/value columns (`Constant_TierType_<table>_VD`, `Constant_TierValue_<table>_VD`). [Repo] |
| Tier type / value (output) | `TierType`, `TierValue` | Parameter, `input=false`, `output=true` | No | Outputs, shipped only in the Recalc procedure, written to `AdjustmentType`, `AdjustmentValue`. [Repo] |
| Quantity | `Quantity` | Parameter | Yes | |
| Input Unit Price | `InputUnitPrice` | Parameter | Yes | Previous `NetUnitPrice`. [Repo] |
| Contract id | `Id` | Parameter | Contract step | `ItemPricingContract` (default procedure) or `ItemContract` (PRM, Recalc). [Repo] |
| Contract enabled | `IsContractEnabled` | Literal | Yes | `true` on the contract step, `false` otherwise. [Repo] |
| Output: net unit price, subtotal | `NetUnitPrice`, `Subtotal` | Parameter (output) | Yes | |
| Output: contracted flag | `IsContracted` | Parameter (output) | Contract step | [Repo] |
| Cumulative Tier Quantity (Tier) | `CumulativeTierQuantity` | Parameter | Only when Use Cumulative Pricing is on | Numeric input, mapped to the aggregated-quantity tag. Present only when cumulative pricing is enabled for the step. [Core][Help] |
| Hide in waterfall | `HideWaterfall` | Literal | Yes | `false` = shown. Not Include in Output (that is the step field `resultIncluded`). [Repo] |
| Tier Discount: result columns | `TierTypeField`, `TierValueField`, `LowerBoundField`, `UpperBoundField` | Parameter | Optional in core (defaults to column names `LowerBound`/`UpperBound` when the bound constants are absent) | Registered as text parameters; constants naming the lookup's type/value/lower/upper columns (Volume registers only the first two). [Core] |
| Tier Discount: lookup | `Tiered_Adjustment_Tier_Decision_Table` ("Tiered Adjustment Entries") | | | Recipe lookup over Price Adjustment Tier: inputs `PriceAdjustmentScheduleId`, `Product2Id`, `ProductSellingModelId`, `EffectiveFrom`, `EffectiveTo`, `CurrencyIsoCode` (multi-currency); outputs `TierType`, `TierValue`, `LowerBound`, `UpperBound`. No quantity conditions, so every band returns. Volume's table adds `LowerBound`/`UpperBound` as inputs. [inferred]; only the table name is [Repo: `cumulusci.yml`] |
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
- Output Resolution is supported only on List Price, Price Tracking and Price Adjustment
  Matrix, and its Stack/Sequence strategies only on the matrix [Help
  `ind.pricing_procedure_output_resolution.htm`]. It is **not** available on Volume or
  Tier Discount (or Attribute-Based Price). When several stacked adjustments must
  combine on one line, use a Price Adjustment Matrix with a Stack or Sequence
  resolution ([`price-adjustment-matrix.md`](price-adjustment-matrix.md)).
- Volume Discount needs exactly one matching row per line; a second match errors
  `DUPLICATE_VALUE_FOUND_IN_LOOKUP`, so fix the overlapping rows. [Core] Tier Discount
  pricing each band the quantity spans at its own rate is normal [Help], not an
  ambiguous match; overlapping bounds are the error there
  (`OVERLAPPING_ADJUSTMENT_TIERS`). [Core]
- "Best price" selection (e.g. `MIN(ListPrice)` on List Price across price books) is
  a List Price resolution strategy, not element order. [Help
  `ind.pricing_example_calculate_the_lowest_price_of_a_product.htm`]

## Rules and limits
- Tier bounds are inclusive and must not overlap; same-effective-date tiers must be
  consecutive with no gaps. [Help] Schedule and tier setup: [`../../pricing-setup/price-adjustment-schedules.md`](../../pricing-setup/price-adjustment-schedules.md).
- No duplicate tier rows for one Product + Selling Model + Schedule + Currency +
  effective range. [Help]
- Tiers must belong to a price adjustment schedule of type Volume; you cannot create
  standalone tiers. Help: deactivate the schedule before adding records, reactivate after. [Help]
  On 264 any tier write fails while the schedule is active and tiers on an inactive schedule
  still price, so this repo leaves "Standard Price Adjustment Tier" inactive; don't activate it. [Repo, measured]
  The block is deliberate: tier changes (add, remove, bound edits) are refused while the parent
  schedule is active [Platform behaviour, traced]. Bundle-Based Adjustment rows have no such check
  ([`bundle-based-price.md`](./bundle-based-price.md)).
- Tier type: Percentage, Amount (Help: a flat amount, for example US$100) or Override
  (Help: when the amount falls outside the pricing policy's rule). [Help] Amount subtracts
  from the unit price, per [Core] below. Percentage is entered as a whole number (10 for
  10%). [Help, matrix article]
- Adjustment Method on the schedule: Range (same discount for all) or Slab (different
  discounts by condition, for example 10% for the first 10 items, 15% for 11-20). Schedule
  Type: Volume, Attribute or Bundle. No Effective To means indefinite. Editing price
  details creates another record. [Help: `ind.pricing_create_price_adjustment_schedules.htm`]
- Contract tiers (Contract Pricing Volume Tiers table; refresh it): set each new tier's
  Lower Bound equal to the previous tier's Upper Bound; the upper bound quantity is priced
  exclusively at run time. [Help: `ind.qocal_use_tiered_volume_and_pricing_in_contract_pricing.htm`]
- Contract tier sequencing: lines are sorted by quantity by default; a field named in the
  Revenue Settings "Cumulative Quantity Pricing Sort Order Tag Configuration" (a context
  tag) overrides it, reps enter sequence numbers from 1, and partial or no numbers fall
  back to quantity. [Help: `ind.qocal_manage_sequencing_for_tiered_volume_discounts.htm`]
- Bulk edits: Pricing Adjustment Batch Jobs take up to 200 records per batch, one job at a
  time; schedule records need effective dates; logs exist only for failed or partial jobs.
  [Help: `ind.pricing_perform_pricing_adjustment_batch_job.htm`]
- Cumulative: aggregated quantity comes from `AggregatedQuantity_std` (Volume) or the
  Cumulative Tier Quantity input (Tier); on real orders/assets it needs a pricing
  contract with aggregation strategy Cumulative; Simulate can use it without a
  contract. [Help] Example: past 6 + current 2 = 8 units, so a 5-10 band's 10% applies to
  the 2 current units; Tier cumulative 3 fills the 1-3 band first, current 6 spreads on.
- [Core] Tier calc: bands are sorted and walked from the lowest; a lower bound of 0 is
  treated as 1; each band's quantity is priced at that band's adjusted unit price;
  net unit price = total / line quantity; a null upper bound is open ended;
  overlapping tiers log `OVERLAPPING_ADJUSTMENT_TIERS` (the error is recorded and the
  walk continues); cumulative quantity is added to the line quantity, fills the lowest
  bands first, and contributes zero price.
- [Core] Tier gaps: quantity not covered by any band (a gap between bands, or above the
  last bounded band) is priced at the input unit price, with no error. Help requires
  consecutive tiers; core does not enforce it.
- [Core] Tier with quantity 0: no price change, empty waterfall entry. Cumulative
  enabled but no `CumulativeTierQuantity` value: no price change, empty waterfall entry.
- [Core] The Tier calculation does not branch on the schedule's Adjustment Method (Range or Slab). The Tier lookup carries no quantity conditions and returns all bands; the model reads only each row's type, value and bounds and always prices band by band. No Slab/Range handling was found in the lookup or Tier layers; it appears only in a separate contract-pricing path.
- [Core] Volume (`VolumeDiscount`) uses the generic single-outcome path: exactly one
  matching row (zero rows: no change, `IsContracted` false; two or more: error).
  Override replaces unit price, Amount subtracts from the input unit price, Percentage
  multiplies by (100 - v)/100. Type matching is case-insensitive and accepts the
  schedule values (Percentage, Amount, Override) and the equivalent adjustment enum
  values. A blank type or null value in the matched row leaves the price unchanged
  with no error.
- [Core] No clamping or rounding in either element: an Amount larger than the unit
  price, or a Percentage above 100, produces a negative price. Round with a Rounding
  Values step ([rounding-values.md](./rounding-values.md)).
- [Core] A null input unit price with Amount or Percentage fails with `INVALID_INPUT`;
  Override still works.
- [Core] Tier type matching is case-sensitive (exact `Override`/`Amount` strings); any other type value is priced as a Percentage, with no error. Volume matches case-insensitively and errors `INVALID_INPUT` on an unrecognised type.

### Feasibility / not supported
| Question | Answer |
|---|---|
| Cumulative quantity across quotes or orders? | Supported only through a pricing contract with aggregation strategy Cumulative (asset-based aggregate), or Simulate input. No cross-quote sum otherwise. [Help] |
| Two Volume rows matching one line? | Not supported: `DUPLICATE_VALUE_FOUND_IN_LOOKUP`. The Builder does not offer Output Resolution here. [Core] |
| Choose Range vs Slab to change Tier math? | No effect found in the Tier element: it always prices band by band. Verify live before relying on Range behaviour. [Core][inferred] |
| Slab-style (graduated) pricing with Volume? | No: Volume prices the whole quantity at one row. Use Tier Discount. [Core] |
| Different rate per band with Tier? | Yes, each band has its own type and value (mixing Percentage, Amount and Override across bands works). [Core] |
| Open-ended top band? | Yes: leave Upper Bound empty on the Tier table. [Core] |
| Key a tier lookup on a line custom field? | Add the field as a lookup input column mapped to a context tag; inputs are dynamic from the decision table. [Core][inferred] |

## Metadata shape
```xml
<steps>
  <actionType>VolumeDiscount</actionType>
  <customElement>
    <parameters><input>true</input><name>PriceAdjustmentScheduleId</name><output>false</output><type>Parameter</type><value>VolumePASIdConstant</value></parameters>
    <parameters><input>true</input><name>Product2Id</name><output>false</output><type>Parameter</type><value>Product</value></parameters>
    <parameters><input>true</input><name>ProductSellingModelId</name><output>false</output><type>Parameter</type><value>ProductSellingModel</value></parameters>
    <parameters><input>true</input><name>LowerBound</name><output>false</output><type>Parameter</type><value>LineItemQuantity</value></parameters>
    <parameters><input>true</input><name>UpperBound</name><output>false</output><type>Parameter</type><value>LineItemQuantity</value></parameters>
    <parameters><input>true</input><name>InputUnitPrice</name><output>false</output><type>Parameter</type><value>NetUnitPrice</value></parameters>
    <parameters><input>true</input><name>LookUpApiName</name><output>false</output><type>Literal</type><value>Price_Adjustment_Tier_Decision_Table</value></parameters>
    <parameters><input>true</input><name>LookUpId</name><output>false</output><type>Literal</type><value>__LOOKUPID_PRICE_ADJUSTMENT_TIER_DECISION_TABLE__</value></parameters>
    <!-- plus EffectiveFrom/EffectiveTo, Quantity, CurrencyIsoCode (Default only), optional outputs TierType/TierValue (Recalc only),
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
`cumulusci.yml`). `__LOOKUPID_*__` are likewise deploy-time; Recalc ships literal ids. [Repo]

## Re-banding positive amendment adds (overlay)

As shipped, units added on an amendment do not re-band. Assets carry `PricingSource`
`LastTransaction`; every non-contract new-sale group in the shipped default filters on
`ItemPricingSource NotEquals 'LastTransaction'`, and the last-transaction lane prices those lines
from the asset's last net price. Skipping the volume and discount steps for last-transaction lines is
by design in the shipped procedure [Platform behaviour, traced]; a line takes that lane when its pricing
source is last transaction, which the amend hook sets for a cancel, for a quantity of zero or less on an
amend or no-change line, and when the asset or an ancestor asset carries that source (what sets the
asset's own source was not traced). The volume step also bands on `LineItemQuantity`
[Repo: `RLM_DefaultPricingProcedure`], which on an amendment line is the delta, not the new total.
On a procedure cloned from the shipped default, which has the same lanes, added units took the
asset's last net price, with no volume step [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch
org]. The amendment flow itself is in
[`../../asset-lifecycle-changes/SKILL.md`](../../asset-lifecycle-changes/SKILL.md).

A source rule like "added units price at the band for the new total; existing units keep their
price" needs an overlay. Define a positive add on an existing asset as
`LineItemQuantity > 0 AND ItemStartQuantity > 0` (`ItemStartQuantity` and `ItemEndQuantity` are
standard tags from the line's `StartQuantity` and `EndQuantity`), then:

| Steps (shipped default names) | Change to the filter's condition logic |
|---|---|
| Every group whose filter has `ItemPricingSource NotEquals 'LastTransaction'` (criterion `k`), except the contract volume group `Applyvolumebaseddiscountstolineswithcontractandwithoutderivedpricing`: input unit price, item net total, both attribute groups, bundle, non-contract volume, manual and amount/percentage discounts, plus any custom group with the same exclusion | `k` → `(k OR (LineItemQuantity > 0 AND ItemStartQuantity > 0))`: positive adds take the new-sale chain |
| The last-transaction filters `SetNetUnitPriceforLastTransactionPricing` (under `ListContainer`) and `Filterlineswithlasttransactionpricing` (under `Filterlineswithlasttransactionpricingandassignnettotalprice`) | Their `ItemPricingSource Equals 'LastTransaction'` criterion `k` → `(k AND (LineItemQuantity <= 0 OR ItemStartQuantity IsNull OR ItemStartQuantity <= 0))`: positive adds leave the last-price lane |
| The non-contract volume step `Calculatenetunitpriceandnettotalpriceaftervolumebaseddiscount` | `LowerBound` and `UpperBound` → `ItemEndQuantity`, the quantity after the change (equal to the line quantity on a new sale); `Quantity` stays `LineItemQuantity` |

Leave the other contract-pricing paths and price revision unchanged. One of the two attribute
groups (`Setattributebasedpricingforlineswithoutderivedpricing`) is itself a contract path, since
it requires `IsContracted` true; the measured overlay changed it with the rest. Each filter change adds criteria
and rewrites the logic; filter mechanics are in
[`list-group-and-list-operation.md`](list-group-and-list-operation.md).

Measured on a procedure cloned from the shipped default that also carried other custom groups (a
rounding step and a term discount), with this overlay merged last
[Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]:

- The added units took the new-sale chain and priced at the band for the new total: the waterfall
  showed the volume step's bounds at the total and its quantity at the delta. The order activated. On the asset the existing units kept their price and the added
  units carried the new one.
- A reduction still credited last in, first out, at the prior prices.
- A renewal stayed on per-lot last prices: renewal lines have `StartQuantity` 0, so the new filters
  don't admit them.
- A new sale priced exactly as before the change, and a new sale at a band edge priced at the
  expected bands.

Know before adopting it:

- Positive adds also pass the manual-discount groups and any custom new-sale group with the same
  exclusion (a term discount, for example), like new units on a new sale.
- The volume step's `customElement` carries the org's own decision-table `LookUpId` and schedule
  constant, so generate the overlay from each org's export instead of shipping a static one
  ([`../../expression-sets/authoring-and-overlays.md`](../../expression-sets/authoring-and-overlays.md)).
- Not measured: an amendment that adds a product the asset didn't have, contract-priced assets,
  and other currencies.

## Shipped in this repo (snapshot)
| Procedure | Step (parent group) | What it does |
|---|---|---|
| RLM_DefaultPricingProcedure, RLM_Revenue_Management_Recalc_Procedure, RLM_PRM_DISTI_Pricing_Procedure | `...volume...contract and without derived pricing` (VolumeDiscount, seq 2) | Contract volume tiers (`Contract_Pricing_Volume_Tiers`), sets `IsContracted` |
| same | `...volume...without contract or last trxn pricing` (VolumeDiscount, seq 2) | Standard schedule tiers (`Price_Adjustment_Tier_Decision_Table`) |
| any | `VolumeTierDiscount` | none shipped |

Snapshot only. Discover live: `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify
- Simulate in Builder with quantity inside and outside each band; waterfall shows the
  volume/tier step. [Help]
- Persisted line: check `NetUnitPrice`/`TotalPrice` on the quote line and, for contract
  tiers, the contracted flag. Refresh the tier decision table first
  (`../../decision-tables/SKILL.md`).

## Troubleshooting
| Symptom / error | Cause | Fix |
|---|---|---|
| No discount | Tier table stale, tier on a schedule no procedure reads (`PriceAdjustmentScheduleId` constant), or selling model/date outside tier | Refresh the decision table; check the schedule id constant. Don't activate the repo's Tier schedule: inactive tiers still price on 264 and an active schedule blocks tier loads [Repo] |
| `DUPLICATE_VALUE_FOUND_IN_LOOKUP` | More than one matching Volume row for the line | Remove the overlapping rows; Output Resolution is not available on this element [Core][Help] |
| `OVERLAPPING_ADJUSTMENT_TIERS` | Overlapping bounds | Fix bounds [Core] |
| Cumulative ignored | Contract aggregation not Cumulative | Set strategy; check `AggregatedQuantity_std` mapping [Help] |

## Open questions
Tier parameter names match core's registration but no live Builder export exists; confirm on a live org before hand-authoring a Tier step. Whether `TierTypeField`/`LowerBoundField` are Constant resources (as with Volume) is inferred.
