# Stop Pricing (`StopPricing`)

> Release 264 / API v68.0. Sources: `ind.pricing_stop_pricing.htm`,
> `ind.pricing_list_group_list_operation.htm`; dev guide
> `meta_expressionsetdefinition.htm` (actionType enum); shipped XML: none;
> core source (behavior only, from a platform test fixture).

Flow-control element. When a line reaches it, pricing for that line ends: no
later element runs and the values so far become the final price.

## When to use it
- Use for exclusive pricing: once a rule applies (e.g. 50+ units get a flat discount), no further discount or calculation should touch the line [Help].
- Use only inside a [List Group](./list-group-and-list-operation.md) so the filter decides which lines stop.
- Do not use to skip one element; filter that element's own group instead.
- Does not stop other lines: it affects only the line that hits it [Help].

## Configuration
| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| (none) | none | n/a | n/a | No inputs. The core test fixture has `customElement.parameters: []` [Core] |
| Include in Output | `resultIncluded` (step field) | boolean | no | Help says to select Include in Output in the List Group walk-through [Help]; maps to `resultIncluded` (inferred) |

## Placement and ordering
- Put it last in the List Group, after the elements whose result should stand (Help example: Formula-Based Pricing, then Stop Pricing) [Help].
- Child of the ListGroup (`parentStep`), with a `sequenceNumber` after the filter and calculation steps [Core fixture: filter 1, StopPricing 2].
- Everything after it in the procedure is skipped for matching lines, including the closing tail (DDS, aggregates, rounding) (inferred from "no subsequent pricing elements are executed" [Help]). Decide whether skipped lines still need header-discount or aggregate results before using it; confirm live.
- Ordering overview: [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).

## Rules and limits
- Stops immediately for that line; later elements do not run; current values are final [Help].
- Per line only [Help].
- Waterfall in Simulate shows where the procedure stopped [Help].
- A breakdown-line/parent scenario exists in core tests that combines a list filter and StopPricing, so parent/child (bundle) interaction is exercised; behavior details are not documented [Core].

## Metadata shape
Skeleton from the core test fixture (JSON form; XML equivalent follows the same field names):
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
    <label>Stop Pricing</label>
    <name>StopPricing</name>
    <parentStep>__LISTGROUP__</parentStep>
    <sequenceNumber>2</sequenceNumber>
    <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
`StopPricing` is in the `actionType` enum of `ExpressionSetDefinition` [Dev guide]. Whether the XML needs an empty `<customElement/>` is unconfirmed. Lifecycle: [../../expression-sets/SKILL.md](../../expression-sets/SKILL.md).

## Shipped in this repo (snapshot)
None. No procedure in `force-app/`, `unpackaged/post_procedureplans/` or `unpackaged/post_prm_pricing/` contains a `StopPricing` step. Discovery: `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`.

## Verify
- Simulate with a line that meets the group filter and one that does not; the waterfall ends at Stop Pricing for the first and continues for the second [Help].
- Check that the final `NetUnitPrice`/`TotalLineAmount` equals the value just before the stop.

## Troubleshooting
| Symptom / error | Cause | Fix |
|---|---|---|
| Totals, header discount or aggregates missing for some lines | Those lines stopped before the tail (inferred) | Narrow the group filter, or move the stop-eligible logic so required steps run first |
| Stop applies to every line | Filter matches all lines or element is outside a group | Place it inside a filtered List Group |
| Later discounts still apply | Stop Pricing sits before, not after, the group's calculations or in a different group | Reorder within the group; it only stops what follows |

## Open questions
- Exact effect on the closing tail (DDS, aggregates, rounding) and on bundle children: needs a live Simulate.
- Whether `resultIncluded` is the "Include in Output" toggle.
- Not shipped; no XML sample from a real org. Core sample is a test fixture only.
