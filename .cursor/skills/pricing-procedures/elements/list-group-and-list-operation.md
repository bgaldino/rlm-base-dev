# List Group (`ListGroup`) and List Operation (`AdvancedListFilter`)

> Release 264 / API v68.0. Sources: `ind.pricing_list_group_list_operation.htm`
> (rating twin: `ind.rm_element_list_group_list_operation.htm`);
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
- Help describes the operation as filtering, value lookups and computations "on line items" [Help]; the shipped XML only uses it as a filter container (a lookup or compute is a child element of the group, not a different step type) [Repo].

## Configuration
| Builder field | Metadata field | Type | Required | Notes |
|---|---|---|---|---|
| List Group name/label | `name`, `label`, `stepType=ListGroup` | step | yes | No `actionType`, no `customElement` [Repo] |
| Filter Condition Requirements | `advancedCondition.conditionLogic` | string | yes | AND, OR and parenthesised combinations over the criterion numbers, e.g. `1`, `1 AND 2`, `1 OR 2`, `(1 OR 2) AND 3`, `1 AND (2 OR (3 AND 4))` [Repo]. Builder "All Conditions Are Met (AND)" is `1 AND 2 ...` [Help] |
| Resource | `criteria.sourceFieldName` | string | yes | Context tag or variable (e.g. `ItemProductCode`, `SellingModelType`) |
| Operator | `criteria.operator` | enum | yes | Full set: `Equals`, `NotEquals`, `GreaterThan`, `GreaterThanOrEquals`, `LessThan`, `LessThanOrEquals`, `Contains`, `DoesNotContain`, `IsNull`, `IsNotNull` [Core]. Shipped XML uses only `Equals`, `NotEquals`, `GreaterThan`, `IsNull`, `IsNotNull` [Repo] |
| Value | `criteria.value` | string | for non-null ops | String literals single-quoted: `&apos;Evergreen&apos;`; booleans/numbers bare [Repo] |
| (value kind) | `criteria.valueType` | string | with `value` | `Literal`, `Parameter`, `Formula`, `Lookup` [Core]; the dev guide enum for this field also lists `Picklist` [Dev guide]. Shipped XML uses `Literal` (most criteria) and `Parameter` (compare against another variable) [Repo]. `Field` is in neither core's enum nor the dev guide's; do not use it [Core][Dev guide] |
| (order) | `criteria.sequenceNumber` | int | yes | 1-based; matches the numbers in `conditionLogic` |

Step types: `ListGroup`, `AdvancedListFilter` and `ListFilter` (the formula-style filter, `conditionExpression` instead of criteria) are in the dev guide `stepType` enum, marked available from API 67.0 [Dev guide]. `ListBranch` (lane-based, not covered here) is not in that public enum [Dev guide], yet core's save validation accepts it as a container of list-filter lanes (with an optional `DefaultPath` lane) and has messages such as `{0} must have at least one list filter lane.` [Core]. Treat it as not publicly documented; API-version availability is unconfirmed.

## Placement and ordering
- ListGroup is top-level; its children carry `parentStep=<group name>` and a per-parent `sequenceNumber` starting at 1. Children are sorted by `sequenceNumber` within their own parent, so numbering restarts under each group [Repo].
- The filter must be the first child; every list group must begin with a List Filter [Help][Core].
- Only one list filter per list group [Help][Core]. Need two populations: two groups.
- A group with no children is rejected, and the filter cannot be the last or only child [Core].
- Children run in `sequenceNumber` order, only for lines that passed the filter. Lines that do not match skip the whole group [Help]. The filter is evaluated first and the children run on the filtered set; whether the unfiltered set stays visible to aggregate elements is [inferred].
- Groups are siblings at top level, ordered by their own `sequenceNumber`. Cross-element ordering: [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).

## Rules and limits
- Add a not-null criterion on any tag you compare; a null tag at execution returns an error [Help]. Example: `{LineItem IsNotNull} AND {LineItem equals 100}`.
- Reset pattern: to clear a field on all lines, use a filter that matches everything (`IsNull OR IsNotNull` on one field) [Repo overlay `approval_flags.json`]; not a platform requirement.
- Removing a producer element while leaving a group's filter in place stays structurally valid but silently misprices; check orphaned groups (see `../../expression-sets/authoring-and-overlays.md` "Removing steps").
- Condition count per filter is capped by an org limit ("Maximum Number of Conditions per Expression Set Version Step"); save fails with `A step can have a maximum of {0} conditions.` with the limit as {0} [Core]. Org value default 200, min 1, max 200, API 242+ [Core]. Shipped procedures use up to 9 criteria in one filter [Repo].
- Local list nodes: a maximum local-list-node depth applies (save error `The maximum depth of a local list node in an expression set version is {0}.`); org value default 6, min 0, max 6, API 262+ [Core]. This limits context-hierarchy depth of list variables, not how many groups you stack.

## Feasibility / not supported
| Need | Answer |
|---|---|
| Group inside a group | No. Unsupported child step types are rejected with `{0} is not allowed inside {1}.` [Core]; the allowed children are a `BusinessKnowledgeModel` step whose `actionType` is `AssignParameterValues`, `GetOutputsFromDecisionMatrix`, `GetOutputsFromDecisionTable` or `PredictiveAI` (or a custom element allowed for the usage type), plus `SubExpression` steps [Core]. Use a second sibling group (`ListBranch` lanes exist in core but are not publicly documented; see Step types) [Core] |
| Two filters in one group | No; use two groups [Help][Core] |
| `Field` value kind, or a group with no filter | No [Core] |
| A filter as the last child | No: `A {0} can't be the last or the only step element in a {1}.` [Core] |
| Local variable as a calculation's output inside the group | Allowed ("advanced looping"), but then only calculation steps and the filter may be in that group; add a lookup, custom element, predictive AI or sub-expression and save fails [Core] |
| Filter at top level | No: `{0} should be inside List Enabled Group or List Branch Lane.` [Core] |
| Conditional on lines other than the one being filtered | Not documented; the filter is evaluated per line item [inferred] |
| Aggregation across the filtered lines | Use the aggregate elements, see [aggregate-price](./aggregate-price.md) [inferred] |

Rating procedures have a twin element with the same container behavior [Help].

## Metadata shape
Shipped `RLM_DefaultPricingProcedure` group and filter, envelope flags omitted [Repo]:
```xml
<steps>  <!-- container -->
    <label>Apply prorated pricing to evergreen lines</label>
    <name>Applyproratedpricingtoevergreenlines</name>
    <resultIncluded>false</resultIncluded>
    <sequenceNumber>29</sequenceNumber>
    <stepType>ListGroup</stepType>
</steps>
<steps>  <!-- filter: child 1 -->
    <advancedCondition>
        <conditionLogic>1 AND 2 AND 3</conditionLogic>
        <criteria><operator>Equals</operator><sequenceNumber>1</sequenceNumber>
            <sourceFieldName>SellingModelType</sourceFieldName>
            <value>&apos;Evergreen&apos;</value><valueType>Literal</valueType></criteria>
        <criteria><operator>Equals</operator><sequenceNumber>2</sequenceNumber>
            <sourceFieldName>AllowPartialProrationPeriods</sourceFieldName>
            <value>true</value><valueType>Literal</valueType></criteria>
        <criteria><operator>IsNotNull</operator><sequenceNumber>3</sequenceNumber>
            <sourceFieldName>itemTransientEndDate</sourceFieldName></criteria>
    </advancedCondition>
    <name>Filterevergreenlineswithpartialprorationandsubscriptionenddate</name>
    <parentStep>Applyproratedpricingtoevergreenlines</parentStep>
    <sequenceNumber>1</sequenceNumber>
    <stepType>AdvancedListFilter</stepType>
</steps>
<!-- children (formula, assignment, ...): parentStep = group, sequenceNumber 2.. -->
```
Overlay JSON (Connect): the same, with `advancedCondition` as an object and `placement.afterStep` on the group; see `docs/references/expression-set-overlay-examples/facility-quantity.overlay.example.json`.

## Shipped in this repo (snapshot)
`ListGroup` steps in shipped XML: default pricing 31, PRM distributor 28, recalc 22, price distribution 3, negotiable rating 3 [Repo]. Examples:

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
| `{0} can not have more than 1 List Filter step inside it.` | Second filter in a group | Use a second group [Core] |
| `Select list filter as the first element in list group.` | First child is not a filter | Make the filter child 1 [Core] |
| `{0} can not be empty.` | Group has no children | Add the filter and at least one element [Core] |
| `{0} is not allowed inside {1}.` | Unsupported child (for example a nested group) | Move it out, see Feasibility [Core] |
| `If you specify a local variable for assignedParameter ...` | Advanced looping group also holds lookup/custom/sub-expression | Split the group [Core] |

## Help coverage
`ind.pricing_list_group_list_operation` (container, first-filter rule, one filter, null-guard, quantity example) and the rating twin `ind.rm_element_list_group_list_operation` are reflected above. Help links "Operators and Functions in Expression Sets" for operator support; the operator list here comes from core.

## Save-time rules and Help notes
- Save-time criteria rules [Core, criteria save validation]:
  - `IsNull`/`IsNotNull` with a `value` or `valueType` set fails with `Specify a valid expression for the {0} step. {1}` ({1} may be empty).
  - Resource (`sourceFieldName`) not a variable, alias or context tag fails with `We couldn’t find the resource {0} used in the step {1}. Specify a valid resource and try again.`
  - A `value` is validated as a formula whose result type is the resource's data type. Type mismatch gives `Specify a valid expression for the {0} step. {1}`; other parse errors give `Specify a valid formula for the {0} step. {1}`; a too-long formula gives `The formula at {0} step reached the limit. {1}`. A `value` over the Expression field maximum (4,000 characters) gives `The expression at {0} reached the limit. Simplify or split the formula, and try again.`
- `ListFilter` (formula style) uses `conditionExpression` with `expression`, `resultParameter`, `successMessage`, `errorMessage` [Dev guide]. Save validates `expression` as a Boolean formula, with the same errors as above plus `For the {0} step’s resultParameter, specify the variable name that corresponds to the step's resultStep parameter.` for a bad `resultParameter` [Core].
- Help vs core: Help's null-guard example (`{LineItem equals isNotNull}`) is loose wording; the actual operators are `IsNotNull`/`IsNull` with no value. No conflicts found otherwise.

## Open questions
- `Contains`/`DoesNotContain` on non-text types: core builds `CONTAINS(source,'%value%')` / `NOT CONTAINS(...)` for text, and picklist-type sources use `ISPICKVAL` and ignore the operator [Core]; behavior on number/date sources is unconfirmed, so use `Equals`/comparison operators there.
- Whether filtered-out lines stay visible to aggregate elements, and how core marks them at runtime, was not located: leave as [inferred].
