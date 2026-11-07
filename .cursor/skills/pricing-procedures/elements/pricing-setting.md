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
| Line Item (input) | `LineItemId` | Parameter (input) | Yes [Core] | Variable usually named `LineItem` [Help]. Some procedures bind a `PricingId` variable instead [Repo: Price_Distribution / ProductDiscovery] |
| Currency (input) | `CurrencyIsoCode` | Parameter (input) | Optional | Exposed only in multicurrency orgs [Core]; not in the Help walkthrough; shipped in every pricing procedure [Repo]. Downstream lookups read this variable |
| Is Derived (input) | `IsDerived` | Parameter (input, Boolean) | Derived pricing only | Exposed only for users with derived-pricing access [Core]. Variable `DerivedPricingAttribute` [Help: `ind.pricing_calculate_the_derived_price_of_product.htm`, Repo] |
| Contract (input) | `ContractId` | Parameter (input) | Optional | Variable `ItemContract` [Repo] |
| Price Waterfall (output) | `PriceWaterfall` | Parameter (output, Text) | Optional [Core] | Variable `price_water_fall` [Help]; needed for the waterfall to show |
| Net Unit Price (output) | `NetUnitPrice` | Parameter (output, Currency) | Yes [Core] | Variable `NetUnitPrice` [Help] |
| Subtotal (output) | `Subtotal` | Parameter (output, Currency) | Yes [Core] | Variable `ItemNetTotalPrice` [Help] |
| Price propagation | `IsPropagationEnabled` | Literal | Shipped | `false` in every shipped procedure [Repo] |
| Real time | `IsRealTime` | Literal | Shipped | `false` [Repo] |
| Section count | `sectionCount` | Literal | Shipped | `0` [Repo] |
| Function | `selectedFunction` | Literal | Shipped | `Get` [Repo] |

The literal rows (`IsPropagationEnabled`, `IsRealTime`, `sectionCount`, `selectedFunction`) are not formal parameters in core; they are Builder-managed housekeeping. Core defines exactly the six input/three output names above [Core]; no other optional parameters exist.

The Parameter `value` is the **procedure variable name** (a resource defined in the
procedure), not the context tag. The tag mapping lives on the variable's definition
in the Expression Set version (inferred from the Help wording "map common variables
to context tags").

## Placement and ordering

- First top-level step (`sequenceNumber` 1) in every shipped pricing procedure. [Repo]
- Not enforced as first by core: design-time validation locates the first Pricing Settings step anywhere in the version and reads its `LineItemId` binding to check that group-by/line-item tags share the line item's hierarchy. If no such step exists the check is skipped (no "must be first" error found). [Core] Keep it first anyway: every element depends on its variables, and the Builder and Help require it. [Help]
- Help: "serves as the initial element for any pricing procedure". [Help]
- [Map Line Item](./map-line-item.md), when used, goes second, immediately after this element. [Help]
- Cross-element ordering: [procedure anatomy and ordering](../procedure-anatomy-and-ordering.md).

## Rules and limits

- Variable names above are conventions; the Help examples and every shipped procedure use the same names, and downstream elements (List Price, Manual Discount, Aggregate Price) are wired to them. Renaming forces re-mapping everywhere. [Help, Repo]
- `IsDerived` and `ContractId` mappings are only needed when the procedure uses [derived pricing](./derived-price.md) or contract-based [List Price](./list-price.md). Shipped RLM_DefaultPricingProcedure maps both even though it omits derived pricing. [Repo]
- Price Propagation and the Derived Price element cannot coexist in a procedure. [Help: `ind.pricing_get_ready_to_calculate_the_derived_price.htm`] Keep `IsPropagationEnabled=false` when using derived pricing.

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
| RLM_PRM_DISTI_Pricing_Procedure | `Mapcontexttagstocommonpricingvariables` | seq 1 |
| RLM_Revenue_Management_Recalc_Procedure | `Mapcontexttagstocommonpricingvariables` | seq 1 |
| RLM_Price_Distribution_Procedure | `PricingSetting` | `LineItemId` bound to `PricingId` |
| RLM_ProductDiscoveryPricingProcedure | `PricingSetting` | `LineItemId` bound to `PricingId` |

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

## Open questions

- Runtime error text when the step is absent or not first: no dedicated message found in core. Needs a live org check.
