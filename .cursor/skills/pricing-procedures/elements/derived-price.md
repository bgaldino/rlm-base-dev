# Derived Price (`DerivedPricing`)

> Release 264 / API v68.0. Sources: `ind.pricing_derived_price.htm`,
> `ind.pricing_calculate_the_derived_price_of_product.htm`,
> `ind.pricing_get_ready_to_calculate_the_derived_price.htm`,
> `ind.qocal_advanced_detail_line_pricing_for_custom_and_derived_products.htm`;
> shipped XML: `RLM_PRM_DISTI_Pricing_Procedure`, `RLM_Revenue_Management_Recalc_Procedure`.
> Parameter names cross-checked against core [Core].

Computes a product's net unit price from another product, an asset, or the whole
transaction total, using a formula stored on a Derived Price record and contributor
data written to context by a discovery procedure.

## When to use it

- Price of product B is a formula of product A (for example 10 percent of a bundle), of an asset, or of the header total. [Help]
- Not for plain discounts: use Manual or Volume Discount.
- Not allowed with Promotion Execution, Price Propagation, or Discount Distribution Service elements in the same procedure. [Help]
- Not supported with compound ramp uplift. [Help]; see [price-revision-compound-uplift.md](./price-revision-compound-uplift.md)

## Prerequisite chain (all required)

| Piece | Detail |
|---|---|
| Price book entries | Source product has a real list price; derived product list price is `0`, `Is Derived` selected. Same price book. [Help] |
| Derived Price record | Scope (Transactional, Non-transactional, Both), Pricing Source (Product or Header), derived product, source product (not needed for Header), `Formula` (e.g. `ListPrice * 0.10`), effective dates. [Help] |
| Decision tables | Refresh **Derived Pricing Entries** and **Price Book Entries V2**. Assetize Order permission set needed to refresh them. [Help] See [decision-tables](../../decision-tables/SKILL.md) |
| Discovery procedure | Usage Type **Pricing Discovery**; Fetch Pricing Rules element on Derived Pricing Entries; Asset Discovery element on Asset Action Source Entries V2 if assets are sources (delete it for purely transactional). Writes contributors into context. [Help] |
| Same context definition | Discovery and pricing procedures must share it. [Help] |
| Line flag | Source line `DerivedPricingAttribute=false`; derived line `true`. [Help] |
| List Price element | Must use Price Book Entries V2 or a custom table. [Help] |

## Configuration

| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Quantity | `Quantity` | Parameter | Optional [Core] | `LineItemQuantity` |
| Contributing Net Unit Price | `ContributingNetUnitPrice` | Parameter | Yes | `ContributorUnitPrice` |
| Contributing Sub Total | `ContributingSubTotal` | Parameter | Yes | `ContributorTotalPrice` |
| Contributing Source | `ContributingSource` | Parameter | Yes | `ContributorSource` |
| Contributing Scope | `ContributingScope` | Parameter | Yes | `ContributorScope` |
| Transactional List Price | `TransactionalListPrice` | Parameter | Yes | `ListPrice` |
| Non-Transactional List Price | `Non-TransactionalListPrice` | Parameter | Yes | `ContributorListPrice` (parameter name has a hyphen) |
| Derived Formula | `DerivedFormula` | Parameter | Yes | `ContributorFormulaInput` |
| Contributor | `ContributingId` | Parameter | Yes | `Contributor` |
| Contributing Product | `ContributingProduct` | Parameter | Yes | `ContributorProduct` |
| Header Total | `HeaderTotal` | Parameter | Yes | `TotalAmount` |
| Output: Net Unit Price | `NetUnitPrice` | Parameter (output) | Yes | |
| Output: Subtotal | `Subtotal` | Parameter (output) | Yes | `ItemNetTotalPrice` |
| Housekeeping | `sectionCount`=`0`, `selectedFunction`=`Get`, `IsRealTime`=`false` | Literal | Shipped | |

All names and values [Repo], matching the Help walkthrough [Help]. Help also says to
select Include in Output.

[Core] All eleven inputs above are formal parameters of this element and **none is marked required** (the "Yes" column is Help/Repo practice: wire all of them). Types: `ContributingNetUnitPrice`, `ContributingSubTotal`, both list prices and `HeaderTotal` are Currency; `Quantity` Numeric; the rest Text. The element has no lookup table of its own (lookup disabled in Builder), so no `LookUp*` literals. Outputs `NetUnitPrice` and `Subtotal` are optional in core. Core also defines a `ContributingListPrice` tag name that this element does not take as a parameter.

## Placement and ordering

- After the base [List Price](./list-price.md) steps and [Pricing Setting](./pricing-setting.md) (which must map `IsDerived` to `DerivedPricingAttribute`). Shipped DISTI order: Pricing Setting (1), cost List Price (2), price book List Price (3), Derived Price (4). [Repo]
- Place [Aggregate Price](./aggregate-price.md) after Derived Price (Help ordering guidance per the Aggregate Price article; not restated in the Derived Price articles, so verify there).
- Downstream steps typically gate on `DerivedPricingAttribute`: shipped filters use `isNotNull` and `isFalse` conditions on `DerivedPricingAttribute` so non-derived lines get the normal discount stack, and a ListGroup "Set the net unit price for lines with derived pricing" assigns the derived result onward. [Repo]
- Cross-element ordering: [procedure anatomy and ordering](../procedure-anatomy-and-ordering.md).

## Rules and limits

- Discount distribution cannot be applied to a procedure used for derived price. [Help]
- Map Line Item: the limits page says it "doesn't support derived pricing"; the advanced-detail article does document Map Line Item in a derived-pricing **discovery** procedure. See [Map Line Item](./map-line-item.md). [Help]
- Derived and source products must share a price book. [Help]
- Header source needs no source product. [Help]
- Discovery output is not shown in the waterfall; simulate discovery only to write contributors to context. [Help]

## Metadata shape

```xml
<steps>
    <actionType>DerivedPricing</actionType>
    <customElement>
        <parameters><input>true</input><name>Quantity</name><output>false</output><type>Parameter</type><value>LineItemQuantity</value></parameters>
        <parameters><input>true</input><name>ContributingNetUnitPrice</name><output>false</output><type>Parameter</type><value>ContributorUnitPrice</value></parameters>
        <parameters><input>true</input><name>ContributingSubTotal</name><output>false</output><type>Parameter</type><value>ContributorTotalPrice</value></parameters>
        <parameters><input>true</input><name>ContributingSource</name><output>false</output><type>Parameter</type><value>ContributorSource</value></parameters>
        <parameters><input>true</input><name>ContributingScope</name><output>false</output><type>Parameter</type><value>ContributorScope</value></parameters>
        <parameters><input>true</input><name>TransactionalListPrice</name><output>false</output><type>Parameter</type><value>ListPrice</value></parameters>
        <parameters><input>true</input><name>Non-TransactionalListPrice</name><output>false</output><type>Parameter</type><value>ContributorListPrice</value></parameters>
        <parameters><input>true</input><name>DerivedFormula</name><output>false</output><type>Parameter</type><value>ContributorFormulaInput</value></parameters>
        <parameters><input>true</input><name>ContributingId</name><output>false</output><type>Parameter</type><value>Contributor</value></parameters>
        <parameters><input>true</input><name>ContributingProduct</name><output>false</output><type>Parameter</type><value>ContributorProduct</value></parameters>
        <parameters><input>true</input><name>HeaderTotal</name><output>false</output><type>Parameter</type><value>TotalAmount</value></parameters>
        <parameters><input>true</input><name>sectionCount</name><output>false</output><type>Literal</type><value>0</value></parameters>
        <parameters><input>true</input><name>selectedFunction</name><output>false</output><type>Literal</type><value>Get</value></parameters>
        <parameters><input>true</input><name>IsRealTime</name><output>false</output><type>Literal</type><value>false</value></parameters>
        <parameters><input>false</input><name>NetUnitPrice</name><output>true</output><type>Parameter</type><value>NetUnitPrice</value></parameters>
        <parameters><input>false</input><name>Subtotal</name><output>true</output><type>Parameter</type><value>ItemNetTotalPrice</value></parameters>
    </customElement>
    <description>Derived Price</description>
    <label>Calculate Net Unit Price from Related Product or Asset</label>
    <name>Calculatethenetunitpricebasedonthepriceofanotherproductorasset</name>
    <stepType>BusinessKnowledgeModel</stepType>
</steps>
```

## Shipped in this repo (snapshot)

| Procedure | Step | Notes |
|---|---|---|
| RLM_PRM_DISTI_Pricing_Procedure | `Calculatethenetunitpricebasedonthepriceofanotherproductorasset` (seq 4) | Derived Price after the two List Price steps |
| RLM_Revenue_Management_Recalc_Procedure | same name (seq 3) | |
| RLM_DefaultPricingProcedure | none | **Omitted by owner decision**; the 264 template includes it. The default procedure still maps `IsDerived` and filters on `DerivedPricingAttribute`. |

Snapshot. Discover with
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify

- Run the discovery procedure's Simulate with source and derived products; confirm contributors written to context. [Help]
- Simulate the pricing procedure with both lines; waterfall shows the derived line priced from the source. [Help]
- Check Derived Pricing Entries and Price Book Entries V2 are Fresh.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Derived line prices at 0 | No contributor in context (discovery not run, stale table, flag wrong) | Run discovery, refresh tables, check `DerivedPricingAttribute` true/false |
| Formula ignored | Derived Pricing Entries stale | Refresh decision tables |
| Procedure fails to save/run with promotions or distribution | Unsupported element combination | Remove Promotion Execution, Price Propagation or Discount Distribution Service |
| List Price returns nothing for derived item | Used Price Book Entries instead of V2 | Switch to V2 |

## Open questions

- Error text for an unsupported element combination is not in the formal-parameter definition; where it is enforced (save vs run) is unconfirmed.
- Behavior of the repo default procedure if derived pricing were re-added is untested.
