# Price Propagation (`PricingPropagation`)

> Release 264 / API v68.0. Sources: `ind.pricing_price_propagation.htm`,
> `ind.pricing_configure_the_price_propagation_element.htm`,
> `ind.pricing_price_propagation_limits.htm`; shipped XML: none (the
> `IsPropagationEnabled=false` flag ships on `PricingSettings` steps); core source
> (behavior only).

Computes hierarchical values in a nested transaction (group > subgroup > line):
horizontal formulas run in a strict sequence on one node, and ascending
propagation rolls child values up to parents through a table configured in the
Pricing Setting element.

## When to use it

- Multilevel group-to-group or group-to-item hierarchies (Help example: Building > Floor > Room > Panel line items) with sequential formulas and child-to-parent rollups. [Help]
- Do not use as a substitute for [Formula](./formula-based-pricing.md) or [Aggregate Price](./aggregate-price.md): it is designed for specific rollup logic. [Help]
- Contrast with Aggregate Roll Up: Roll Up adds child line prices to one parent line via a parent reference tag, one SUM-type function per section; Propagation uses a node/join/merged-attribute table, ordered horizontal formulas, and works across group levels. [Help]

## Configuration

Most configuration lives in the Pricing Setting element, not the Propagation step.

| Builder field | Parameter / storage | Type | Required | Notes |
|---|---|---|---|---|
| Pricing Setting > Enable Propagation | `IsPropagationEnabled` on the `PricingSettings` step | Literal `true`/`false` | yes | Ships as `false` in every repo procedure. [Repo][Core] |
| Configure Propagation Rules (table) | stored in the Pricing Setting JSON | JSON | yes when enabled | Save the table before saving the procedure, or save can fail with `LookUpName isn't a valid variable name`. [Help] |
| Add Nodes | table | | | Data sources and attributes, e.g. `SalesTransactionItem`, `SalesTransactionGroup`. [Help] |
| Join Nodes | table | | | Mapping Type Parent-Child; Parent Key (e.g. `GroupSource`); Child Key (e.g. `SalesTransactionItemGroup`); Node Identifier. [Help] |
| Merge Attributes | table | | | Merged attribute name, merged condition (e.g. Not Null), attributes 1 and 2. [Help] |
| Edit Attributes: horizontal formula | table | | | Column, formula, Sequence. Sequence required, positive, unique; not auto-adjusted. [Help] |
| Use Zero for Null Values | table | | | On: null inputs treated as 0. Off: any formula with a null argument is skipped. [Help] |
| Ascending propagation | table | | | Merged attribute, aggregation `Sum`, child field (e.g. `Sum(!Child.ItemTotalCost)`), up to 3 conditions, all must match. [Help] |
| Price Propagation element | `actionType=PricingPropagation` | | | The step declares NO input or output parameters; all configuration is in the Pricing Setting table. [Core] |

## Placement and ordering

- Prerequisite: a context definition with the nested group hierarchy (e.g. Sales Transaction Context) and the mappings that link the procedure to it. [Help] See `../../context-service/SKILL.md`.
- Top-level only; not supported inside a ListGroup. [Help]
- Help does not state an absolute position. Core test fixtures include start-of-procedure and end-of-procedure placements. Cross-element rules: [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).
- With delta pricing enabled, copy `NetUnitPrice` into a separate tag before the element and use that tag in the table and formulas. [Help]

## Rules and limits

| Rule | Source |
|---|---|
| One Price Propagation element per procedure. | [Help] |
| Incompatible with Derived Pricing, Map Line Item and Promotions elements in the same procedure. | [Help] |
| Do not use in amend, renew or cancel pricing procedures (inaccurate pricing). | [Help] |
| Existing procedure must not already contain propagation, derived price or promotion elements before enabling. | [Help] |
| Deselecting Enable Propagation keeps the configuration in the Pricing Setting JSON; to reset, remove and re-add the Pricing Setting element. | [Help] |
| `PricingPropagation` is available from API v65.0 (Release 258). | [Dev guide][Core] |
| Not eligible for element-level parallel execution; a procedure containing it runs sequentially. | [Core] |

## Metadata shape

Not shipped. Core declares no formal parameters for this element, so the step is an empty shell:

```xml
<steps>
  <actionType>PricingPropagation</actionType>
  <customElement><!-- no parameters; configuration lives in the PricingSettings step --></customElement>
  <name>__STEP_NAME__</name>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```

Whether the XML needs an empty `<customElement/>` is unconfirmed: build once in
Builder, retrieve the `ExpressionSetDefinition`, and copy the shape (unescape
HTML per `../../expression-sets/SKILL.md`).

## Shipped in this repo (snapshot)

None. `PricingSettings` steps in `RLM_DefaultPricingProcedure`,
`RLM_PRM_DISTI_Pricing_Procedure`, `RLM_Price_Distribution_Procedure`,
`RLM_ProductDiscoveryPricingProcedure` and `RLM_Revenue_Management_Recalc_Procedure`
carry `IsPropagationEnabled=false`. Snapshot only. Discover live:
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify

1. Simulate in Builder; propagation results are inspected in line-item logs and the JSON output (the logs component has a propagation-specific view). [Core]
2. Check a parent group total equals the sum of its qualifying children; check the sequence by confirming a later formula sees an earlier one's result.

## Troubleshooting

| Symptom / error | Cause | Fix |
|---|---|---|
| `LookUpName isn't a valid variable name` on save | Propagation enabled but table not configured | Configure and save the table first [Help] |
| Formula skipped | Null argument and Use Zero for Null off | Enable it or populate input [Help] |
| Wrong formula order | Duplicate/empty/stale sequence numbers | Renumber all formulas manually [Help] |
| Incorrect amend/renew totals | Unsupported transaction types | Use another procedure for those [Help] |
| Net unit price wrong under delta pricing | Propagation reads the delta value | Copy to a separate tag first [Help] |

## Open questions

- The Pricing Setting JSON key and shape for the propagation table: unknown; retrieve from a live Builder-built procedure.
- Exact placement constraint relative to Discount Distribution and the aggregate tail: Help silent; test live.
- The "Price Propagation Limits" Help article is partly echoed in the parent page; no disagreement found.
