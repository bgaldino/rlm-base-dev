# List Group (`ListGroup`) and List Operation (`AdvancedListFilter`)

> Release 264 / API v68.0. Sources: `ind.pricing_list_group_list_operation.htm`;
> dev guide `meta_expressionsetdefinition.htm`; shipped XML:
> `RLM_DefaultPricingProcedure`, `RLM_PRM_DISTI_Pricing_Procedure`,
> `RLM_Price_Distribution_Procedure`, `RLM_Revenue_Management_Recalc_Procedure`,
> `Negotiable_Rating_Procedure`; core source (behavior only).

A List Group is a container: it holds a filter plus the elements that run only
on the lines the filter selects. The filter is a List Operation, stored as an
`AdvancedListFilter` step. Neither has an `actionType` or `customElement`.

## When to use it
- Use to run elements (formula, assignment, discount, lookup) on a subset of lines.
- Use to stop pricing for matching lines: filter, then [Stop Pricing](./stop-pricing.md) inside the group.
- Do not use a group when every line takes the same path; add the element at top level.
- Help describes the operation as filtering, value lookups and computations "on line items" [Help]; the shipped XML only ever uses it as a filter container (a lookup or compute is a child element of the group, not a different step type) [Repo].

## Configuration
| Builder field | Metadata field | Type | Required | Notes |
|---|---|---|---|---|
| List Group name/label | `name`, `label`, `stepType=ListGroup` | step | yes | No `actionType`, no `customElement` [Repo] |
| Filter Condition Requirements | `advancedCondition.conditionLogic` | string | yes | `1`, `1 AND 2`, `1 OR 2`, `1 AND (2 OR 3)` [Repo]. Builder "All Conditions Are Met (AND)" is `1 AND 2 ...` [Help] |
| Resource | `criteria.sourceFieldName` | string | yes | Context tag or variable (e.g. `ItemProductCode`, `SellingModelType`) |
| Operator | `criteria.operator` | enum | yes | Full set: `Equals`, `NotEquals`, `GreaterThan`, `GreaterThanOrEquals`, `LessThan`, `LessThanOrEquals`, `Contains`, `DoesNotContain`, `IsNull`, `IsNotNull` [Core]. Shipped XML and overlays use a subset [Repo] |
| Value | `criteria.value` | string | for non-null ops | String literals single-quoted: `&apos;Evergreen&apos;`; booleans/numbers bare [Repo] |
| (value kind) | `criteria.valueType` | string | with `value` | `Literal`, `Parameter`, `Formula`, `Lookup` [Core]. Shipped XML uses `Literal` only [Repo]. `Parameter` compares against another variable (inferred). `Field` is not in core's enum; do not use it |
| (order) | `criteria.sequenceNumber` | int | yes | 1-based; matches the numbers in `conditionLogic` |

## Placement and ordering
- ListGroup is top-level; its children carry `parentStep=<group name>` and a per-parent `sequenceNumber` starting at 1 [Repo].
- The `AdvancedListFilter` must be child `sequenceNumber` 1; every list group must begin with a List Filter [Help].
- Only one list filter per list group [Help]. Need two populations: two groups.
- Children run in `sequenceNumber` order, only for lines that passed the filter. Lines that do not match skip the whole group [Help].
- Groups are siblings at top level, ordered by their own `sequenceNumber`. Cross-element ordering: [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).
- Nested groups are not shipped and no nesting rule was found in core; treat as unsupported until a live save succeeds.

## Rules and limits
- Add a not-null criterion on any tag you compare; a null tag at execution returns an error [Help]. Example: `{LineItem IsNotNull} AND {LineItem equals 100}`.
- Reset pattern: to clear a field on all lines, use a filter that matches everything (`IsNull OR IsNotNull` on one field) [Repo overlay `approval_flags.json`]; not a platform requirement.
- Removing a producer element while leaving a group's filter in place stays structurally valid but silently misprices; check orphaned groups (see `../../expression-sets/authoring-and-overlays.md` "Removing steps").

## Metadata shape
```xml
<steps>  <!-- container -->
    <label>Calculate cost and margin for priced lines</label>
    <name>Calculatecostandmarginforpricedlines</name>
    <resultIncluded>false</resultIncluded>
    <sequenceNumber>34</sequenceNumber>
    <stepType>ListGroup</stepType>
</steps>
<steps>  <!-- filter: child 1 -->
    <advancedCondition>
        <conditionLogic>1 AND 2</conditionLogic>
        <criteria><operator>Equals</operator><sequenceNumber>1</sequenceNumber>
            <sourceFieldName>SellingModelType</sourceFieldName>
            <value>&apos;Evergreen&apos;</value><valueType>Literal</valueType></criteria>
        <criteria><operator>IsNull</operator><sequenceNumber>2</sequenceNumber>
            <sourceFieldName>itemTransientEndDate</sourceFieldName></criteria>
    </advancedCondition>
    <name>FilterEvergreen</name>
    <parentStep>Calculatecostandmarginforpricedlines</parentStep>
    <sequenceNumber>1</sequenceNumber>
    <stepType>AdvancedListFilter</stepType>
</steps>
<!-- children (formula, assignment, ...): parentStep = group, sequenceNumber 2.. -->
```
Overlay JSON (Connect): the same, with `advancedCondition` as an object and `placement.afterStep` on the group; see `docs/references/expression-set-overlay-examples/facility-quantity.overlay.example.json`.

## Shipped in this repo (snapshot)
| Procedure | Group (examples) | Purpose |
|---|---|---|
| RLM_DefaultPricingProcedure | `Calculatecostandmarginforpricedlines` | filter `ItemUnitCost__std IsNotNull`, then cost/margin formula |
| RLM_DefaultPricingProcedure | `Applyproratedpricingtoevergreenlines` | evergreen + partial proration + end date set |
| RLM_DefaultPricingProcedure | `Setpricingdateforlineswithcontractpricing` | `IsContracted` true and `PricingDate IsNull` |
| RLM_DefaultPricingProcedure | `ApplyHeaderPriceOverride`, `ApplyPercentageBasedHeaderDiscount` | header discount branches |

Snapshot; refresh with `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`.

## Verify
- Simulate with a line that matches and one that does not; the waterfall shows the group's children only for the match [Help].
- `trace_expression_set.py` shows consumers/producers per variable.

## Troubleshooting
| Symptom / error | Cause | Fix |
|---|---|---|
| Group never fires | Filter criteria never true; string value not quoted | Quote string literals; test with `IsNotNull` first |
| Error when executing on quote/order | Compared tag is null | Add `IsNotNull` criterion [Help] |
| Stale value stays on non-matching lines | Branch-only assignment | Reset first; see [assignment](./assignment.md) |
| Second filter rejected | One filter per group | Use a second group |

## Open questions
- Whether groups can nest: no shipped example, no rule found in core; test live.
- `Contains`/`DoesNotContain` on non-text types: unconfirmed.
