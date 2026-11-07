# Price Tracking (`MinimumPrice`)

> Release 264 / API v68.0. Sources: `ind.pricing_price_tracking.htm`,
> `ind.pricing_price_tracking_actions.htm`,
> `ind.pricing_ensure_price_transparency_using_the_price_tracking_element.htm`,
> `ind.pricing_update_your_product_price_range_entries_decision_table.htm`,
> `ind.pricing_set_price_history_tracking.htm` (referenced); shipped XML: none;
> core source (behavior only).

Fetches and/or saves a product's historical minimum and maximum recorded price
for a product, selling model, price book and currency combination, so the
procedure can display or evaluate it.

## When to use it

- Price-transparency or regional-compliance display ("lowest price in last 30 days"). [Help]
- Not a price calculator: it does not change `NetUnitPrice`.

## actionType

Builder name is Price Tracking; the stored `actionType` is `MinimumPrice`
(registered with the Price Tracking icon) [Core]. `PriceGuidance` is a different element: input `ListPrice`; outputs ceiling, floor and target price plus three adjustment percentages; the Builder offers it only in orgs with a pilot enabled [Core]. Do not use it for tracking.

## Configuration

| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Lookup table | `LookUpName`, `LookUpApiName`, `LookUpId` | Literal | yes | Help picks Price Book Entries V2 in the example; core fixtures use a Product Price Range Entries table. Shipped-style `__LOOKUPID_*__` placeholders apply. [Help][Core] |
| Action Type | `selectedFunction` | Literal | yes | Stored values `Get`, `Save`, `Save and Get` (Builder constants; Help shows "Save & Get") [Core]. |
| Input: Product | `ProductId` | Parameter | yes | [Core] |
| Input: Price Book | `PricebookId` | Parameter | yes | [Core] |
| Input: Product Selling Model | per lookup table | Parameter | per Help | Inputs are generated from the lookup table's input columns, so the name is the column mapping you choose [Core] |
| Inputs for Save / Save and Get | tracked price, transaction date | Parameter | yes | Added only when `selectedFunction` is not `Get`; exact names unconfirmed [Core] |
| Output: Min recorded | `SavedRecordedPrice` | Parameter, output | | Absent when function is `Save`. Help label "Saved Min Recorded Price" (`ItemRecordedPrice`). [Help][Core] |
| Output: Max recorded | `MaxRecordedPrice`, `SavedMaxRecordedPrice` | Parameter, output | | `SavedMaxRecordedPrice` exists only when the org's highest-price-compliance preference is on and function is not `Save` [Core]. Help example maps `ItemMaxRecordedPrice_std`; core fixture uses `ItemMaxRecordedPrice__std`. [Help][Core] |
| (fixed) | `sectionCount`=`0`, `IsRealTime`, `IsOutputResolutionEnabled` | Literal | yes | As on lookup elements. [Core] |

## Placement and ordering

- Help example places it after List Price and Manual Discount, so it can record the final price. [Help]
- Whether it must precede or follow DDS and the aggregate tail: not stated. See [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).
- Top-level; the result is JSON-only (not in the waterfall). [Help]

## Rules and limits

| Rule | Source |
|---|---|
| Every run or simulation writes to Product Price History Log; per product/model/price book per day, the log keeps the top price (a larger price later that day replaces it). | [Help] |
| Product Price Range stores the min/max for the configured duration and is the source for Get / Save & Get. | [Help] |
| To rerun Get you must manually refresh the decision table. | [Help] |
| If maximum tracking is enabled in Price Tracking History settings but the Product Price Range Entries decision table lacks `MaxRecordedPrice`, the procedure fails at execution. | [Help] |
| New enablement with both min and max: use predefined Product Price Range Entries V2. | [Help] |

## Metadata shape

From a core test fixture (not shipped here; ids are placeholders):

```xml
<steps>
  <actionType>MinimumPrice</actionType>
  <customElement>
    <parameters><name>ProductId</name><type>Parameter</type><value>Product</value></parameters>
    <parameters><name>PricebookId</name><type>Parameter</type><value>PriceBooks</value></parameters>
    <parameters><name>LookUpName</name><type>Literal</type><value>__TRACKING_TABLE_NAME__</value></parameters>
    <parameters><name>LookUpApiName</name><type>Literal</type><value>__TRACKING_TABLE_API_NAME__</value></parameters>
    <parameters><name>LookUpId</name><type>Literal</type><value>__LOOKUPID_PRODUCT_PRICE_RANGE__</value></parameters>
    <parameters><name>sectionCount</name><type>Literal</type><value>0</value></parameters>
    <parameters><name>selectedFunction</name><type>Literal</type><value>Get</value></parameters>
    <parameters><name>IsRealTime</name><type>Literal</type><value>false</value></parameters>
    <parameters><output>true</output><name>MaxRecordedPrice</name><type>Parameter</type><value>__MAX_TAG__</value></parameters>
    <parameters><output>true</output><name>SavedRecordedPrice</name><type>Parameter</type><value>__MIN_TAG__</value></parameters>
  </customElement>
  <name>PriceTracking</name>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```

Decision table work: `../../decision-tables/SKILL.md`.

## Shipped in this repo (snapshot)

None. Discover live:
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify

1. Simulate; read the min/max output tags in the JSON (not waterfall). [Help]
2. Query Product Price Range / Product Price History Log for the product, selling model and price book. (Object names per Help.)
3. If Get returns stale values, refresh the decision table. [Help]

## Troubleshooting

| Symptom / error | Cause | Fix |
|---|---|---|
| Procedure fails after enabling max tracking | Decision table lacks `MaxRecordedPrice` | Deactivate, add result, reactivate, or use V2 [Help] |
| Get returns old value | Table not refreshed | Refresh table [Help] |
| Only one price per day recorded | Daily max overwrite design | Expected [Help] |

## Open questions

- Exact names of the tracked-price and transaction-date inputs for Save: unconfirmed.
- Relation to Price History settings: confirm in a live Builder.
- Max tag naming differs: Help `ItemMaxRecordedPrice_std`, core `ItemMaxRecordedPrice__std`; use the context-defined name.
