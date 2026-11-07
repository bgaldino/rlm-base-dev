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
| Header Discount Type | `DiscountType` | Parameter | yes | Values Amount, Percentage, Override. [Help] Shipped: `HeaderDiscountType`. |
| Header Discount Value | `DiscountValue` | Parameter | yes | `HeaderDiscountValue`. |
| Header Distribution Logic | `SpreadLogic` | Parameter | yes | Equal or Proportionate (proportional to list price). Shipped: `AdjustmentDistributionLogic__std`. [Help][Repo] |
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
| Output: remainder | `TotalRemainderAmount` | Parameter, output | optional | Currency tag. Declared as an optional output; map it when `RemainderAllowed=true`. [Core] |
| Eligible line items: conditions | `where-condition-count`, `condition-K-input`, `condition-K-operator`, `condition-K-output-data`, `condition-K-input-data-type` | Literal / Parameter | no | Same condition parameters and operators as Aggregate Price (`greaterThan`, `lessThan`, `equalTo`, `notEqualTo`, `isNull`, `isNotNull`, `isTrue`, `isFalse`); see [aggregate-price.md](./aggregate-price.md). Empty = all lines. [Core][Help] |
| Eligible line items: lookup table | Builder lookup selection | | no | The element also takes a lookup table whose columns become extra input parameters; their names come from the table. [Core] |

## Placement and ordering

- Must be the last pricing element; Rounding Values and Aggregate Price are the only elements allowed after it. [Help] Both statements stand together: the tail is DDS, then aggregates/rounding. [Repo]
- Attempting to add DDS after those, or a formula after the aggregate tail, yields `You can add the Discount Distribution Service element only before the Rounding Rules and Aggregate elements`. [Repo]
- Aggregates must follow DDS because DDS rewrites `NetUnitPrice`/`ItemNetTotalPrice`. See [aggregate-price.md](./aggregate-price.md) and [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).
- The header-discount ListGroups (amount, percentage, price override) sit before DDS and set `HeaderDiscountType`/value from record fields. [Repo]

## Rules and limits

| Rule | Source |
|---|---|
| Use once per procedure. | [Help] |
| Do not map Is Derived; derived products on lines unsupported. | [Help] |
| Floor prices apply only when the distribution type is `NetUnitPrice`; unapplied amount goes to the next eligible line, then `TotalRemainderAmount`. | [Help] |
| Uses only `NetUnitPrice`, not Proration/Subscription's `LineItemSubTotal`. For total subscription price, compute `ProrationMultiplier * NetUnitPrice` in a Formula and feed it as Input Unit Price. | [Help] |
| Amend/renew assume `NetUnitPrice * Quantity = ItemNetTotal`; a discount applied to `ItemNetTotal` does not recompute `NetUnitPrice` (one-time discount). | [Help] |
| Floor limits come from the context definition or a custom object hydrated via Context Service. | [Help] |

## Metadata shape

Shipped step (parameters trimmed to name/type/value). All inputs `input=true`;
the five outputs `output=true`.

```xml
<steps>
  <actionType>DiscountDistributionService</actionType>
  <customElement>
    <parameters><name>DiscountType</name><type>Parameter</type><value>HeaderDiscountType</value></parameters>
    <parameters><name>DiscountValue</name><type>Parameter</type><value>HeaderDiscountValue</value></parameters>
    <parameters><name>SpreadLogic</name><type>Parameter</type><value>AdjustmentDistributionLogic__std</value></parameters>
    <parameters><name>InputSpreadType</name><type>Parameter</type><value>Constant_DDS_NetUnitPrice</value></parameters>
    <parameters><name>ListPrice</name><type>Parameter</type><value>NetUnitPrice</value></parameters>
    <parameters><name>InputUnitPrice</name><type>Parameter</type><value>NetUnitPrice</value></parameters>
    <parameters><name>Quantity</name><type>Parameter</type><value>LineItemQuantity</value></parameters>
    <parameters><name>LineItemId</name><type>Parameter</type><value>LineItem</value></parameters>
    <parameters><name>HeaderSubtotal</name><type>Parameter</type><value>TotalAmount</value></parameters>
    <parameters><name>LineFloorPrice</name><type>Parameter</type><value>MinimumNetUnitPrice</value></parameters>
    <parameters><name>FloorPricingEnabled</name><type>Literal</type><value>false</value></parameters>
    <parameters><name>RemainderAllowed</name><type>Literal</type><value>false</value></parameters>
    <parameters><output>true</output><name>SpreadValue</name><type>Parameter</type><value>LineItemDiscountValue</value></parameters>
    <parameters><output>true</output><name>SpreadType</name><type>Parameter</type><value>HeaderDistributionType</value></parameters>
    <parameters><output>true</output><name>LineItemDiscountType</name><type>Parameter</type><value>LineItemDiscountType</value></parameters>
    <parameters><output>true</output><name>NetUnitPrice</name><type>Parameter</type><value>NetUnitPrice</value></parameters>
    <parameters><output>true</output><name>Subtotal</name><type>Parameter</type><value>ItemNetTotalPrice</value></parameters>
  </customElement>
  <name>DiscountDistributionService</name>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```

`Constant_DDS_*` are version-level Constants (`type: Constant`, Text) that the
steps reference; ship them in `addVariables` (they are inputs, not step
outputs). [Repo] Enabling floors: set `FloorPricingEnabled=true` and
`RemainderAllowed=true`, map `LineFloorPrice`, and add a `TotalRemainderAmount` output parameter. [Core]

## Shipped in this repo (snapshot)

| Where | What |
|---|---|
| `datasets/expression_set_overlays/discount_distribution.json` on `RLM_DefaultPricingProcedure_V1` | 3 ListGroups (`ListApplyAmountBasedHeaderDiscount`, `ApplyPercentageBasedHeaderDiscount`, `ApplyHeaderPriceOverride`), each with an AdvancedListFilter and an AssignmentElement setting `HeaderDiscountType` from `Constant_DDS_Amount`/`Percentage`/`Override`; then `DiscountDistributionService` placed `afterStep: ApplyHeaderPriceOverride`; ships 4 constants `Constant_DDS_Amount`, `_NetUnitPrice`, `_Override`, `_Percentage`. |
| `RLM_DefaultPricingProcedure` | Same block in the base procedure (seq 39). |
| `RLM_Price_Distribution_Procedure` (`unpackaged/post_procedureplans`) | DDS plus the same three header ListGroups. |

Snapshot only. Discover live:
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify

1. Simulate with header discount type/value/logic set: Help scenario = $300 spread across two lines, then Equal versus Proportionate. [Help]
2. Floors: set `HeaderDiscountValue` above what floors allow; the surplus appears in the remainder tag. [Help]
3. Check each line's `NetUnitPrice` and `ItemNetTotalPrice` and that their sum equals `TotalAmount`.

## Troubleshooting

| Symptom / error | Cause | Fix |
|---|---|---|
| Null `NetUnitPrice` in waterfall | `InputUnitPrice` not mapped | Map it [Help] |
| `...only before the Rounding Rules and Aggregate elements` | DDS (or a formula) misplaced relative to the tail | Reorder [Repo] |
| Floors ignored | Distribution type is not `NetUnitPrice` | Use `NetUnitPrice` [Help] |
| Subscription total not discounted | DDS reads `NetUnitPrice` only | Pre-multiply in a Formula [Help] |
| Amend/renew totals off | One-time discount semantics | Expected [Help] |

## Open questions

- Exact value strings accepted by `DiscountType`, `SpreadLogic` and `InputSpreadType` (set via the shipped Constants): copy from the shipped overlay; not enumerated here.

## Disagreements resolved

- Help names the Builder variables `HeaderDistributionLogic` / `HeaderDiscountType`; metadata parameters are `SpreadLogic` / `DiscountType` (core formal parameters confirm `DiscountType`, `DiscountValue`, `SpreadLogic`, `InputSpreadType`, `ListPrice`, `Quantity`, `LineItemId`, optional `InputUnitPrice`, `HeaderSubtotal`, `LineFloorPrice`). Core and shipped XML win; Help is Builder labels.
