# Formula-Based Pricing (`FormulaBasedPricing`)

> Release 264 / API v68.0. Sources: `ind.pricing_formula_based_pricing.htm`;
> dev guide `meta_expressionsetdefinition.htm` (actionType enum); shipped XML:
> `RLM_DefaultPricingProcedure`, `RLM_PRM_DISTI_Pricing_Procedure`,
> `RLM_Revenue_Management_Recalc_Procedure`; core source (parameters, limits).

Evaluates up to five formulas in one element and writes each result to an
output variable (a context tag). Used for line math: totals, cost, margin,
unit-price derivations.

## When to use it
- Use for arithmetic or `IF`/`ISNULL` logic over variables already on the line (price, quantity, custom fields).
- Use several formulas in one element when they belong to the same scenario; each has its own output.
- Do not use for grouping/summing across lines: use Aggregate Price (`GroupingAndAggregatePricing`).
- Do not use for a plain copy of a value: use [Assignment](./assignment.md).
- Does not support derived products on quote line items [Help].

## Configuration
| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Formula N (N = 1..5) | `formula-section-{N-1}-input` | `Formula` | yes | Expression text; 0-based index. `input=true`. Required for every index below `formulaSectionCount`, optional above it. Max five [Help][Core] |
| Output variable N | `formula-section-{N-1}-output` | `Parameter` | yes | Target tag/variable; `output=true`. Same index as the formula. Declared as Currency in core metadata [Repo][Core] |
| (formula count) | `formulaSectionCount` | `Literal` | yes | Number of formulas, e.g. `3` [Repo] |
| (function) | `selectedFunction` | `Literal` | yes | Always `Get` in shipped XML [Repo]. Core's formal parameters for this element do not read it; write `Get` and treat it as a fixed marker [Core] |
| (legacy section count) | `sectionCount` | `Literal` | yes | Shipped as `0` in every step [Repo] |
| Hide in waterfall | `HideWaterfall` | `Literal` | yes | `false` shipped [Repo] |
| Real time | `IsRealTime` | `Literal` | yes | `false` shipped [Repo]. Core does not declare it as a parameter of this element and only lookup-backed elements read it; write `false` as shipped and treat it as inert here [Core][inferred] |
| Output Variable | `Output Variable` | `Parameter` | no | Legacy single-formula output kept for backward compatibility; core still registers it as an optional output. New steps use `formula-section-0-output`; keep it only when copying an older step [Repo][Core] |
| (write back) | `writeBackData` | `Literal` | no | `[]` in some steps [Repo]. Core's formal parameters for this element do not include it; leave `[]` or omit [inferred]. Searched core rules-engine metadata and runtime for `writeBackData`: no handler found; it appears as `[]` in 2 shipped procedures (PRM, Recalc) [Repo] |

Operators and functions: Help points to "Operators and Functions in Expression Sets" (not in the snapshot) [Help]. Shipped XML uses `+ - * /`, `IF` and `ISNULL` only (one `IF ( ISNULL (` formula in the PRM procedure); `ROUND` and `NOTNULL` do not appear in any shipped procedure [Repo]. Core rewrites `ROUND(`, `ISNULL(` and `ISNOTNULL(` (case-insensitive, `(` after optional spaces) to its own engine variants before validating and loading a formula [Core]; the null-check function is `ISNOTNULL`, and `NOTNULL` is not rewritten, so do not rely on it [Core]. A formula that is exactly one list function (SUM, AVG, MIN, MAX) over a multi-value tag aggregates that line's child values [Core]. Results are computed at scale 16; a `Percent` output is multiplied by 100, and a formula that is just a single `Percent` tag returns that tag divided by 100 [Core]. The Expression field holds 4,000 characters; a formula longer than that fails to save [Core].

## Placement and ordering
- There is no scope parameter. The element always iterates line items; each line's formula reads that line's tags plus the tags of its parent nodes (for example header tags) [Core]. A top-level step (no `parentStep`) runs for every line, as in the Help walkthrough, which adds it right after List Price and prices each line from `ListPrice` and `LineItemQuantity` [Help]. A `ListGroup` parent only narrows which lines run; it does not turn line tags into header tags [Core].
- What makes a result line or header is the context node of the tags you read and write, not the placement. Line tags in, line tags out gives one value per line. A formula that writes a header-node tag is evaluated once per line, so it is only well defined when its inputs are identical on every line [inferred]. To combine lines, use Aggregate Price.
- Every shipped formula step sits inside a ListGroup and before DDS [Repo].
- Lines already stopped by [Stop Pricing](./stop-pricing.md) or in error are skipped; tax-inclusive lines are not skipped by this element [Core].
- Formulas inside one element evaluate in section order; a later formula can read an earlier formula's output (Help example chains `ItemNetTotalPrice` then `ItemDiscountAmount`) [Help].
- **Tail rule** (full rule owned by [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md)): in a procedure with a Discount Distribution Service (DDS), only Aggregate Price and Rounding Values steps may follow it, so a `FormulaBasedPricing` step after DDS is rejected [Core]. A procedure without DDS has no such check: the shipped PRM and Recalc procedures end with an Assignment after their aggregates [Repo]. Summary for a procedure with DDS:
  - The rejection error is misleading: it names DDS (`You can add the Discount Distribution Service element only before the Rounding Rules and Aggregate elements`), not your formula step [Repo]; ordering rules in [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).
  - A formula before the tail is accepted. It lags one reprice cycle only when its operand is produced by a step that runs later in the procedure (in practice an aggregate in the closing block): it then reads the value hydrated from the record at reprice start [Live, repo owner]. Operands produced by earlier steps are fresh.
  - So with DDS, a formula over aggregate outputs has no slot that is both accepted and fresh. Use an earlier derivation/aggregate step or a Salesforce formula field. Without DDS, a formula after the aggregates passes the save check [Core]; Simulate it before relying on it [inferred].

## Rules and limits
- Legacy form: with `formulaSectionCount` absent or `0`, core evaluates one formula and writes `Output Variable` [Core]. New steps set the count.
- Max five formulas per element [Help][Core: five input slots are generated]. Builder offers Hide in waterfall and profile filter for this element; no lookup [Core].
- A formula referencing a custom field only works if the field exists on the source object and is mapped (tag) into the bound context definition. The overlay cannot create it; the example overlay records this under `externalDependencies` (`docs/references/expression-set-overlay-examples/facility-quantity.overlay.example.json`). Standard `__std` and unsuffixed tags come from the standard context definition [Repo]. See [../../context-service/SKILL.md](../../context-service/SKILL.md).
- The formula string is plain text inside the parameter `value`. Save validates it: a formula that does not parse or type-check is rejected with `Specify a valid formula for the {0} step. {1}` (or `Specify a valid expression for the {0} step. {1}` on a type mismatch, {1} being the engine detail) [Core]. A formula longer than 4,000 characters (the Expression field's maximum length) is rejected (`LIMIT_EXCEEDED`) with `The expression at {0} reached the limit. Simplify or split the formula, and try again.` [Core]. A tag removed after save breaks at runtime (inferred). A formula that cannot be evaluated puts that line in error with `INVALID_FORMULA` ("We couldn’t simulate the pricing procedure because the formula entered in the Calculation Formula input variable was incorrect. Enter a valid formula and try again.") and the output is null [Core]. Null operands are passed to the formula engine as null (core counts and logs them), so guard with `ISNULL` [Core].
- Assignments are per line within the filtered list; nothing persists to the database from the element itself.

## Metadata shape
Line-scope, three formulas, from the shipped cost/margin step (child of a ListGroup/filter pair):

```xml
<steps>
    <actionType>FormulaBasedPricing</actionType>
    <customElement>
        <parameters><input>true</input><name>formula-section-0-input</name><output>false</output>
            <type>Formula</type><value>ItemUnitCost__std * LineItemQuantity</value></parameters>
        <parameters><input>true</input><name>formula-section-1-input</name><output>false</output>
            <type>Formula</type><value>( ItemNetTotalPrice - ( ItemUnitCost__std * LineItemQuantity ) ) / ItemNetTotalPrice</value></parameters>
        <parameters><input>true</input><name>formula-section-2-input</name><output>false</output>
            <type>Formula</type><value>ItemNetTotalPrice - ( ItemUnitCost__std * LineItemQuantity )</value></parameters>
        <parameters><input>true</input><name>formulaSectionCount</name><output>false</output><type>Literal</type><value>3</value></parameters>
        <parameters><input>true</input><name>selectedFunction</name><output>false</output><type>Literal</type><value>Get</value></parameters>
        <parameters><input>true</input><name>sectionCount</name><output>false</output><type>Literal</type><value>0</value></parameters>
        <parameters><input>true</input><name>HideWaterfall</name><output>false</output><type>Literal</type><value>false</value></parameters>
        <parameters><input>true</input><name>IsRealTime</name><output>false</output><type>Literal</type><value>false</value></parameters>
        <parameters><input>false</input><name>formula-section-0-output</name><output>true</output>
            <type>Parameter</type><value>ItemTotalCost__std</value></parameters>
        <parameters><input>false</input><name>formula-section-1-output</name><output>true</output>
            <type>Parameter</type><value>ItemMargin__std</value></parameters>
        <parameters><input>false</input><name>formula-section-2-output</name><output>true</output>
            <type>Parameter</type><value>ItemMarginAmount__std</value></parameters>
    </customElement>
    <label>Calculate total cost and margin</label>
    <name>Calculatetotalcostandmargin</name>
    <parentStep>Calculatecostandmarginforpricedlines</parentStep>
    <sequenceNumber>2</sequenceNumber>
    <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
Conventions: `stepType` is `BusinessKnowledgeModel` with `actionType` `FormulaBasedPricing`; `sequenceNumber` is per parent; keep `formulaSectionCount` equal to the number of input/output pairs (indexes contiguous from 0) (inferred). Connect JSON uses the same parameter names; lifecycle: [../../expression-sets/SKILL.md](../../expression-sets/SKILL.md).

## Shipped in this repo (snapshot)
| Procedure | Step (parent group, seq) | What it does |
|---|---|---|
| Default | `Calculatetotalcostandmargin` (`Calculatecostandmarginforpricedlines`, 2) | 3 formulas: total cost, margin %, margin amount |
| Default, PRM, Recalc | `Calculateitemnettotalpriceforlineswithlasttransactionpricing` (`Filterlineswithlasttransactionpricingandassignnettotalprice`, 2) | `NetUnitPrice * LineItemQuantity` to `ItemNetTotalPrice` |
| Default, PRM, Recalc | `Calculateitemnettotalpriceforlineswithoutderivedorlasttrxnpricing` (`Calculateitemnettotalpriceforlineswithoutderivedpricing`, 3) | line total from input unit price |
| PRM, Recalc | `Uplift` (`Applyupliftstorampedsubscriptionsitemsduringamendment`, 2) | ramp uplift on amendment |
| PRM | `CalculatePartnerUnitPrice` (`AssignPartnerUnitPrice`, 2) | `IF ( ISNULL ( RLM_Distributor_Unit_Price__c ) , ...` over `PartnerDiscountPercent` |
| PRM | `CalculateDistributorUnitPrice` (`AssignDistributorUnitPrice`, 2) | `NetUnitPrice - ( NetUnitPrice * RLM_Distributor_Discount_Percent__c )` |
| PRM | `ConvertDistributorDiscountPercenttoDecimal` (`NormalizeDistributorDiscountPercent`, 2) | percent to decimal |
| PRM | `CalculatePartnerNetTotalPrice` (2), `CalculateMarginfromPartnerTotalPrice` (3), both under `AssignPartnerTotalCostandMargin` | partner totals and margin |

Total 14 steps: Default 3, PRM distributor 8, Recalc 3 (counted from the XML). Parents are List Group/filter steps; sequence numbers are per parent (checked against the XML).

Snapshot; refresh with `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`.

## Verify
- Builder Simulate: the price waterfall lists each formula and result [Help].
- JSON output: the output variable key holds the value.
- Persisted field: SOQL on the mapped field (e.g. `ItemMargin__std` target) after a reprice; compare twice to catch stale-operand lag.

## Troubleshooting
| Symptom / error | Cause | Fix |
|---|---|---|
| `INVALID_INPUT: You can add the Discount Distribution Service element only before the Rounding Rules and Aggregate elements` on adding a formula | Formula step placed after DDS (any step but Aggregate Price or Rounding Values) | Move it before DDS; see [ordering rule](../procedure-anatomy-and-ordering.md) |
| Formula off by one reprice | An operand is produced by a later step (aggregate in the closing block), so it is the prior reprice's value | Compute earlier or use a record formula field |
| `INVALID_FORMULA` on a line | Formula does not evaluate (bad function, type mismatch, missing tag) | Fix the expression; test in Simulate |
| Formula fails or null on custom field | Field not mapped into the context definition | Add field + tag mapping, then redeploy |
| Sixth formula rejected/ignored | Limit of five | Split into a second element |

## Help vs core
- Help vs core: Help says up to five formulas, but its example table lists six rows; core generates five slots, so treat five as the limit. Help also labels the fields "Calculation Formula"/"Output Variable" (older single-formula layout) while metadata uses `formula-section-N-*`. Help's `ItemProductAmount` row is a plain tag copy, not a formula.

## Open questions
- `IsRealTime` and `writeBackData` semantics on this element: no handler found in core (searched `writeBackData`); they look inert as shipped. Confirm live only if you need non-default values.
