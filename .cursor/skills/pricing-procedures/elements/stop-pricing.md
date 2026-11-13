# Stop Pricing (`StopPricing`)

> Release 264 / API v68.0. Sources: `ind.pricing_stop_pricing.htm`,
> `ind.pricing_list_group_list_operation.htm`; dev guide
> `meta_expressionsetdefinition.htm` (actionType enum); shipped XML: none;
> platform source (behavior only): Stop Pricing marks the line as aborted, which
> later elements check before running (Aggregate Price is the exception: it still sums the stopped line).

Flow-control element. When a line reaches it, pricing for that line ends: no
later element runs (Aggregate Price still sums the line) and the values so far become the final price.

## When to use it
- Use for exclusive pricing: once a rule applies (e.g. 50+ units get a flat discount), no further discount or calculation should touch the line [Help].
- Use only inside a [List Group](./list-group-and-list-operation.md) so the filter decides which lines stop.
- Do not use to skip one element; filter that element's own group instead.
- Does not stop other lines: it affects only the line that hits it [Help].

## Configuration
| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| (none) | none | n/a | n/a | No inputs or outputs: core declares no formal parameters for this element, so `customElement` carries none [Core]. Builder offers Hide in Waterfall only [inferred: not re-verified] |
| Include in Output | `resultIncluded` (step field) | boolean | no | Help says to select Include in Output in the List Group walk-through [Help]; maps to `resultIncluded` [Dev guide] |

## Placement and ordering
- Put it last in the List Group, after the elements whose result should stand (Help example: Formula-Based Pricing, then Stop Pricing) [Help].
- Child of the ListGroup (`parentStep`), with a `sequenceNumber` after the filter and calculation steps [inferred: filter first, so the stop is at least sequence 2].
- Stop Pricing marks the line aborted. Every later element, in any group, skips an aborted line [Help][Core]; this includes DDS, Rounding Values and Price Propagation. Core's shared line-selection rule skips aborted lines for every element except Aggregate Price, so an aggregate still sums a stopped line's final values [Core]. Lines that are ignored, errored or skipped never reach Stop Pricing in the first place [Core].
- Outside a List Group it stops every line that reaches it, because a top-level element runs for all eligible lines [inferred from the same line-selection rule].
- Ordering overview: [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).

## Rules and limits
- Stops immediately for that line; later elements do not run; current values are final [Help]. Aggregate Price still includes the stopped line [Core].
- Per line only [Help]. It does not stop the children of a stopped bundle parent; a child stops only if its own line meets the condition [Platform behaviour, traced].
- Stopped lines are still counted by Aggregate Price, but only within that element's own list-group filter: a line the filter excludes is invisible to the aggregate [Platform behaviour, traced]. Price Propagation skips stopped lines, even in its own aggregation [Platform behaviour, traced].
- Waterfall in Simulate shows where the procedure stopped [Help].

## Metadata shape
Skeleton built from the element definition [inferred]. JSON form for an overlay (`label` is stripped by the overlay tool; a direct Connect POST rejects it, so drop it there):
```json
{
  "actionType": "StopPricing",
  "customElement": { "parameters": [] },
  "label": "Stop Pricing",
  "name": "StopPricing",
  "parentStep": "<list group name>",
  "sequenceNumber": 2,
  "resultIncluded": false,
  "stepType": "BusinessKnowledgeModel"
}
```
XML:
```xml
<steps>
    <actionType>StopPricing</actionType>
    <customElement/>
    <label>Stop Pricing</label>
    <name>StopPricing</name>
    <parentStep>__LISTGROUP__</parentStep>
    <resultIncluded>false</resultIncluded>
    <sequenceNumber>2</sequenceNumber>
    <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
`StopPricing` is in the `actionType` enum of `ExpressionSetDefinition` [Dev guide]. Every shipped `BusinessKnowledgeModel` step carries `customElement` and `resultIncluded`, so the skeleton includes both; whether an empty `<customElement/>` deploys is unconfirmed. Lifecycle: [../../expression-sets/SKILL.md](../../expression-sets/SKILL.md).

## Shipped in this repo (snapshot)
None. No procedure in `force-app/`, `unpackaged/post_procedureplans/` or `unpackaged/post_prm_pricing/` contains a `StopPricing` step. Discovery: `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name>`.

## Verify
- Simulate with a line that meets the group filter and one that does not; the waterfall ends at Stop Pricing for the first and continues for the second [Help].
- Check that the final `NetUnitPrice`/`TotalLineAmount` equals the value just before the stop.

## Troubleshooting
| Symptom / error | Cause | Fix |
|---|---|---|
| Header discount (DDS) or rounding missing for some lines | Those lines were stopped earlier, so later elements skip them [Core] | Narrow the group filter, or move the stop-eligible logic so required steps run first |
| Stop applies to every line | Filter matches all lines or element is outside a group | Place it inside a filtered List Group |
| An unwanted discount still applies to a line you meant to stop | The line never reached Stop Pricing (the group filter is false for it), or the discount runs before the stop. Once a line reaches the stop, no later element runs for it (Aggregate Price aside), including elements in later groups [Help][Core] | Check in Simulate that the line reaches the stop; move discounts that must not apply after the stop, or exclude the line from their groups |

## Open questions
- Effect on bundle children: no parent-to-child cascade was found [Platform behaviour, traced]; that is absence of a finding in the traced code, so confirm with a live Simulate.
- Not shipped; no XML sample from a real org. The JSON skeleton above is built from the element's parameter-less definition, not from a saved step.
