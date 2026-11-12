# Rounding Values (`RoundingValues`)

> Release 264 / API v68.0. Sources: `ind.pricing_apply_the_rounding_values_element.htm`,
> `ind.pricing_rounding_values.htm` (rating twins: `ind.rm_element_rounding_values.htm`,
> `ind.rm_element_add_rounding_values.htm`); dev guide `meta_expressionsetdefinition.htm`
> (actionType enum); shipped XML: none; core source (behavior only); a step created and run on a
> fresh 264 `ent-sb0` scratch org on 2026-11-11 (multicurrency, USD and EUR).

Rounds the value of one or more pricing variables (up, down or half-up) to a
number of decimal places, writing the result to an output variable.

## When to use it
- Use to make price outputs (e.g. `ItemNetTotalPrice`) land on the currency's decimal places or a fixed precision after formulas/discounts [Help].
- Also finalises currency outputs of preceding elements such as Manual Discount and Volume Discount [Help].
- Do not use rating-side rounding here: rating procedures use the separate `RatingRoundingValues` actionType [Dev guide enum][Core].
- Not shipped in this repo: no shipped procedure has a `RoundingValues` step, yet the DDS ordering error names "Rounding Rules" [Repo; see Placement].

## Configuration
| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Precision (Fixed Input Variable) | `Precision` | `Parameter` (Numeric, optional) | single-currency only | Decimal places, read as integer. Absent or non-numeric: value returned unchanged, no error [Help][Core] |
| Input Variable (row N) | `section-{N-1}-input1` | `Parameter` | yes | Value to round. Core declares these as Currency inputs only [Core] |
| Rounding Rule (row N) | `section-{N-1}-input2` | `Literal` | yes | `roundUp`, `roundDown`, `halfUp` [Core]; Builder: Round Up / Round Down / Half Up [Help] |
| Output Variable (row N) | `section-{N-1}-output` | `Parameter` | yes | Receives rounded value; Currency only [Core] |
| (row count) | `sectionCount` | `Literal` | yes | Number of rounding rows [Core] |
| Hide in waterfall | `HideWaterfall` | `Literal` | no | Excluded when rules are read [Core] |
| Currency | `CurrencyIsoCode` | — | **refused** | Creating the step with a `CurrencyIsoCode` parameter failed: "CurrencyIsoCode isn't a valid variable name" (`INVALID_INPUT`). Without it, the step rounded USD and EUR lines to 2 places [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]. The currency comes from the context, not a step parameter (Rules and limits) |

Parameter names, the Currency data type and the three rule strings come from core. Builder metadata for this element also enables Hide in Waterfall, lookup selection, profile filter and additional variables [Core]. The mapping to rounding modes is `roundUp` = away from zero, `roundDown` = toward zero (truncate), `halfUp` = half rounds away from zero [Core].

## Placement and ordering
- Help example places it outside the List Group, after the formula that produces the value [Help].
- It belongs to the closing tail with DDS and the aggregate steps. When a procedure has a DDS, core rejects any step after it other than Aggregate Price or Rounding Values: "You can add the Discount Distribution Service element only before the Rounding Rules and Aggregate elements or you can make it the only element in a pricing procedure." [Core]. Place Rounding Values after DDS and after the price calculations it rounds.
- Position relative to aggregates (round before or after summing) changes totals: sum of already-rounded lines vs rounding the sum. Core enforces neither order, so pick the one you need. See [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).
- No `FormulaBasedPricing` after DDS: see [formula-based-pricing](./formula-based-pricing.md).
- Rounding mid-procedure, before a negotiated (manual) discount, when a source requires it: see
  [commitment-term-discount → Rounding before a negotiated discount](./commitment-term-discount.md#rounding-before-a-negotiated-discount).
  A step at that position ran (Rules and limits); its effect on the manual discount was not measured.

## Rules and limits
- Measured step (2026-11-11, multicurrency org): one row, `NetUnitPrice` → `NetUnitPrice`,
  `halfUp`, no `Precision` and no `CurrencyIsoCode`, as a top-level step right after the
  non-contract volume discount group. USD and EUR nets landed on 2 places
  [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org].
- Single-currency org: uses the `Precision` input; if none is passed the value is returned unchanged [Help][Core]. Core only accepts a numeric tag value; anything else leaves precision unset, and the value passes through without an error [Core].
- Multicurrency org: ignores `Precision`; uses decimal places from Manage Currencies for the currency in `CurrencyIsoCode` context, else each currency's own setting [Help][Core].
- In a multicurrency org Help says the user's personal currency setting determines the currency code used, not the context currency parameter. Core uses the `CurrencyIsoCode` tag when it has a value and falls back to the user's currency only when it is empty [Help][Core]. Help's `ind.pricing_apply_the_rounding_values_element` carries the user-currency note; `ind.pricing_rounding_values` agrees with core. Treat the live org as truth.
- Rule semantics [Help]: Round Up 1.60 to 2; Round Down 1.60 to 1; Half Up 1.45 to 1.50 (at the chosen precision).
- An unknown rule string fails with `SF-Pricing-00015: The rounding value specified isn’t valid. Enter a valid value and try again.` (API code `ROUNDING_VALUE_INCORRECT`, HTTP 400) [Core].
- Core derives the row count from the step's Literal constants other than `sectionCount` and `HideWaterfall`, so do not add any other Literal parameter to this step; it shifts the rule lookup [Core].
- A null input stays null [Core].
- Aborted (Stop Pricing), errored, skipped, ignored and tax-inclusive lines are not rounded: the shared line-selection rule excludes them for this element [Core].

## Feasibility / not supported
| Need | Answer |
|---|---|
| Round a non-currency value (text, integer quantity) | No: inputs and outputs are Currency [Core] |
| Different precision per row in a single-currency org | No: one `Precision` for the whole step; use two steps [Core] |
| Per-row precision in a multicurrency org | No: scale comes from the currency setting [Help][Core] |
| Rounding modes beyond up/down/half-up (half-even, banker's) | No: only the three strings are accepted [Core] |
| Pre-existing line totals rounded in rating | Use `RatingRoundingValues` in the rating procedure [Dev guide enum] |
| Place before DDS | Accepted, but DDS then rewrites the rounded prices, so the output is unrounded again [Core][inferred] |
| Round a value that a later step recalculates | Accepted, but the later value is unrounded; core checks no position for Rounding Values itself [Core] |

## Metadata shape
Skeleton built from the parameter names above (not from shipped XML or a saved step) [inferred]; placeholders marked. A step with the same parameter names minus `Precision`, plus `HideWaterfall` `false`, bound to `NetUnitPrice` → `NetUnitPrice` with `halfUp`, was created through an overlay and ran [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]:
```xml
<steps>
    <actionType>RoundingValues</actionType>
    <customElement>
        <parameters><input>true</input><name>Precision</name><output>false</output><type>Parameter</type><value>__PRECISION_VARIABLE__</value></parameters>
        <parameters><input>true</input><name>section-0-input1</name><output>false</output><type>Parameter</type><value>ItemNetTotalPrice</value></parameters>
        <parameters><input>true</input><name>section-0-input2</name><output>false</output><type>Literal</type><value>roundDown</value></parameters>
        <parameters><input>true</input><name>sectionCount</name><output>false</output><type>Literal</type><value>1</value></parameters>
        <parameters><input>false</input><name>section-0-output</name><output>true</output><type>Parameter</type><value>ItemNetTotalPrice</value></parameters>
    </customElement>
    <name>__STEPNAME__</name>
    <sequenceNumber>__N__</sequenceNumber>
    <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
Each parameter name appears once (`scripts/ai/validate_expression_set.py` rejects a duplicate name in one `customElement`). Create the precision value as a version variable: Resource Type Constant, Number, e.g. `PrecisionVariable` = 1 (Help example) [Help]. Overlay mechanics and activation: [../../expression-sets/SKILL.md](../../expression-sets/SKILL.md).

## Shipped in this repo (snapshot)
None. A count of `RoundingValues` across the three shipped procedure directories returns no matches [Repo]. Discovery: `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name>`.

## Verify
- Simulate; the waterfall shows a Rounding Values entry and the rounded Net Amount at the chosen decimal [Help].
- Compare persisted line totals via SOQL against expected scale.

## Troubleshooting
| Symptom / error | Cause | Fix |
|---|---|---|
| Value not rounded, no error shown | Single-currency org and no/non-numeric `Precision` | Pass a numeric `Precision` constant |
| `Precision` seems ignored | Multicurrency org | Set decimal places in Manage Currencies |
| Wrong currency scale | User's currency used when `CurrencyIsoCode` absent | Pass `CurrencyIsoCode` in context, not as a step parameter; verify per Help note |
| `CurrencyIsoCode isn't a valid variable name` (`INVALID_INPUT`) at create | A `CurrencyIsoCode` parameter on the step | Drop the parameter [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org] |
| `You can add the Discount Distribution Service element only before the Rounding Rules and Aggregate elements ...` | A step other than Aggregate Price or Rounding Values is ordered after DDS | Move that step before DDS (the message names DDS, not the offending step); see [discount-distribution-service](./discount-distribution-service.md) and ordering rule [Core] |
| `SF-Pricing-00015: The rounding value specified isn’t valid.` | Rule string is not `roundUp`/`roundDown`/`halfUp` | Fix the literal [Core] |
| Rule applied to the wrong row | Extra Literal parameter on the step | Remove it [Core] |

## Help coverage
`ind.pricing_rounding_values` (rules, single- vs multi-currency, preceding-element outputs) and `ind.pricing_apply_the_rounding_values_element` (example, precision constant) are reflected above. The rating twins describe `RatingRoundingValues`, which is outside this file.

## Open questions
- Whether the skeleton matches a Builder-saved step (flags, `sectionCount` encoding); needs a sample from a live org.
- Help vs core on currency source: the two Help articles disagree with each other (one matches core, one says the user's currency wins); follow core and verify on a live org.
