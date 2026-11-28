# Price Propagation (`PricingPropagation`)

> Release 264 / API v68.0. Sources: `ind.pricing_price_propagation.htm`,
> `ind.pricing_configure_the_price_propagation_element.htm`,
> `ind.pricing_price_propagation_limits.htm`; shipped XML: none (the
> `IsPropagationEnabled=false` flag ships on `PricingSettings` steps); core source
> (behavior and, for the metadata shape, a test fixture).

Computes hierarchical values in a nested transaction (group > subgroup > line):
horizontal formulas run in a strict sequence on one node, and ascending
propagation rolls child values up to parents through a table configured in the
Pricing Setting element.

## When to use it

- Multilevel group-to-group or group-to-item hierarchies (Help example: Building > Floor > Room > Panel line items) with sequential formulas and child-to-parent rollups. [Help: ind.pricing_price_propagation]
- Do not use as a substitute for [Formula](./formula-based-pricing.md) or [Aggregate Price](./aggregate-price.md): it is designed for specific rollup logic. [Help: ind.pricing_price_propagation_limits]
- Contrast with Aggregate Roll Up: Roll Up adds child line prices to one parent line via a parent reference tag, one SUM-type function per section; Propagation uses a node/join/merged-attribute table, ordered horizontal formulas, and works across group levels. [inferred] Help states that propagation supports group-to-group and group-to-item relationships. [Help: ind.pricing_price_propagation]

## Configuration

Most configuration lives in the Pricing Setting element, not the Propagation step.

| Builder field | Parameter / storage | Type | Required | Notes |
|---|---|---|---|---|
| Pricing Setting > Enable Propagation | `IsPropagationEnabled` on the `PricingSettings` step | Literal `true`/`false` | yes | Ships `false` (see Shipped). |
| Configure Propagation Rules (table) | Literal parameters on the `PricingSettings` step (JSON string values; see Metadata shape) | JSON | yes when enabled | Save the table before saving the procedure, or save can fail with `LookUpName isn't a valid variable name`. [Help: ind.pricing_configure_the_price_propagation_element] |
| Add Nodes | table | | | Data sources and attributes, e.g. `SalesTransactionItem`, `SalesTransactionGroup`. [Help: ind.pricing_configure_the_price_propagation_element] |
| Join Nodes | table | | | Mapping Type Parent-Child; Parent Key (e.g. `GroupSource`); Child Key (e.g. `SalesTransactionItemGroup`); Node Identifier. [Help: ind.pricing_configure_the_price_propagation_element] |
| Merge Attributes | table | | | Merged attribute name, merged condition (e.g. Not Null), attributes 1 and 2. [Help: ind.pricing_configure_the_price_propagation_element] |
| Edit Attributes: horizontal formula | table | | | Column, formula, Sequence. Sequence required, not negative, unique; not auto-adjusted. [Help: ind.pricing_configure_the_price_propagation_element] |
| Use Zero for Null Values | table | | | On: null inputs treated as 0. Off: any formula with a null argument is skipped. [Help: ind.pricing_configure_the_price_propagation_element] |
| Ascending propagation | table | | | Merged attribute, aggregation `Sum`, child field (e.g. `Sum(!Child.ItemTotalCost)`), up to 3 conditions (e.g. `SellingModelType = 'One Time'`), all must match; non-matching or null items are excluded. [Help: ind.pricing_configure_the_price_propagation_element] |
| Table template | Builder | | no | Help offers template "Map sales SalesTransactionItem to SalesTransactionGroup" (predefined Sales Transaction Context) instead of a new table. [Help: ind.pricing_configure_the_price_propagation_element] |
| Price Propagation element | `actionType=PricingPropagation` | | | All configuration is in the Pricing Setting table. [Help: ind.pricing_configure_the_price_propagation_element] |

## Placement and ordering

- Build order: Pricing Setting (tick Enable Propagation, map common variables), configure and save the table, add the Propagation element, save and activate. Permission: Salesforce Pricing Design Time. [Help: ind.pricing_configure_the_price_propagation_element]
- Prerequisite: a context definition with the nested group hierarchy (e.g. Sales Transaction Context) and the mappings that link the procedure to it. [Help: ind.pricing_configure_the_price_propagation_element] See `../../context-service/SKILL.md`.
- Top-level only; not supported inside a ListGroup. [Help: ind.pricing_price_propagation_limits]
- Price Propagation can't use local list variables. [Help: ind.pricing_configure_pricing_procedure]
- Help does not state an absolute position. Core test fixtures include start-of-procedure and end-of-procedure placements [Core: pricing propagation functional-test fixture, 264]; in a procedure that has a Discount Distribution Service step the end placement is rejected (see Measured below). Cross-element rules and the save-time errors: [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md#save-time-procedure-rules-core-enforces).
- With delta pricing enabled, copy `NetUnitPrice` into a separate tag before the element and use that tag in the table and formulas. [Help: ind.pricing_price_propagation_limits]

## Rules and limits

| Rule | Source |
|---|---|
| One Price Propagation element per procedure. Save error: `Only one Pricing Propagation element is allowed in the pricing procedure. The presence of any other Pricing Propagation element is not Allowed.` | [Core: pricing procedure save validator, 264] |
| Not allowed inside a List Group (List Container). Save error: `Pricing Propagation element is not allowed in List Container element in the pricing procedure.` | [Core: pricing procedure save validator, 264] |
| Must stay in sync with Pricing Setting > Enable Propagation, in both directions. Enabled with no element: `You must add Pricing Propagation element when propagation is enabled in the Pricing Settings element.` Element present, not enabled: `You must select Enable Propagation in the Pricing Settings element when the Pricing Propagation element is added.` | [Core: pricing procedure save validator, 264] |
| Help names Derived Pricing, Map Line Item and Promotions elements as incompatible in the same procedure. | [Help: ind.pricing_price_propagation_limits] |
| Map Line Item is `BreakdownLineMapping`, which the repo default ships. Core checks `PromotionExecution`, not `GPMPromotionExecution`; `AdvancedPromotionExecution` only for the Communications subtype. Save error: `Pricing Propagation element is not allowed with incompatible elements in the pricing procedure.` | [Core: pricing procedure save validator, 264] |
| A procedure containing Price Propagation runs sequentially: core marks the element not eligible for parallel execution, and one ineligible element makes the whole procedure sequential (see [../runtime-and-observability.md](../runtime-and-observability.md)). | [Core: pricing propagation runtime, 264] |
| Do not use in amend, renew or cancel pricing procedures (inaccurate pricing). | [Help: ind.pricing_price_propagation_limits] |
| Existing procedure must not already contain propagation, derived price or promotion elements before enabling. | [Help: ind.pricing_configure_the_price_propagation_element] |
| Deselecting Enable Propagation keeps the configuration in the Pricing Setting step; to reset, remove and re-add the Pricing Setting element. | [Help: ind.pricing_price_propagation_limits] |
| `PricingPropagation` is available from API v65.0 (Release 258). | [Dev guide: meta_expressionsetdefinition] |

## Metadata shape

Shape source: a core functional-test fixture, a Tooling-API representation of a procedure with one `PricingSettings` step and one `PricingPropagation` step (core 264). [Core: pricing propagation functional-test fixture, 264]

- The `PricingPropagation` step is `stepType` `BusinessKnowledgeModel` with a `customElement` of three Literal parameters: `sectionCount=0`, `selectedFunction=Get`, `IsRealTime=false`. It carries nothing else. [Core: pricing propagation functional-test fixture, 264]
- The propagation table is not on that step. It sits in the `PricingSettings` step's `customElement` as extra Literal parameters, whose values are JSON strings (XML-escape them in metadata). [Core: pricing propagation functional-test fixture, 264]

| Parameter on the `PricingSettings` step | Value |
|---|---|
| `IsPropagationEnabled` | Literal `true` |
| `nodes` | JSON array of `{name, dataPath, waterfallIdentifier}`, e.g. `SalesTransactionItem` (`SalesTransaction/SalesTransactionItem`, identifier `LineItem`) and `SalesTransactionGroup` (identifier `GroupSource`) |
| `columnNames`, `tags` | JSON arrays of the table's column names (`$Tag`) and the tag names |
| `join` | JSON object: `{type: parentChildRelationship, parentAttributeName, parentNodeName, childNodes: [{childAttributeName, childNodeName}, ...]}` |
| one parameter per column, named `$<Tag>` | JSON object `{name, dataType, dataPath, fieldType (INPUT or INPUTOUTPUT), parentNode, horizontalFormula, verticalBTFormula, verticalTBFormula}`; each formula field is an array of `{formulaExpression, tagsUsedInFormula}` objects |
| merged column | `{name, dataType, mergedFields: [<item tag>, <group tag>], merged: true, mergeCondition: not_null, verticalBTFormula: [{formulaExpression: "Sum ( ! Child )"}]}`; a top-to-bottom column uses `verticalTBFormula: [{formulaExpression: "Copy ( ! Parent )"}]` |

The fixture's sample table rolls item net totals up to the group (merged `NetPrice`, `TotalPrice`), copies group margin down to items (merged `Margin`), and recomputes item and group totals with horizontal formulas. [Core: pricing propagation functional-test fixture, 264]

The fixture names the steps `PricingSetting` and `PricingPropagation`, with Pricing Setting first. [Core: pricing propagation functional-test fixture, 264]

```xml
<steps>
  <actionType>PricingPropagation</actionType>
  <customElement><!-- three Literal parameters: sectionCount, selectedFunction, IsRealTime --></customElement>
  <name>__STEP_NAME__</name>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```

## Shipped in this repo (snapshot)

No `PricingPropagation` step in any procedure under `force-app`, `post_procedureplans` or `post_prm_pricing`. `IsPropagationEnabled=false` (seq 1 Pricing Settings step, Literal) ships in `RLM_DefaultPricingProcedure` and `RLM_ProductDiscoveryPricingProcedure` [Repo: force-app/main/default/expressionSetDefinition], `RLM_Revenue_Management_Recalc_Procedure` and `RLM_Price_Distribution_Procedure` [Repo: unpackaged/post_procedureplans/expressionSetDefinition], and `RLM_PRM_DISTI_Pricing_Procedure` [Repo: unpackaged/post_prm_pricing/expressionSetDefinition]. The Pricing Setting step is `PricingSetting` in `RLM_Price_Distribution_Procedure` and `RLM_ProductDiscoveryPricingProcedure`, and `Mapcontexttagstocommonpricingvariables` in `RLM_Revenue_Management_Recalc_Procedure`. No other procedure carries it. Snapshot only. Discover live:
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify

1. Simulate in Builder; propagation results are inspected in line-item logs and the JSON output (the logs component has a propagation-specific view). [Core: pricing propagation runtime, 264]
2. Check a parent group total equals the sum of its qualifying children; check the sequence by confirming a later formula sees an earlier one's result.

## Troubleshooting

| Symptom / error | Cause | Fix |
|---|---|---|
| `LookUpName isn't a valid variable name` on save | Propagation enabled but table not configured | Configure and save the table first [Help: ind.pricing_configure_the_price_propagation_element] |
| Formula skipped | Null argument and Use Zero for Null off | Enable it or populate input [Help: ind.pricing_configure_the_price_propagation_element] |
| Wrong formula order | Duplicate/empty/stale sequence numbers | Renumber all formulas manually [Help: ind.pricing_configure_the_price_propagation_element] |
| Incorrect amend/renew totals | Unsupported transaction types | Use another procedure for those [Help: ind.pricing_price_propagation_limits] |
| Net unit price wrong under delta pricing | Propagation reads the delta value | Copy to a separate tag first [Help: ind.pricing_price_propagation_limits] |
| `MISSING_UNIQUE_IDENTIFIER_ERROR`, `UNIQUE_IDENTIFIER_NULL_ERROR` | A propagation node has no unique-identifier attribute, or its value is null | Tag a non-null unique id on each propagation node [Core: pricing propagation runtime, 264] |
| `DUPLICATE_PROPAGATION_ITEMS_ERROR` | Two items on a node share a unique id | Make ids unique per node [Core: pricing propagation runtime, 264] |
| Save error `Pricing Propagation element is not allowed with incompatible elements...` | Derived Price, Promotion Execution or Map Line Item (`BreakdownLineMapping`) in the same procedure | Remove the other element, or do not use propagation [Core: pricing procedure save validator, 264] |
| Save error `You must select Enable Propagation...` / `You must add Pricing Propagation element...` | Pricing Setting flag and the element disagree | Align them [Core: pricing procedure save validator, 264] |
| `LINE_ITEM_DELETED_IN_CONTEXT` | A changed item was deleted from the context mid-run | Item is reported as an error on its step detail; rerun [Core: pricing propagation runtime, 264] |

## Runtime behavior

- The step reads changed items from the context change list and builds change sets for propagation items. Only changed tags whose column in the propagation table is Number, Percent or Currency are eligible. [Core: pricing propagation runtime, 264]
- When the procedure setting that ignores the change set is off and the context has no change list, the run fails with `IGNORE_CHANGE_SET_ERROR`. With that setting on, a separate sequential propagation path runs instead. [Core: pricing propagation runtime, 264]

## Measured

Procedure with Propagation on: a copy of the default procedure with `IsPropagationEnabled=true`, a small table (item and group nodes, parent-child join, one merged top-to-bottom column) and a `PricingPropagation` step placed right after the Pricing Setting step, created through the Connect expression-set POST (`import_expression_set.py`).

- The Connect create accepted the table in the Metadata shape above. [Measured: 2026-11-27, 264, scratch org built from main]
- The save error `Pricing Propagation element is not allowed with incompatible elements` came from the default's `BreakdownLineMapping` step; the copy saved once that step was removed. [Measured: 2026-11-27, 264, scratch org built from main]
- With the Propagation step placed second, after the Pricing Setting step, the copy saved. With it last, the save failed with `You can add the Discount Distribution Service element only before the Rounding Rules and Aggregate elements...`, the Discount Distribution ordering rule in [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md) (Rule 1). [Measured: 2026-11-27, 264, scratch org built from main]
- Variables for merged columns that are not context tags were accepted as Constants in the `variables` list. [Measured: 2026-11-27, 264, scratch org built from main]
- The create was accepted with top-level `sequenceNumber`s renumbered contiguously from 1. [Measured: 2026-11-27, 264, scratch org built from main]
- A metadata deploy of a new `ExpressionSetDefinition` (dry run, real deploy, or an unmodified clone of the default) failed; the Connect POST worked. [Measured: 2026-11-27, 264, scratch org built from main]
- Activating that procedure version with the activation script, `--no-cascade`, succeeded and touched only the expression-set version (no procedure-plan changes). [Measured: 2026-11-27, 264, scratch org built from main]
- A headless pricing request against the activated copy returned Completed with no errors, and net prices equalled the default's. [Measured: 2026-11-27, 264, scratch org built from main]
- A headless request needs the header `Pricebook` and `CurrencyIsoCode`; without them `ListPrice` comes back empty and net is 0. [Measured: 2026-11-27, 264, scratch org built from main]
- A headless request does not run the Propagation step: the waterfall has no propagation entry (`ignoreChangeSet` is true and there is no change list). [Measured: 2026-11-27, 264, scratch org built from main]
- On a real quote with a group Discount of 10 and two lines, the default procedure priced each line at the list price less 10 percent (list 3899, `NetUnitPrice` 3509.1, line Discount 10). [Measured: 2026-11-27, 264, scratch org built from main]
- After switching the Revenue Settings pricing procedure to the copy and a Force reprice, the same lines priced at 3509.1 again, and the waterfall contained a `PricingPropagation` step whose output was `propagationId` only. [Measured: 2026-11-27, 264, scratch org built from main]
- With this table propagation ran and did not change net prices; the group discount already reaches lines under the default procedure. [Measured: 2026-11-27, 264, scratch org built from main]
- The Revenue Settings pricing procedure is switched with the Robot setup suite `configure_revenue_settings`, which picks the procedure by its Name label. [Measured: 2026-11-27, 264, scratch org built from main]

## Open questions

- Whether any table makes a propagated group discount change line net prices beyond the default behavior. Check: reprice a quote under the copy with a table that propagates a group value onto lines the default does not discount, and compare line `NetUnitPrice` with the default.
- Whether dropping `BreakdownLineMapping` changes breakdown lines on orders. Check: place an order from a quote priced by the copy and one priced by the default and compare `OrderItemDetail` rows; the copy also has propagation on, so repeat with a copy that only drops `BreakdownLineMapping`.
- Why a metadata deploy of a new `ExpressionSetDefinition` fails on a fresh scratch org. Check: deploy an unmodified clone of the default with --dry-run on a second fresh scratch org and read the error.
- Whether the fixture's tags and nodes (`SalesTransactionGroup`, `GroupSource`, `ParentSalesTransactionItemGroup__std`, the `Group*__std` columns) resolve against this repo's sales transaction context. Check: describe the repo context definition for those tags and nodes.
- Whether other placements between the Pricing Setting step and Discount Distribution save and price the same. Check: create variants with the Propagation step at other positions before Discount Distribution and reprice.
