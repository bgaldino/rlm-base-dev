# Derived Price (`DerivedPricing`)

> Release 264 / API v68.0. Sources: `ind.pricing_derived_price.htm`,
> `ind.pricing_calculate_the_derived_price_of_product.htm`,
> `ind.pricing_get_ready_to_calculate_the_derived_price.htm`,
> `ind.qocal_advanced_detail_line_pricing_for_custom_and_derived_products.htm`,
> `ind.qocal_set_up_add_derived_pricing_assets_to_a_quote_or_order.htm`,
> `ind.pricing_limits.htm`, `ind.pricing_add_aggregate_price_element.htm`,
> `ind.qocal_considerations_ramp_deals.htm`,
> `ind.qocal_consumer_price_index_and_uplifts_important_considerations.htm`;
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
- Derived pricing products do not support price uplifts [Help: `ind.qocal_consumer_price_index_and_uplifts_important_considerations.htm`]. Derived products added to a ramp deal for groups do not price correctly [Help: `ind.qocal_considerations_ramp_deals.htm`].

## Prerequisite chain (all required)

| Piece | Detail |
|---|---|
| Price book entries | Source product has a real list price; derived product list price is `0`, `Is Derived` selected. Same price book. [Help] |
| Derived Price record | Scope (Transactional, Non-transactional, Both), Pricing Source (Product or Header), derived product, source product (not needed for Header), `Formula` (e.g. `ListPrice * 0.10`), effective dates. [Help] |
| Decision tables | Refresh **Derived Pricing Entries** and **Price Book Entries V2**. Assetize Order permission set needed to refresh them. [Help] See [decision-tables](../../decision-tables/SKILL.md) |
| Discovery procedure | Usage Type **Pricing Discovery**; Fetch Pricing Rules element on Derived Pricing Entries; Asset Discovery element on Asset Action Source Entries V2 if assets are sources (delete it for purely transactional). Writes contributors into context. Cloning the Default Discovery Procedure: switch its decision table to Asset Action Source Entries V2 and map the new variables; or clone the Salesforce Pricing Discovery Procedure template. [Help] |
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
- Place [Aggregate Price](./aggregate-price.md) after Derived Price and add a Where condition targeting only the contributing lines; this keeps it consistent with Map Line Item in derived-pricing discovery procedures. [Help: `ind.pricing_add_aggregate_price_element.htm`]
- Downstream steps typically gate on `DerivedPricingAttribute`: shipped filters use `isNotNull` and `isFalse` conditions on `DerivedPricingAttribute` so non-derived lines get the normal discount stack, and a ListGroup "Set the net unit price for lines with derived pricing" assigns the derived result onward. [Repo]
- Cross-element ordering and the save-time combination rules (exact error text): [procedure anatomy and ordering](../procedure-anatomy-and-ordering.md#save-time-procedure-rules-core-enforces).

## Rules and limits

- Discount distribution cannot be applied to a procedure used for derived price. [Help]
- Map Line Item: the limits page says it "doesn't support derived pricing"; the advanced-detail article does document Map Line Item in a derived-pricing **discovery** procedure. See [Map Line Item](./map-line-item.md). [Help]
- Advanced Detail Line Pricing (Revenue Settings toggle) with derived pricing: besides the pricing procedure's Map Line Item (second element, after Pricing Setting), the discovery procedure needs a Discovery Settings element (Line Item to `LineItem`) and a Map Line Item mapping `SalesTransactionItem` to `SalesTransactionItemDetail`, plus `LineItem`, `EffectiveFrom`, `EffectiveTo` and `DerivedPricingAttribute` to their item-detail tags. This is required to find valid contributing and derived products. [Help: `ind.qocal_advanced_detail_line_pricing_for_custom_and_derived_products.htm`]
- Revenue Settings "Add Derived Pricing Assets to a Quote or Order" adds derived-product assets when contributing products are added. Future-dated amendments or renewals include contributing products but add derived products only if the request names them. [Help: `ind.qocal_set_up_add_derived_pricing_assets_to_a_quote_or_order.htm`]
- Derived and source products must share a price book. [Help]
- Header source needs no source product. [Help]
- Discovery output is not shown in the waterfall; simulate discovery only to write contributors to context. [Help]

### Runtime behavior and errors [Core]

- Each contributing child is evaluated in order; the first contributor error stops the
  line. Formula results of all contributors are summed into the net unit price; subtotal
  is that sum times the line quantity.
- Contributor handling by source: Product + Transactional reads the source line's priced
  values from the current run (a source line with its own error gives
  `CONTRIBUTING_LINE_HAS_ERROR`); Product + Non-transactional reads the contributor
  price tags written by discovery (all three empty gives `CONTRIBUTING_TAG_EMPTY`);
  Header requires an empty scope (else `SCOPE_SHOULD_BE_EMPTY`) and a header total
  (else code `CONTRIBUTING_TAG_EMPTY`, the same code as the non-transactional case).
  These codes surface prefixed `DPP: ` (for example `DPP: FORMULA_EMPTY`).
- Empty formula: `DPP: FORMULA_EMPTY`. A derived line with no contributors:
  `MISSING_CONTRIBUTORS` (no `DPP:` prefix; it also marks the waterfall response failed). Formula evaluation errors surface with the formula service's
  own code.
- The waterfall lists each contributor (source, scope, product, id, contributed price).
- Limits are per-org values, enforced at Derived Price save and again in discovery
  (runtime guardrail errors) [Core]. The 264 Help limits page publishes contributing
  products per derived product as 40 default, 1 minimum, 50 maximum (the total of transactional and non-transactional contributors), and assets per contributing asset as 50 maximum [Help: `ind.pricing_limits.htm`]; the same page caps a discovery procedure at 50 elements by default (100 maximum) and a discovery run at 10 seconds by default (60 maximum). Core's
  platform defaults are larger (contributing products 500, min 1, up to 2000; assets per
  product 100, up to 1000; source products per price book entry 3, up to 5) [Core].
  Design to the Help numbers; the effective value on an org can differ.
- [Core] Save-time rules (the procedure cannot be saved):
  - "You can’t have the Derived Price and Promotion Execution elements in the same pricing procedure. Delete one of them and try again."
  - "You can’t have the Derived Price and Discount Distribution Service elements in the same pricing procedure. Delete one of them and try again." So a derived-pricing procedure has no DDS; its aggregates follow Derived Price instead.
  - "You can only have one derived price element in a procedure."
  - "Map the Is Derived variable to a value in the Pricing Settings element if you want to add a Derived Pricing element to your procedure." Pricing Settings must come first.
  - "Pricing Propagation element is not allowed with incompatible elements in the pricing procedure." (one Price Propagation step with Derived Price, Promotion Execution or Breakdown Line Mapping.)
  - Communications, media, energy and utilities procedures: "You can't have the Derived Price and Advanced Promotion Execution elements in the same pricing procedure. Delete one of them and try again."
- [Core] Runtime guardrail messages: "The limit of {0} contributing products for a source product was reached."; "The limit of {0} assets for a contributing product was reached."; "We couldn’t add the source product because the limit of {0} source products associated with a derived product was reached. Delete a source product and try again."; "We can’t price your quote when contributing products are missing. Please add the contributing products to the transaction."
- Parallel execution: core has a general pricing-element parallel executor and a
  per-request override, but no Derived Price specific restriction was found.
- Cross-procedure: contributor prices reflect only the procedure the Derived Price
  step runs in. [Help `ind.pricing_procedure_plan_limits.htm`]
- Aggregate Price does not support derived products on quote lines [Help]: aggregate the contributing lines and exclude the derived ones (the Where conditions above).

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
- Behavior of the repo default procedure if derived pricing were re-added is untested.
