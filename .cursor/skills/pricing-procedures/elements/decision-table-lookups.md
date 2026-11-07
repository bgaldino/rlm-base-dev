# Decision table and matrix lookups (`GetOutputsFromDecisionTable`, `GetOutputsFromDecisionMatrix`)

> Release 264 / API v68.0. Sources: `meta_expressionsetdefinition.htm` (actionType enum,
> `ExpressionSetDecisionTable`), `connect_requests_expression_set_version.htm` (JSON
> example); `ind.pricing_configure_decision_tables.htm`. Shipped XML: none (no shipped
> procedure uses these actionTypes). Enum values and the lookup parameter convention checked against core [Core].

Generic lookup steps: read a decision table or decision matrix and return its output
columns into procedure variables. Not pricing-specific; no price waterfall entry.

## When to use it

- Use when you need a plain lookup (tax code, region, tier label, rate) that no dedicated element covers. [inferred]
- Do not use for base price: use [List Price](./list-price.md) (waterfall, currency, contract handling).
- Do not use for matrix-driven price adjustment: use the Price Adjustment Matrix element. [Help: `ind.pricing_add_the_price_adjustment_matrix_element.htm`]
- `DecisionTable` = Salesforce decision table (refreshable object); `DecisionMatrix` = Business Rules Engine decision matrix. Both enumerated as actionTypes and as variable `dataType`/`lookupType`. [Dev guide]

## Configuration

Unlike pricing elements, these steps use the step-level `lookupTable` object, not
`customElement` parameters. [Dev guide]

| Field | Where | Type | Required | Notes |
|---|---|---|---|---|
| Lookup name | `lookupTable.lookupTableName` | string | Yes | Table or matrix name (example `DM_for_test`) [Dev guide] |
| Lookup type | `lookupTable.type` | `DecisionMatrix` or `DecisionTable` | Yes | [Dev guide] |
| Input columns | procedure `variables[]` with `input=true`, `lookupName`, `lookupType` | Variable | Yes | Variable name is the column name (example `City`) |
| Output columns | `variables[]` with `output=true`, same `lookupName`/`lookupType` | Variable | Yes | Named `<LookupName>__<Column>` (example `DM_for_test__State`) [Dev guide] |

The step is `stepType: BusinessKnowledgeModel`, `actionType: GetOutputsFromDecisionMatrix`
or `GetOutputsFromDecisionTable`. Step `name` equalled the lookup name in the dev guide
example. Parameter shape beyond this is not shipped here. Note the repo skill mentions
a `DecisionTable` parameter on `GetOutputsFromDecisionTable`; the dev guide example
shows `lookupTable`. Core has no pricing-specific parameter form for these actionTypes, so use the dev-guide `lookupTable` shape.

## How pricing elements parameterize a lookup [Core]

Dedicated pricing elements (List Price, Price Adjustment Matrix, tiers, attribute-based) are the supported way to look up a table in a pricing procedure. They use `customElement` literals `LookUpName`, `LookUpApiName`, `LookUpId`. The table's **input columns** become the step's formal input parameters and its **output columns** the formal outputs, each bound to a procedure variable. The id's key prefix decides whether core reads a decision table or a decision matrix, so one convention covers both. If `LookUpApiName` is set and the id does not load, core resolves the id from the name.

Both `GetOutputsFromDecisionTable` and `GetOutputsFromDecisionMatrix` exist in the shared Business Rules Engine step enum (alongside non-pricing actions), so they validate on save. No pricing-specific parameter definition exists for them, and there is no `DecisionTableLookup` actionType [Core]; do not use that name. For a lookup with price semantics use the dedicated elements; for plain lookups prefer these steps with the `lookupTable` shape below.

## Placement and ordering

- After Pricing Setting; before any element that reads its output variables.
- Top-level or inside a ListGroup like other BKM steps. [inferred]
- No pricing-specific ordering rules documented. See [procedure anatomy and ordering](../procedure-anatomy-and-ordering.md).

## Rules and limits

- The table or matrix must exist and be Active/refreshed; stale tables return stale or no rows. Authoring, refresh and freshness: [decision-tables](../../decision-tables/SKILL.md).
- Inputs map by column name; mismatched variable names return no match. [inferred]
- The validator treats both actionTypes as known values (`scripts/expression_sets/_schema.py`). [Repo]
- Dedicated pricing elements (List Price, Price Adjustment Matrix) additionally require recipe table mappings; see [pricing-wiring](../../pricing-wiring/SKILL.md). Whether generic lookups need one is unconfirmed.

## Metadata shape

Connect JSON (from the dev guide example; trimmed):

```json
{
  "name": "DM_for_test",
  "stepType": "BusinessKnowledgeModel",
  "actionType": "GetOutputsFromDecisionMatrix",
  "lookupTable": { "lookupTableName": "DM_for_test", "type": "DecisionMatrix" },
  "resultIncluded": true,
  "sequenceNumber": 2
}
```

Plus variables:

```json
{ "name": "City", "dataType": "Text", "input": true, "output": false,
  "lookupName": "DM_for_test", "lookupType": "DecisionMatrix", "type": "Variable" }
{ "name": "DM_for_test__State", "dataType": "Text", "input": false, "output": true,
  "lookupName": "DM_for_test", "lookupType": "DecisionMatrix", "type": "Variable" }
```

Metadata API equivalent: `<decisionTable>` child of `<steps>` ("Represents a decision
matrix or decision table step"). Field details were not extractable from the local dev
guide copy. [Dev guide]

## Shipped in this repo (snapshot)

None. Pricing lookups ship as `ListPrice`, `PriceAdjustmentMatrix`, `AttributeDiscount`
and similar. Discover with
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify

- Simulate with known input values; confirm the `<LookupName>__<Column>` output variables are populated in the JSON output.
- Query the table's source or check decision table Fresh status.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Output variables null | No matching row, stale table, or input variable unset | Refresh table; check inputs |
| Step rejected on save | Wrong `lookupTable.type`, or lookup name not found | Match name and type |
| Works in one org only | Org-specific lookup record | Reference by name, not id |

## Open questions

- Metadata API `<decisionTable>` field list needs a live Builder save.
- Whether these steps appear in the price waterfall, and whether they need recipe mappings, is unverified (the pricing runtime handling of these actionTypes was not found in core).
