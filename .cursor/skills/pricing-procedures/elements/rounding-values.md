# Rounding Values (`RoundingValues`)

> Release 264 / API v68.0. Sources: `ind.pricing_apply_the_rounding_values_element.htm`,
> `ind.pricing_rounding_values.htm`; dev guide `meta_expressionsetdefinition.htm`
> (actionType enum); shipped XML: none; core source (behavior only).

Rounds the value of one or more pricing variables (up, down or half-up) to a
number of decimal places, writing the result to an output variable.

## When to use it
- Use to make price outputs (e.g. `ItemNetTotalPrice`) land on the currency's decimal places or a fixed precision after formulas/discounts [Help].
- Also finalises currency outputs of preceding elements such as Manual Discount and Volume Discount [Help].
- Do not use rating-side rounding here: rating procedures use `RatingRoundingValues` [Dev guide enum].
- Not shipped in this repo: no shipped procedure has a `RoundingValues` step, yet the DDS ordering error names "Rounding Rules" [Repo; see Placement].

## Configuration
| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Precision (Fixed Input Variable) | `Precision` | `Parameter` (Numeric, optional) | single-currency only | Decimal places; read as integer. If absent, value returned unchanged [Help][Core] |
| Input Variable (row N) | `section-{N-1}-input1` | `Parameter` | yes | Value to round. Currency only: the element declares these as Currency inputs [Core] |
| Rounding Rule (row N) | `section-{N-1}-input2` | `Literal` | yes | `roundUp`, `roundDown`, `halfUp` [Core]; Builder: Round Up / Round Down / Half Up [Help] |
| Output Variable (row N) | `section-{N-1}-output` | `Parameter` | yes | Receives rounded value; Currency only [Core] |
| (row count) | `sectionCount` | `Literal` | yes | Number of rounding rows [Core] |
| Hide in waterfall | `HideWaterfall` | `Literal` | no | Other constants are ignored when reading rules [Core] |
| Currency | `CurrencyIsoCode` | `Parameter` | no | Optional tag; picks the currency's scale in multicurrency orgs [Core][Help] |

Parameter names and data types come from core formal parameters (`Precision` Numeric optional; section inputs and outputs Currency). Not shipped, so the exact `input`/`output` XML flags are the standard convention (inferred). Builder metadata for this element also enables Hide in Waterfall, lookup selection and additional variables. [Core]

## Placement and ordering
- Help example places it outside the List Group, after the formula that produces the value [Help].
- It belongs to the closing tail with DDS and the aggregate steps: DDS must come before Rounding Rules and Aggregate elements [Repo: DDS error text]. Place Rounding Values after DDS and the price calculations it rounds.
- Position relative to aggregates (round before or after summing) matters for totals: aggregate sums of already-rounded line values vs rounding the sum. Not documented; check live. See [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).
- No `FormulaBasedPricing` after the tail: see [formula-based-pricing](./formula-based-pricing.md).

## Rules and limits
- Single-currency org: uses the `Precision` input; if none is passed the value is returned unchanged [Help]. Core reads `Precision` only if it is a number; otherwise no precision is found, an error is logged and the line is not rounded [Core].
- Multicurrency org: ignores `Precision`; uses decimal places from Manage Currencies for the currency in `CurrencyIsoCode` context, else each currency's own setting [Help][Core].
- In a multicurrency org the user's personal currency setting determines the currency code used for rounding, not the context currency parameter [Help]. Core falls back to the user's currency when `CurrencyIsoCode` is empty [Core]. Help and core read slightly differently here: Help says the personal setting overrides the context value, core uses the tag when present. Treat the live org as truth.
- Rule semantics [Help]: Round Up 1.60 to 2; Round Down 1.60 to 1; Half Up 1.45 to 1.50 (at the chosen precision).
- Unknown rule string throws an error [Core].
- A null input stays null (inferred from core null handling).

## Metadata shape
Skeleton built from core parameter names (not from shipped XML); placeholders marked:
```xml
<steps>
    <actionType>RoundingValues</actionType>
    <customElement>
        <parameters><input>true</input><name>Precision</name><output>false</output><type>Parameter</type><value>__PRECISION_CONSTANT__</value></parameters>
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
Create the precision value as a version variable: Resource Type Constant, Number, e.g. `PrecisionVariable` = 1 (Help example) [Help]. Overlay mechanics and activation: [../../expression-sets/SKILL.md](../../expression-sets/SKILL.md).

## Shipped in this repo (snapshot)
None. No `RoundingValues` step in any shipped procedure. Discovery: `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`.

## Verify
- Simulate; the waterfall shows a Rounding Values entry and the rounded Net Amount at the chosen decimal [Help].
- Unit tests in core cover 10.555 to 10.56 (half-up, scale 2) and 10.999 round-down at precision 0 to 10 [Core].
- Compare persisted line totals via SOQL against expected scale.

## Troubleshooting
| Symptom / error | Cause | Fix |
|---|---|---|
| Value not rounded, no error shown | Single-currency org and no/non-numeric `Precision` | Pass a numeric `Precision` constant |
| `Precision` seems ignored | Multicurrency org | Set decimal places in Manage Currencies |
| Wrong currency scale | User's currency used when `CurrencyIsoCode` absent | Pass `CurrencyIsoCode` in context; verify per Help note |
| `INVALID_INPUT: ... only before the Rounding Rules and Aggregate elements` | Misleading ordering error; real cause is a step after the tail | See [formula-based-pricing](./formula-based-pricing.md) and ordering rule |
| Rounding error on a line | Unrecognised rule string | Use `roundUp`, `roundDown` or `halfUp` |

## Open questions
- Whether the XML flags in the skeleton match a Builder-saved step; needs a sample from a live org.
- Whether the closing-tail position is enforced for Rounding Values itself and its order versus aggregates.
- Help vs core on currency source (see Rules).
