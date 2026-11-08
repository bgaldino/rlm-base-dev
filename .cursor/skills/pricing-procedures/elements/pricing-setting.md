# Pricing Setting (`PricingSettings`)

> Release 264 / API v68.0. Sources: `ind.pricing_pricing_setting.htm`,
> `ind.pricing_map_context_tags_in_pricing_procedures.htm` (parent);
> `meta_expressionsetdefinition.htm` (dev guide); shipped XML:
> `RLM_DefaultPricingProcedure`, `RLM_PRM_DISTI_Pricing_Procedure`,
> `RLM_Revenue_Management_Recalc_Procedure`, `RLM_Price_Distribution_Procedure`,
> `RLM_ProductDiscoveryPricingProcedure`. Parameter names and rules cross-checked against core [Core].

Binds the procedure's common variables (line item id, currency, contract, price
waterfall, net unit price, subtotal) to context tags. Every other element reads and
writes these variables.

## When to use it

- Always. It is the first element of every pricing procedure. [Help]
- Discovery procedures use **Discovery Settings** (`DiscoverySettings`) instead, not this element. [Help: `ind.pricing_map_line_item_element.htm`]
- Rating procedures use `RatingSetting` (different element, different variables).

## Configuration

| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Line Item (input) | `LineItemId` | Parameter (input) | Yes [Core] | Variable usually named `LineItem` [Help]. `RLM_ProductDiscoveryPricingProcedure` binds a `PricingId` variable instead [Repo] |
| Currency (input) | `CurrencyIsoCode` | Parameter (input) | Optional | Exposed only in multicurrency orgs [Core]; not in the Help walkthrough; mapped in 3 of the 5 shipped procedures (not `RLM_PRM_DISTI_Pricing_Procedure` or `RLM_ProductDiscoveryPricingProcedure`) [Repo]. Downstream lookups read this variable |
| Is Derived (input) | `IsDerived` | Parameter (input, Boolean) | Derived pricing only | Exposed only for users with derived-pricing access [Core]. Variable `DerivedPricingAttribute` [Help: `ind.pricing_calculate_the_derived_price_of_product.htm`, Repo] |
| Contract (input) | `ContractId` | Parameter (input) | Optional | Variable `ItemContract` [Repo] |
| Price Waterfall (output) | `PriceWaterfall` | Parameter (output, Text) | Optional [Core] | Variable `price_water_fall` [Help]; needed for the waterfall to show |
| Net Unit Price (output) | `NetUnitPrice` | Parameter (output, Currency) | Yes [Core] | Variable `NetUnitPrice` [Help] |
| Subtotal (output) | `Subtotal` | Parameter (output, Currency) | Yes [Core] | Variable `ItemNetTotalPrice` [Help] |
| Price propagation | `IsPropagationEnabled` | Literal | Shipped | `false` in every shipped procedure [Repo] |
| Real time | `IsRealTime` | Literal | Shipped | `false` [Repo] |
| Section count | `sectionCount` | Literal | Shipped | `0` [Repo] |
| Function | `selectedFunction` | Literal | Shipped | `Get` [Repo] |

The literal rows (`IsPropagationEnabled`, `IsRealTime`, `sectionCount`, `selectedFunction`) are not formal parameters in core; they are Builder-managed housekeeping [Core]. Core declares exactly four formal inputs (`LineItemId` required; `CurrencyIsoCode`, `IsDerived`, `ContractId` optional) and three formal outputs (`PriceWaterfall` optional Text; `NetUnitPrice` and `Subtotal` required Currency) [Core]. The Help article lists only the line item, waterfall, net unit price and total price mappings [Help]. `IsPropagationEnabled` is read at save time: when it is `true`, the procedure must contain a Price Propagation element, and when a Price Propagation element is present it must be `true` (both mismatches are save errors; the check is skipped if the procedure has more than one propagation element). Its runtime effect beyond this was not found in core [inferred]. See [price propagation](./price-propagation.md).

The Parameter `value` is the **procedure variable name** (a resource defined in the
procedure), not the context tag. The tag mapping lives on the variable's definition
in the Expression Set version (inferred from the Help wording "map common variables
to context tags").

## Placement and ordering

- First top-level step (`sequenceNumber` 1) in every shipped pricing procedure. [Repo]
- Enforced at save time: a missing or late Pricing Settings step is rejected with `Add Pricing Setting as the first element in the pricing procedure.` and a second one with `You can only add one Pricing Setting element in a pricing procedure.` [Core: message text read in the label file]. The exemption for a procedure made only of Discount Distribution Service (optionally with Rounding and Aggregate) steps, and for a lone Commerce step, is [Core] (see [the anatomy table](../procedure-anatomy-and-ordering.md)); the walk order (steps sorted by parent and sequence) was not re-read, so treat the exact boundary as [inferred].
- The repo's offline validator also requires the first top-level step to be `PricingSettings`. [Repo: `tasks/expression_set_schema.py`]
- Core also uses the first Pricing Settings step's `LineItemId` binding to check that group-by/line-item tags share the line item's hierarchy. [Core] Keep it first: every element depends on its variables, and the Builder and Help require it. [Help]
- Help: "serves as the initial element for any pricing procedure". [Help]
- [Map Line Item](./map-line-item.md), when used, goes second, immediately after this element. [Help]
- Cross-element ordering: [procedure anatomy and ordering](../procedure-anatomy-and-ordering.md).

## Rules and limits

- Variable names above are conventions; the Help examples and the shipped pricing procedures use the same names (the discovery pricing procedure binds `PricingId` and `SubTotal`, see the table), and downstream elements (List Price, Manual Discount, Aggregate Price) are wired to them. Renaming forces re-mapping everywhere. [Help, Repo]
- `IsDerived` and `ContractId` mappings are only needed when the procedure uses [derived pricing](./derived-price.md) or contract-based [List Price](./list-price.md). Shipped RLM_DefaultPricingProcedure maps both even though it omits derived pricing. [Repo]
- The Derived Price element cannot be used in a procedure that has Promotion Execution, Price Propagation or Discount Distribution Service. [Help: `ind.pricing_get_ready_to_calculate_the_derived_price.htm`] Keep `IsPropagationEnabled=false` when using derived pricing.
- When price waterfall is enabled, `price_water_fall` must be mapped in both Pricing Setting and Map Line Item (when used). [Help: `ind.pricing_map_context_tags_in_pricing_procedures.htm`]

## Metadata shape

```xml
<steps>
    <actionType>PricingSettings</actionType>
    <customElement>
        <parameters><input>true</input><name>LineItemId</name><output>false</output><type>Parameter</type><value>LineItem</value></parameters>
        <parameters><input>true</input><name>CurrencyIsoCode</name><output>false</output><type>Parameter</type><value>CurrencyIsoCode</value></parameters>
        <parameters><input>true</input><name>IsDerived</name><output>false</output><type>Parameter</type><value>DerivedPricingAttribute</value></parameters>
        <parameters><input>true</input><name>ContractId</name><output>false</output><type>Parameter</type><value>ItemContract</value></parameters>
        <parameters><input>true</input><name>sectionCount</name><output>false</output><type>Literal</type><value>0</value></parameters>
        <parameters><input>true</input><name>selectedFunction</name><output>false</output><type>Literal</type><value>Get</value></parameters>
        <parameters><input>true</input><name>IsRealTime</name><output>false</output><type>Literal</type><value>false</value></parameters>
        <parameters><input>true</input><name>IsPropagationEnabled</name><output>false</output><type>Literal</type><value>false</value></parameters>
        <parameters><input>false</input><name>PriceWaterfall</name><output>true</output><type>Parameter</type><value>price_water_fall</value></parameters>
        <parameters><input>false</input><name>NetUnitPrice</name><output>true</output><type>Parameter</type><value>NetUnitPrice</value></parameters>
        <parameters><input>false</input><name>Subtotal</name><output>true</output><type>Parameter</type><value>ItemNetTotalPrice</value></parameters>
    </customElement>
    <description>Pricing Setting</description>
    <label>Map context tags to common pricing variables</label>
    <name>Mapcontexttagstocommonpricingvariables</name>
    <resultIncluded>false</resultIncluded>
    <sequenceNumber>1</sequenceNumber>
    <stepType>BusinessKnowledgeModel</stepType>
</steps>
```

Inputs carry `input=true/output=false`; outputs the reverse. [Repo] Literals are
always input-side.

## Shipped in this repo (snapshot)

| Procedure | Step name | Notes |
|---|---|---|
| RLM_DefaultPricingProcedure | `Mapcontexttagstocommonpricingvariables` | seq 1; LineItem, Currency, IsDerived, ItemContract |
| RLM_PRM_DISTI_Pricing_Procedure | `Mapcontexttagstocommonpricingvariables` | seq 1; no `CurrencyIsoCode`; IsDerived `DerivedPricingAttribute`, ContractId `ItemContract` |
| RLM_Revenue_Management_Recalc_Procedure | `Mapcontexttagstocommonpricingvariables` | seq 1 |
| RLM_Price_Distribution_Procedure | `PricingSetting` | seq 1; `LineItemId` bound to `LineItem`; Currency mapped; no `IsDerived`/`ContractId` |
| RLM_ProductDiscoveryPricingProcedure | `PricingSetting` | seq 1; `LineItemId` bound to `PricingId`; Subtotal bound to `SubTotal`; no Currency/`IsDerived`/`ContractId` |

All five are top-level at sequence 1 and set `IsPropagationEnabled=false`. No shipped procedure uses `DiscoverySettings`. [Repo]

Snapshot. Discover with
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify

- Simulate in Builder: the output JSON has `price_water_fall`, `NetUnitPrice`, `ItemNetTotalPrice` populated after the last element. [Help]
- If any output is empty after a later element ran, check this step's output bindings first.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Waterfall empty / no `price_water_fall` | Output `PriceWaterfall` unmapped | Map to the waterfall variable |
| Lookups ignore currency | `CurrencyIsoCode` not mapped here or not passed to the lookup | Map it, then see [List Price](./list-price.md) |
| Contract price never applies | `ContractId` unmapped | Map `ItemContract`; see List Price contract section |
| Derived price skipped | `IsDerived` unmapped, so `DerivedPricingAttribute` is null | Map it |

## Feasibility / not supported

- Exactly one Pricing Setting per pricing procedure, ordered before every other step: zero, two or more, or a late one fail the save (messages above). [Core]
- Not valid in discovery procedures (use Discovery Settings) or rating procedures (`RatingSetting`). [Help, Repo]
- Price Propagation is not compatible with Derived Pricing, Map Line Item or Promotions elements. [Help] Core checks Derived Price, Promotion Execution (not `GPMPromotionExecution`) and Map Line Item, and allows only one propagation element, not inside a list container. [Core]

## Open questions

- Runtime effect of `IsPropagationEnabled` beyond the save-time coupling is not traced in core. Searched the pricing save validation and knowledge-model code only.
