# Map Line Item (`BreakdownLineMapping`)

> Release 264 / API v68.0 (actionType available from API v64.0, [Dev guide]
> `meta_expressionsetdefinition.htm`). Sources: `ind.pricing_map_line_item_element.htm`,
> `ind.pricing_map_line_item_limits.htm`,
> `ind.qocal_advanced_detail_line_pricing_for_custom_and_derived_products.htm`,
> `ind.qocal_advanced_line_pricing_map_line_json_task.htm`; shipped XML:
> `RLM_DefaultPricingProcedure`; overlay `datasets/expression_set_overlays/map_line_item.json`.
> Parameter names and parsing rules cross-checked against core [Core].

Copies values from a line item (`SalesTransactionItem`) to its detail items
(`SalesTransactionItemDetail`) so per-detail amounts, dates and custom fields are
priced and persisted. Used for Advanced Detail Line Pricing.

## When to use it

- Advanced Detail Line Pricing: amend, renew, cancel (ARC) transactions with detail lines, and custom fields on line or detail items. [Help]
- Mapping variables at line level and sub-line (detail) level in pricing and discovery procedures. [Help]
- Do not use for general-purpose calculation or just to persist values: it degrades pricing performance. [Help limits]
- Do not combine with delta pricing in the same use case. [Help limits]

## Configuration

Each mapping is a **section**: one input variable paired with one output tag.

| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Source node | `MapLineItemNodeInput` | Parameter (input, context node) | Yes [Core] | `SalesTransactionItem` [Repo, Help JSON] |
| Target node | `MapLineItemNodeOutput` | Parameter (output, context node) | Yes [Core] | `SalesTransactionItemDetail` [Repo, Help JSON] |
| Section N input variable | `section-{N}-input1` | Parameter (input) | Per section | N is 0-based. Value is a procedure variable name |
| Section N output tag | `section-{N}-output` | Parameter (output) | Per section | Detail-node tag, e.g. `ItemDetailQuantity`. Stored as `input:true`, `output:false` Parameters in both the shipped XML and the overlay [Repo] |
| Section N pairing | `sectionJsonString{N+1}` | Literal | Per section | 1-based suffix. JSON `whereConditions` pairing the two (below) |
| Section count | `sectionCount` | Literal | Yes | Number of sections, e.g. `18` |

`sectionJsonString{K}` value (K = N+1):

```json
{"whereConditions":[{"field":{"dataType":"Currency","name":"section-2-input1","value":"NetUnitPrice","allowCompatibleDataTypes":true},"value":{"dataType":"Currency","name":"section-2-output","value":"ItemDetailNetUnitPrice","allowCompatibleDataTypes":true}}]}
```

`dataType` must match the tag type (Text, Numeric, Currency, DateTime, Boolean). [Help JSON]
Note the off-by-one: `section-0-*` pairs with `sectionJsonString1`.

[Core] Formal parameters are built by reading `sectionJsonString1`, `2`, `3` ... consecutively until the first missing index (a gap silently drops every later section; `sectionCount` is not what drives it). Each `whereConditions` entry registers its `field.name` and `value.name` as formal parameters, typed from `dataType`. Both sides land in the step's input set, which is why `section-N-output` is stored with `input:true` in shipped XML. Unparseable JSON fails the build with `Error processing JSON`. Keep `sectionCount` equal to the number of strings anyway.

### The 18 standard sections (Help JSON, also the shipped overlay)

| N | Input variable | Output tag |
|---|---|---|
| 0 | `LineItem` | `SalesTrxnItemDetailSource` |
| 1 | `LineItemQuantity` | `ItemDetailQuantity` |
| 2 | `NetUnitPrice` | `ItemDetailNetUnitPrice` |
| 3 | `price_water_fall` | `DetailPriceWaterfallIdentifier` |
| 4 | `InputUnitPrice` | `ItemDetailUnitPrice` |
| 5 | `ItemBillingReference` | `ItemDetailBillingReference` |
| 6 | `ItemNetTotalPrice` | `ItemDetailTotalPrice` |
| 7 | `TotalLineAmount` | `ItemDetailTotalLineAmount` |
| 8-9 | `EffectiveFrom`, `EffectiveTo` | `ItemDetailEffectiveFrom__std`, `ItemDetailEffectiveTo__std` |
| 10 | `PricingTermCount` | `ItemDetailPricingTermCount__std` |
| 11 | `itemTransientEndDate` | `ItemDetailTransientEndDate__std` |
| 12 | `ItemPricingSource` | `ItemDetailPricingSource__std` |
| 13 | `DerivedPricingAttribute` | `ItemDetailDerivedPricingAttribute__std` |
| 14 | `ItemGroupSummarySubtotal` | `ItemDetailGroupSummaryTotal__std` |
| 15 | `ListPrice` | `ItemDetailListPrice__std` |
| 16 | `IsContracted` | `ItemDetailIsContracted__std` |
| 17 | `ItemContractPrice` | `ItemDetailContractPrice__std` |

Custom fields: append one section (e.g. `STI_TenantName__c` to `STID_TenantName__c`)
and raise `sectionCount`. [Help]

## Placement and ordering

- Second element, immediately after Pricing Setting (or Discovery Settings in a discovery procedure). [Help]
- Use an [Assignment](./assignment.md) element after it to initialize the tags it maps. [Help limits]
- Disable **parallel execution** on the procedure; the element does not support it. [Help limits]
- Overlay form: `placement.afterStep = Mapcontexttagstocommonpricingvariables`. [Repo]
- Behavior: if a detail item exists the value is written to the detail, otherwise to the line item. Map line-to-detail; never write the custom detail field directly. [Help limits]

## Rules and limits

- Org setting **Advanced Detail Line Pricing** must be on (Revenue Settings; metadata `enableAdvancedDetailLinePricing`, set true in `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`). [Help, Repo]
- Custom fields: add to quote line item/detail and order product/detail, add to both context nodes, create `QuoteEntitiesMapping` and `OrderEntitiesMapping` entries, then the section. Detail custom fields on QuoteLineItem/OrderProduct additionally need Procedure Plan Orchestration for Pricing plus an Apex handler (Help gives an example). [Help]
- Asset State Period / Asset Action Source custom fields need cross-context mappings. [Help]
- Help limits page says the element "doesn't support derived pricing", while the Advanced Detail Line Pricing article configures a derived-pricing **discovery** procedure with Discovery Settings plus Map Line Item (`LineItem`, `EffectiveFrom`, `EffectiveTo`, `DerivedPricingAttribute`). Read as: not in a derived-pricing **pricing** procedure; discovery use is documented. Inferred; confirm live.
- Mapping count limits: 70 by default, 100 max (`ind.pricing_limits.htm`; table in
  [`../runtime-and-observability.md`](../runtime-and-observability.md) → *Pricing limits*). [Help]
- Author `sectionJsonStringN` **unescaped** in Connect payloads. Documented UI path is paste of the JSON. See [expression-sets](../../expression-sets/SKILL.md) "Map Line Item - special case".

## Metadata shape

```xml
<steps>
    <actionType>BreakdownLineMapping</actionType>
    <customElement>
        <parameters><input>true</input><name>MapLineItemNodeInput</name><output>false</output><type>Parameter</type><value>SalesTransactionItem</value></parameters>
        <parameters><input>true</input><name>section-0-input1</name><output>false</output><type>Parameter</type><value>LineItem</value></parameters>
        <!-- section-1-input1 ... section-17-input1, section-0-output ... section-17-output -->
        <parameters><input>true</input><name>sectionCount</name><output>false</output><type>Literal</type><value>18</value></parameters>
        <parameters><input>true</input><name>sectionJsonString1</name><output>false</output><type>Literal</type><value>{"whereConditions":[...]}</value></parameters>
        <!-- sectionJsonString2 ... sectionJsonString18 -->
        <parameters><input>false</input><name>MapLineItemNodeOutput</name><output>true</output><type>Parameter</type><value>SalesTransactionItemDetail</value></parameters>
    </customElement>
    <label>Map Line Item to Detail Item</label>
    <name>MapLineItemtoDetailItem</name>
    <stepType>BusinessKnowledgeModel</stepType>
</steps>
```

In XML the JSON string is entity-escaped; the Connect API needs it unescaped.

## Shipped in this repo (snapshot)

| Procedure | Step | What it does |
|---|---|---|
| RLM_DefaultPricingProcedure | `MapLineItemtoDetailItem` | 18 sections, line to detail; also shipped as overlay `map_line_item.json` (`afterStep` Pricing Setting) |

PRM DISTI, Recalc and Price Distribution procedures do not ship it. Discover with
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify

- Simulate on an ARC transaction with detail lines; confirm `SalesTransactionItemDetail` tags (`ItemDetailNetUnitPrice`, `DetailPriceWaterfallIdentifier`) are populated. Simulation on a plain new sale only fills line-level values.
- Query the persisted detail record fields after a quote save (inferred: `QuoteLineItemDetail` / `OrderItemDetail`).

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Detail fields stay null | Setting off, or element not second | Enable Advanced Detail Line Pricing; reposition |
| Errors or wrong order in parallel runs | Parallel execution on | Disable it on the procedure |
| Custom field not saved on detail | Written directly to detail tag | Map line field to detail field instead |
| Mapping rejected | `dataType` mismatch, or `sectionCount` != sections | Match types; recount |
| Slow pricing | Element used for logic/persistence | Limit to standard mapping |

## Open questions

- Derived pricing relationship (see Rules): discovery use is documented; derived-pricing **pricing** procedure use is unconfirmed. Live check needed.
