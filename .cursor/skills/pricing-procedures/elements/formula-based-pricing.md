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
| Real time | `IsRealTime` | `Literal` | yes | `false` shipped [Repo]. Not a formal parameter of this element in core; write `false` as shipped (inferred: common element flag) |
| Output Variable | `Output Variable` | `Parameter` | no | Legacy single-formula output kept for backward compatibility; core still registers it as an optional output. New steps use `formula-section-0-output`; keep it only when copying an older step [Repo][Core] |
| (write back) | `writeBackData` | `Literal` | no | `[]` in some steps [Repo]. Not a formal parameter of this element in core; leave `[]` or omit (inferred) |

Operators and functions: Help points to "Operators and Functions in Expression Sets".

## Placement and ordering
- Scope is set by `parentStep`, not a parameter. Top-level (no `parentStep`) = header scope; child of a `ListGroup` = line scope, running only for lines that passed the group's filter [Repo].
- Every shipped formula step is line scope, inside a ListGroup, before DDS [Repo].
- Formulas inside one element evaluate in section order; a later formula can read an earlier formula's output (Help example chains `ItemNetTotalPrice` then `ItemDiscountAmount`) [Help].
- **Tail rule** (full rule owned by [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md)): the procedure ends with a tail (Discount Distribution Service, aggregate steps, Rounding Rules). A `FormulaBasedPricing` step after the tail is rejected. Summary:
  - The rejection error is misleading: it names DDS (`You can add the Discount Distribution Service element only before the Rounding Rules and Aggregate elements`), not your formula step [Repo]; ordering rules in [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).
  - A top-level formula before the tail is accepted, but its operands are the values hydrated from the record at reprice start, so it lags one reprice cycle.
  - So a header formula over aggregate outputs has no slot that is both accepted and fresh. Use an earlier derivation/aggregate step or a Salesforce formula field.

## Rules and limits
- Max five formulas per element [Help][Core: five input slots are generated]. Builder offers Hide in waterfall and profile filter for this element; no lookup [Core].
- A formula referencing a custom field only works if the field exists on the source object and is mapped (tag) into the bound context definition. The overlay cannot create it; the example overlay records this under `externalDependencies` (`docs/references/expression-set-overlay-examples/facility-quantity.overlay.example.json`). Standard `__std` and unsuffixed tags come from the standard context definition [Repo]. See [../../context-service/SKILL.md](../../context-service/SKILL.md).
- The formula string is plain text inside the parameter `value`; the platform does not rewrite it. Renaming or removing a tag breaks it at runtime, not at save (inferred).
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
| Procedure | Step | What it does |
|---|---|---|
| RLM_DefaultPricingProcedure | `Calculatetotalcostandmargin` | 3 formulas: total cost, margin %, margin amount, for lines with unit cost |
| RLM_DefaultPricingProcedure | `Calculateitemnettotalpriceforlineswithlasttransactionpricing` | `NetUnitPrice * LineItemQuantity` to `ItemNetTotalPrice` |
| RLM_DefaultPricingProcedure | steps using `InputUnitPrice * LineItemQuantity` | line total from input unit price |
| PRM distributor / Recalc procedures | partner net total, `IF ( ISNULL ( RLM_Distributor_Unit_Price ...` | custom-field formulas (`RLM_*__c`) |

Snapshot; refresh with `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`.

## Verify
- Builder Simulate: the price waterfall lists each formula and result [Help].
- JSON output: the output variable key holds the value.
- Persisted field: SOQL on the mapped field (e.g. `ItemMargin__std` target) after a reprice; compare twice to catch stale-operand lag.

## Troubleshooting
| Symptom / error | Cause | Fix |
|---|---|---|
| `INVALID_INPUT: You can add the Discount Distribution Service element only before the Rounding Rules and Aggregate elements` on adding a formula | Formula step placed after the aggregate/DDS/rounding tail | Move before the tail; see [ordering rule](../procedure-anatomy-and-ordering.md) |
| Header formula off by one reprice | Operands hydrated from the prior reprice | Compute earlier or use a record formula field |
| Formula fails or null on custom field | Field not mapped into the context definition | Add field + tag mapping, then redeploy |
| Sixth formula rejected/ignored | Limit of five | Split into a second element |

## Open questions
- `IsRealTime` and `writeBackData` semantics on this element: core does not declare them as its parameters, so they look inert as shipped. Confirm live only if you need non-default values.
- Exact save-time validation of formula text unconfirmed (needs live check).
