# Discount Distribution Service (`DiscountDistributionService`)

> Release 264 / API v68.0. Sources: `ind.pricing_discount_spread_service.htm`,
> `ind.pricing_use_the_discount_spread_service_element.htm`,
> `ind.pricing_understand_discount_distribution_service_terms.htm`,
> `ind.pricing_discount_distribution_service_limits.htm`; shipped XML:
> `RLM_DefaultPricingProcedure`, `RLM_Price_Distribution_Procedure`, overlay
> `datasets/expression_set_overlays/discount_distribution.json`; core source
> (behavior only).

Spreads a header (quote-level) discount, percentage or price override across
qualifying line items, equally or proportionally, optionally honoring per-line
floor prices and storing the undistributed remainder.

## When to use it

- Discretionary discount entered at quote/header level that must be reflected on each line for accounting. [Help]
- Floor price limits and product/category exclusions on that spread. [Help]
- Not for line-level discounts: use Manual Discount or the discount elements.
- Not for a procedure that computes a product's derived price. [Help]

## Configuration

| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Header Discount Type | `DiscountType` | Parameter | yes | Values `Amount`, `Percentage`, `Override` (case-insensitive). [Help][Core] Shipped: `HeaderDiscountType`. |
| Header Discount Value | `DiscountValue` | Parameter | yes | `HeaderDiscountValue`. |
| Header Distribution Logic | `SpreadLogic` | Parameter | yes | `Equal` or `Proportionate` (proportional to list price x quantity); ignored for `Percentage` [Core]. Shipped: `AdjustmentDistributionLogic__std`. [Help][Repo] |
| Header Distribution Type | `InputSpreadType` | Parameter | yes | Which field the discount comes off: `NetUnitPrice` or `ItemNetTotalPrice`. Shipped constant `Constant_DDS_NetUnitPrice`. |
| Header Subtotal | `HeaderSubtotal` | Parameter | for Override | Subtotal the target is deducted from. Shipped: `TotalAmount`. [Help][Repo] |
| List Price | `ListPrice` | Parameter | yes | Shipped: `NetUnitPrice`. |
| Input Unit Price | `InputUnitPrice` | Parameter | yes when Net Unit Price mapped | Omitting it returns an empty value and a null Net Unit Price in the waterfall. [Help] |
| Quantity | `Quantity` | Parameter | yes | `LineItemQuantity`. |
| Line Item | `LineItemId` | Parameter | yes | `LineItem`. |
| Minimum Net Unit Price | `LineFloorPrice` | Parameter | for floors | Currency tag, e.g. `MinimumNetUnitPrice`. [Help][Repo] |
| Set floor price limit | `FloorPricingEnabled` | Literal | yes | Shipped `false`. |
| Store remainder amount | `RemainderAllowed` | Literal | yes | Shipped `false`. Maps `TotalRemainderAmount` (currency) when on. [Help] |
| Output: discount value | `SpreadValue` | Parameter, output | yes | `LineItemDiscountValue`. |
| Output: distribution type | `SpreadType` | Parameter, output | yes | `HeaderDistributionType`. |
| Output: discount type | `LineItemDiscountType` | Parameter, output | yes | |
| Output: Net Unit Price | `NetUnitPrice` | Parameter, output | yes | |
| Output: Subtotal | `Subtotal` | Parameter, output | yes | `ItemNetTotalPrice`. |
| Output: remainder | `TotalRemainderAmount` | Parameter, output | optional | Currency tag. Map it when `RemainderAllowed=true`. [Help][inferred] |
| Eligible line items: conditions | `where-condition-count`, `condition-K-input`, `condition-K-operator`, `condition-K-output-data`, `condition-K-input-data-type` | Literal / Parameter | no | Same condition parameters and operators as Aggregate Price (`greaterThan`, `lessThan`, `equalTo`, `notEqualTo`, `isNull`, `isNotNull`, `isTrue`, `isFalse`); see [aggregate-price.md](./aggregate-price.md). Empty = all lines. [Help][inferred] |
| Eligible line items: lookup table | Builder lookup selection | | no | The element also takes a lookup table whose columns become extra input parameters; their names come from the table. [inferred] |

## Runtime behavior [Core]

- Eligible lines are those matching the where-conditions (or, with a lookup, those the lookup returns). The first eligible line's header tags (type, value, logic, spread type, subtotal) drive the whole spread.
- `Percentage`: the percent itself is written to each line's `SpreadValue`; nothing is divided.
- `Amount`: `Equal` = value / count of eligible lines; `Proportionate` = line list price x quantity x value / sum of eligible list-price totals. With `NetUnitPrice` spread type the line amount is divided by quantity. A zero total list price or zero quantity yields 0 for that line.
- `Override`: the amount spread is `HeaderSubtotal` minus `DiscountValue`, then spread like `Amount`.
- Line `NetUnitPrice` falls by the spread value (percent: by that percent). Lines whose `InputUnitPrice` is empty are left out of the price update.
- Floor-price handling runs only when `FloorPricingEnabled` and spread type `NetUnitPrice`; otherwise a plain spread. Rounding-remainder handling inside the floor path was not read: [inferred] from Help.
- Blank type or blank logic (for Amount/Override) makes the step do nothing silently.

## Placement and ordering

- Must be the last pricing element; Rounding Values and Aggregate Price are the only elements allowed after it. [Help] Both statements stand together: the tail is DDS, then aggregates/rounding. [Repo]
- Save-time check: any element after DDS other than Aggregate Price (`GroupingAndAggregatePricing`) or Rounding Values (`RoundingValues`) is rejected with the full message `You can add the Discount Distribution Service element only before the Rounding Rules and Aggregate elements or you can make it the only element in a pricing procedure.` A DDS that is the only element is also accepted. [Core][Repo]
- Other save-time errors for this element [Core]:
  - Second DDS: `You can use only one Discount Distribution Service element in a pricing procedure.`
  - DDS plus Derived Price: `You can’t have the Derived Price and Discount Distribution Service elements in the same pricing procedure. Delete one of them and try again.`
  - A DDS condition without a usable participating condition or lookup: `Add a valid participating condition or delete the condition in the Discount Distribution Service element.`
- Aggregates must follow DDS because DDS rewrites `NetUnitPrice`/`ItemNetTotalPrice`. See [aggregate-price.md](./aggregate-price.md) and [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).
- The header-discount ListGroups (amount, percentage, price override) sit before DDS and set `HeaderDiscountType`/value from record fields. [Repo]

## Rules and limits

| Rule | Source |
|---|---|
| Use once per procedure (second one rejected on save, message above). | [Help][Core] |
| Cannot coexist with Derived Price in one procedure (rejected on save). | [Core] |
| Without a lookup table or conditions, all input lines participate; a condition that is incomplete is rejected on save. | [Core] |
| Runtime line errors: `INVALID_SPREAD_TYPE`, `INVALID_DISCOUNT_TYPE`, `INVALID_SPREAD_LOGIC`, `NULL_SUBTOTAL_DSS` (Override with empty `HeaderSubtotal`). [Core] | [Core] |
| Line-item tags (list price, quantity, line id, input unit price, floor, outputs) coming from different context hierarchy nodes: a save-time check is suspected but its text was not read. | [inferred] |
| Do not map Is Derived; derived products on lines unsupported. | [Help] |
| Floor prices apply only when the distribution type is `NetUnitPrice`; unapplied amount goes to the next eligible line, then `TotalRemainderAmount`. | [Help] |
| Uses only `NetUnitPrice`, not Proration/Subscription's `LineItemSubTotal`. For total subscription price, compute `ProrationMultiplier * NetUnitPrice` in a Formula and feed it as Input Unit Price. | [Help] |
| Amend/renew assume `NetUnitPrice * Quantity = ItemNetTotal`; a discount applied to `ItemNetTotal` does not recompute `NetUnitPrice` (one-time discount). | [Help] |
| Floor limits come from the context definition or a custom object hydrated via Context Service. | [Help] |

## Metadata shape

Shipped step, flags as shipped: the inputs are `input=true`, `output=false`; the five
outputs are `input=false`, `output=true`. Write both flags: they default to true [Dev guide].

```xml
<steps>
  <actionType>DiscountDistributionService</actionType>
  <customElement>
    <parameters><input>true</input><name>DiscountType</name><output>false</output><type>Parameter</type><value>HeaderDiscountType</value></parameters>
    <parameters><input>true</input><name>DiscountValue</name><output>false</output><type>Parameter</type><value>HeaderDiscountValue</value></parameters>
    <parameters><input>true</input><name>SpreadLogic</name><output>false</output><type>Parameter</type><value>AdjustmentDistributionLogic__std</value></parameters>
    <parameters><input>true</input><name>InputSpreadType</name><output>false</output><type>Parameter</type><value>Constant_DDS_NetUnitPrice</value></parameters>
    <parameters><input>true</input><name>ListPrice</name><output>false</output><type>Parameter</type><value>NetUnitPrice</value></parameters>
    <parameters><input>true</input><name>InputUnitPrice</name><output>false</output><type>Parameter</type><value>NetUnitPrice</value></parameters>
    <parameters><input>true</input><name>Quantity</name><output>false</output><type>Parameter</type><value>LineItemQuantity</value></parameters>
    <parameters><input>true</input><name>LineItemId</name><output>false</output><type>Parameter</type><value>LineItem</value></parameters>
    <parameters><input>true</input><name>HeaderSubtotal</name><output>false</output><type>Parameter</type><value>TotalAmount</value></parameters>
    <parameters><input>true</input><name>LineFloorPrice</name><output>false</output><type>Parameter</type><value>MinimumNetUnitPrice</value></parameters>
    <parameters><input>true</input><name>FloorPricingEnabled</name><output>false</output><type>Literal</type><value>false</value></parameters>
    <parameters><input>true</input><name>RemainderAllowed</name><output>false</output><type>Literal</type><value>false</value></parameters>
    <parameters><input>false</input><name>SpreadValue</name><output>true</output><type>Parameter</type><value>LineItemDiscountValue</value></parameters>
    <parameters><input>false</input><name>SpreadType</name><output>true</output><type>Parameter</type><value>HeaderDistributionType</value></parameters>
    <parameters><input>false</input><name>LineItemDiscountType</name><output>true</output><type>Parameter</type><value>LineItemDiscountType</value></parameters>
    <parameters><input>false</input><name>NetUnitPrice</name><output>true</output><type>Parameter</type><value>NetUnitPrice</value></parameters>
    <parameters><input>false</input><name>Subtotal</name><output>true</output><type>Parameter</type><value>ItemNetTotalPrice</value></parameters>
  </customElement>
  <name>DiscountDistributionService</name>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```

`Constant_DDS_*` are version-level Constants (`type: Constant`, Text) that the
steps reference; ship them in `addVariables` (they are inputs, not step
outputs). [Repo] Enabling floors: set `FloorPricingEnabled=true` and
`RemainderAllowed=true`, map `LineFloorPrice`, and add a `TotalRemainderAmount` output parameter. [Help][inferred]

## Shipped in this repo (snapshot)

| Where | What |
|---|---|
| `datasets/expression_set_overlays/discount_distribution.json` on `RLM_DefaultPricingProcedure_V1` | 3 ListGroups (`ListApplyAmountBasedHeaderDiscount`, `ApplyPercentageBasedHeaderDiscount`, `ApplyHeaderPriceOverride`), each with an AdvancedListFilter and an AssignmentElement setting `HeaderDiscountType` from `Constant_DDS_Amount`/`Percentage`/`Override`; then `DiscountDistributionService` placed `afterStep: ApplyHeaderPriceOverride`; ships 4 constants `Constant_DDS_Amount`, `_NetUnitPrice`, `_Override`, `_Percentage`. |
| `RLM_DefaultPricingProcedure` | Top level, no parent: ListGroups seq 36 `ListApplyAmountBasedHeaderDiscount`, 37 `ApplyPercentageBasedHeaderDiscount`, 38 `ApplyHeaderPriceOverride`; `DiscountDistributionService` seq 39; then three `GroupingAndAggregatePricing` steps seq 40-42 (total amount, subtotal, item group subtotal). [Repo, checked] |
| `RLM_Price_Distribution_Procedure` (`unpackaged/post_procedureplans`) | Top level: `PricingSetting` seq 1, ListGroups 2 `AmountBasedHeaderDiscount`, 3 `PercentageBasedHeaderDiscount`, 4 `OverrideBasedHeaderDiscount`, `DiscountDistributionService` seq 5 (last; no aggregates). Same input bindings; outputs `SpreadValue`->`AdjustmentValue`, `LineItemDiscountType`->`AdjustmentType`. [Repo, checked] |
| PRM Disti, Recalc, `RLM_ProductDiscoveryPricingProcedure` and all other procedures | None. [Repo, checked: every procedure under `force-app`, `post_procedureplans`, `post_prm_pricing`] |

The metadata snippet above is the `RLM_DefaultPricingProcedure` step (top level, no condition).

Snapshot only. Discover live:
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify

1. Simulate with header discount type/value/logic set: Help scenario = $300 spread across two lines, then Equal versus Proportionate. [Help]
2. Floors: set `HeaderDiscountValue` above what floors allow; the surplus appears in the remainder tag. [Help]
3. Check each line's `NetUnitPrice` and `ItemNetTotalPrice` and that their sum equals `TotalAmount`.

## Troubleshooting

| Symptom / error | Cause | Fix |
|---|---|---|
| Line error `INVALID_SPREAD_TYPE` / `INVALID_DISCOUNT_TYPE` / `INVALID_SPREAD_LOGIC` | Bound value not an exact accepted string | Use `NetUnitPrice`/`ItemNetTotalPrice`, `Amount`/`Percentage`/`Override`, `Equal`/`Proportionate`; spread type and logic are matched case-sensitively, discount type is not [Core] |
| `NULL_SUBTOTAL_DSS` | Override without `HeaderSubtotal` | Map `HeaderSubtotal` [Core] |
| Spread silently skipped | Blank type/logic tag | Populate header tags [Core] |
| Null `NetUnitPrice` in waterfall | `InputUnitPrice` not mapped | Map it [Help] |
| `You can add the Discount Distribution Service element only before the Rounding Rules and Aggregate elements or you can make it the only element...` | A non-Aggregate, non-Rounding element follows DDS | Move the other element before DDS; don't move DDS down, because the aggregates must follow it [Core] |
| `You can use only one Discount Distribution Service element...` | Two DDS steps | Delete one [Core] |
| `You can’t have the Derived Price and Discount Distribution Service elements...` | Derived Price in the same procedure | Delete one [Core] |
| `Add a valid participating condition or delete the condition...` | Incomplete DDS condition | Complete or delete the condition [Core] |
| Floors ignored | Distribution type is not `NetUnitPrice` | Use `NetUnitPrice` [Help] |
| Subscription total not discounted | DDS reads `NetUnitPrice` only | Pre-multiply in a Formula [Help] |
| Amend/renew totals off | One-time discount semantics | Expected [Help] |

## Open questions

- Rounding remainder inside the floor path: not read in core.

## Disagreements resolved

- Help's example maps the distribution-type output to `LineItemDistributionType` and Input Unit Price to `ListPrice`; the repo binds `HeaderDistributionType` and `NetUnitPrice`.
- Help prerequisites: Pricing Setting with LineItem, `price_water_fall`, `NetUnitPrice`, `ItemNetTotalPrice` (no Is Derived), a List Price element first, permission Salesforce Pricing Design Time, Include in Output. Minimum Net Unit Price and Total Remainder Amount tags must be currency. [Help]
- Help names the Builder variables `HeaderDistributionLogic` / `HeaderDiscountType`; metadata parameters are `SpreadLogic` / `DiscountType` (core formal parameters confirm `DiscountType`, `DiscountValue`, `SpreadLogic`, `InputSpreadType`, `ListPrice`, `Quantity`, `LineItemId`, optional `InputUnitPrice`, `HeaderSubtotal`, `LineFloorPrice`). Core and shipped XML win; Help is Builder labels.
