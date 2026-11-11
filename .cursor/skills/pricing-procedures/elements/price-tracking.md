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
(registered with the Price Tracking icon) [Core]; [Dev guide] lists `MinimumPrice` from API 62.0. `PriceGuidance` is a different element (registered as a separate non-lookup element; Builder offers it only in orgs with an analytics pilot enabled [Core]). Its runtime reads floor, ceiling and target value percentages from context rules; its exact design-time parameters (input `ListPrice`, price and percentage outputs) were not verified [inferred]; [Dev guide] lists it from API 64.0. Do not use it for tracking.

## Configuration

| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Lookup table | `LookUpName`, `LookUpApiName`, `LookUpId` | Literal | yes | Help picks Price Book Entries V2 in the example; core fixtures use a Product Price Range Entries table. Set `LookUpId` to the table's record Id; this repo's CCI transforms do not resolve a token for this table (see Metadata shape). [Help][Core] |
| Action Type | `selectedFunction` | Literal | yes | Stored values `Get`, `Save`, `Save and Get` (Builder constants; Help shows "Save & Get") [Core]. |
| Input: Product | `ProductId` | Parameter | yes | [Core] |
| Input: Price Book | `PricebookId` | Parameter | yes | [Core] |
| Input: Product Selling Model | per lookup table | Parameter | per Help | Inputs are generated from the lookup table's input columns, so the name is the column mapping you choose [Core] |
| Inputs for Save / Save and Get | `TrackedPrice`, `TransactionDate` | Parameter | yes | Tag names core reads; added when `selectedFunction` is not `Get`. `TransactionDate` is a date-time tag; the history save uses the `yyyy-MM-dd` day. All three of `TrackedPrice`, `TransactionDate` and the currency are required on the Save paths. [Core] |
| Output: Min recorded | `SavedRecordedPrice` | Parameter, output | | Absent when function is `Save` [inferred]; core sets it only when the tag exists on the step. Help label "Saved Min Recorded Price" (`ItemRecordedPrice`). [Help][Core] |
| Output: Max recorded | `MaxRecordedPrice`, `SavedMaxRecordedPrice` | Parameter, output | | `SavedMaxRecordedPrice` exists only when the org's maximum-price-compliance preference is on and function is not `Save` [Core]. Help example maps `ItemMaxRecordedPrice_std`; core fixture uses `ItemMaxRecordedPrice__std`. [Help][Core] |
| (fixed) | `sectionCount`=`0`, `IsRealTime`, `IsOutputResolutionEnabled` | Literal | yes | As on lookup elements [inferred]; the core fixture below shows `sectionCount`, `selectedFunction` and `IsRealTime`. |

## Placement and ordering

- Help example places it after List Price and Manual Discount, so it can record the final price. [Help]
- Whether it must precede or follow DDS and the aggregate tail: not stated. See [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).
- Top-level; the result is JSON-only (not in the waterfall). [Help]

## Rules and limits

| Rule | Source |
|---|---|
| Help: every run or simulation saves its result to Product Price History Log, and a larger same-day price "overwrites" the maximum entry. Core: only Save and Save and Get write history (Get only reads the range table), and the overwrite is the net effect of the purge job below, not an inline overwrite. So a Get-only step may record nothing; verify on the org. | [Help][Core] |
| Product Price Range stores the min/max for the configured duration and is the source for Get / Save & Get. | [Help] |
| The save only inserts a Product Price History Log row (range, day, tracked price, currency) per call; it never overwrites inline, for minimum or maximum tracking. A save with no matching range row creates a new range first. Whether a second same-day insert for the same range is rejected by a uniqueness check is not confirmed. | [Core][inferred] |
| A scheduled purge job later reads rows created since its previous run, grouped by range and day. Per group it keeps one row at the minimum price (if minimum tracking is on) and one at the maximum price (if maximum tracking is on); ties keep the lowest record name, and one row survives when both are equal. All other rows for that range and day are deleted. It then recomputes the range's recorded min/max over the configured duration (null when 0). So within a day only the minimum and/or maximum row remain, per enabled tracking. | [Core] |
| The async save runs only when price tracking is enabled in the org. | [Core] |
| To rerun Get you must manually refresh the decision table. | [Help] |
| If maximum tracking is enabled in Price Tracking History settings but the Product Price Range Entries decision table lacks `MaxRecordedPrice`, the procedure fails at execution. | [Help] |
| New enablement with both min and max: use predefined Product Price Range Entries V2. | [Help] |

## Metadata shape

Parameter names and values from a core test fixture (not shipped here); the flags follow
the shipped convention for inputs and outputs. The `__...__` values are placeholders you
replace yourself: `LookUpId` is the decision table's record Id, and this repo's CCI
transforms resolve only the `__LOOKUPID_*__` tokens of the shipped tables, not this one.

```xml
<steps>
  <actionType>MinimumPrice</actionType>
  <customElement>
    <parameters><input>true</input><name>ProductId</name><output>false</output><type>Parameter</type><value>Product</value></parameters>
    <parameters><input>true</input><name>PricebookId</name><output>false</output><type>Parameter</type><value>PriceBooks</value></parameters>
    <parameters><input>true</input><name>LookUpName</name><output>false</output><type>Literal</type><value>__TRACKING_TABLE_NAME__</value></parameters>
    <parameters><input>true</input><name>LookUpApiName</name><output>false</output><type>Literal</type><value>__TRACKING_TABLE_API_NAME__</value></parameters>
    <parameters><input>true</input><name>LookUpId</name><output>false</output><type>Literal</type><value>__PRICE_RANGE_TABLE_ID__</value></parameters>
    <parameters><input>true</input><name>sectionCount</name><output>false</output><type>Literal</type><value>0</value></parameters>
    <parameters><input>true</input><name>selectedFunction</name><output>false</output><type>Literal</type><value>Get</value></parameters>
    <parameters><input>true</input><name>IsRealTime</name><output>false</output><type>Literal</type><value>false</value></parameters>
    <parameters><input>false</input><name>MaxRecordedPrice</name><output>true</output><type>Parameter</type><value>__MAX_TAG__</value></parameters>
    <parameters><input>false</input><name>SavedRecordedPrice</name><output>true</output><type>Parameter</type><value>__MIN_TAG__</value></parameters>
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

1. Simulate; read the min/max output tags in the JSON (not waterfall). [Help] With tracking enabled, a Save or Save and Get run writes history even from Simulate, and the daily purge keeps the extreme rows, so a deliberately low or high test price can become the recorded minimum or maximum. Test with realistic prices, in a sandbox or disposable org. [Help][Core][inferred]
2. Query Product Price Range / Product Price History Log for the product, selling model and price book. (Object names per Help.)
3. If Get returns stale values, refresh the decision table. [Help]

## Runtime behavior [Core]

- Function `Save` with `TrackedPrice` on the step skips the lookup and goes straight to the insert list. Save and Get runs the lookup first: one matching range row adds history for that range, none creates a new range, more than one logs a duplicate-lookup error. History is written by an asynchronous job, only when price tracking is enabled, so rows appear after the transaction. Get only reads the lookup (the Product Price Range table).
- For Save, the other lookup input columns plus `TrackedPrice` and `TransactionDate` are what is stored.
- Output tags: core sets `SavedRecordedPrice` (min) and `SavedMaxRecordedPrice` (max) only when the tag exists in the step.
- Multiple-output resolution is supported (candidate priority and resolution strategy). An inactive or unknown strategy logs `RESOLUTION_STRATEGY_NOT_ACTIVE`; an invalid strategy formula logs `RESOLUTION_FORMULA_ERROR`; the winner's min/max are written to the output tags. With resolution on, Help says a line with no matching row stops pricing as a configuration error (no zero, no skip) [Help]; not checked against core.

## Troubleshooting

| Symptom / error | Cause | Fix |
|---|---|---|
| Procedure fails after enabling max tracking | Decision table lacks `MaxRecordedPrice` | Deactivate, add result, reactivate, or use V2 [Help] |
| Run-time failure (error code `INVALID_INPUT`) before any line is priced | Maximum-price preference is on and the step's output parameters do not include `MaxRecordedPrice` (the lookup table lacks that result column) | Add `MaxRecordedPrice` to the table and step outputs [Core] |
| Line error `TRACKED_PRICE_NULL` ("Specify a valid tracked price value and try again."), `TRANSACTION_DATE_NULL` ("Specify a valid transaction date and try again."), `CURRENCY_ISO_CODE_NULL` ("Specify a valid currency ISO code and try again.") | The tag is on the step but empty for the line; the currency error also needs price tracking enabled in the org. Skipped when the tag is not on the step | Map `TrackedPrice`, `TransactionDate`, currency [Core] |
| `UNEXPECTED_ERROR_DURING_LOOKUP` | Lookup failed unexpectedly | Check the lookup table and rerun [Core] |
| Get returns old value | Table not refreshed | Refresh table [Help] |
| Few history-log rows per day | Purge job deleted all but the day's minimum and/or maximum row | Expected [Core]; Help describes the same-day maximum overwrite [Help] |

## Help coverage
- `ind.pricing_set_price_history_tracking.htm`: enablement only; enable min and/or max, duration up to 30 days (default 7); changing it resets the daily jobs and can distort history and prices [Help].
- `ind.pricing_price_tracking_actions.htm`: defines Get, Save, Save & Get only; reflected above.

## Open questions
- Whether a second same-day insert for the same range hits a uniqueness check: not found in the entity definition (the purge behavior itself is settled, see Rules).
- Relation to Price History settings: confirm in a live Builder.
