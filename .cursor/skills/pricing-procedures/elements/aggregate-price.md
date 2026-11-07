# Aggregate Price (`GroupingAndAggregatePricing`)

> Release 264 / API v68.0. Sources: `ind.pricing_add_aggregate_price_element.htm`,
> `ind.pricing_use_the_aggregate_price_element.htm`,
> `ind.pricing_roll_up_pricing_using_the_aggregate_price_element.htm`; dev guide
> custom-element step/parameter shapes; shipped XML: `RLM_DefaultPricingProcedure`,
> `RLM_PRM_DISTI_Pricing_Procedure`, `RLM_Revenue_Management_Recalc_Procedure`;
> core source (behavior only).

Aggregates a context tag (SUM/AVG/MIN/MAX) across line items, optionally grouped
by up to 5 tags, or rolled up from child lines to a parent line, and writes the
result to an output context tag. Results do not appear in the price waterfall.

## When to use it

- Header totals (`TotalAmount`, `Subtotal`): group-count 0, SUM over all contributing lines. [Repo]
- Per-group subtotals (by quote line group, product category, product type): GroupBy mode. [Help]
- Bundle total on the parent line from its children: Roll Up Price. [Help]
- Do not use for a per-line calculation: use [Formula](./formula-based-pricing.md) or a discount element.
- Do not use to move a value between hierarchy levels with sequential formulas: see [price-propagation.md](./price-propagation.md).

## Configuration

| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| (section count) | `section-count` | Literal | yes | Number of aggregation sections. Shipped = `1`. See "Multiple sections". |
| Group By (count) | `section-N-group-count` | Literal | yes | `0` = whole-transaction (header) aggregate; `>=1` = GroupBy. [Repo] |
| Group By tag M | `section-N-group-M` | Parameter | per count | Context tag. Zero-based M. [Repo] |
| Group By tag M type | `section-N-group-M-type` | Literal | per count | Data type of the tag (`Text` shipped). Allowed tag types in Builder: Text, Numeric, Currency. [Core] |
| Formula (function) | `section-N-aggr-func` | Literal | yes | Exactly `SUM`, `AVG`, `MIN`, `MAX` (upper case). No COUNT: the function enum has four members and any other value fails at run time. [Core] |
| Formula (aggregated tag) | `section-N-aggr-func-tag` | Parameter | yes | Tag being aggregated. Builder allows Currency or Numeric tags only. [Core] |
| (tag type) | `section-N-aggr-func-tag-type` | Literal | yes | `Currency` shipped. |
| Output Variable | `section-N-output` | Parameter, `output=true` | yes | Implicit variable; see Placement. Builder requires Currency or Numeric. [Core] |
| (output type) | `section-N-output-type` | Literal | yes | `Currency` shipped. |
| Where: field | `condition-K-input` | Parameter | per count | Zero-based K. [Repo][Core] |
| Where: operator | `condition-K-operator` | Literal | per count | One of `greaterThan`, `lessThan`, `equalTo`, `notEqualTo`, `isNull`, `isNotNull`, `isTrue`, `isFalse`. Shipped uses `isNotNull`, `isFalse`. See "Where operators". [Core] |
| Where: value | `condition-K-output-data` | Literal | comparison operators | Comparison value; omit for the is* operators. Runtime strips the first and last character of the stored string (the Builder stores it wrapped), so copy a Builder-saved sample. [Core] |
| Where: data type | `condition-K-input-data-type` | Literal | per count | Type of the Where field: `Text`, `Boolean`, `Currency`, `Numeric`, `DateTime`. [Repo][Core] |
| Where: count | `where-condition-count` | Literal | yes | Builder limits Where conditions to 3. [Core] Shipped = `3`. |
| Write Back: tag | `write-back` | Parameter | no | Condition field choosing which lines receive the aggregate (see "Write Back"). Not allowed with Roll Up. [Help][Core] |
| Write Back: operator / value / type | `write-back-operator`, `write-back-output-data`, `write-back-data-type` | Literal | no | Same operator set as Where. Shipped only `write-back-data-type=Text` (placeholder, nothing configured). [Core][Repo] |
| Roll Up Price | `RollUpPrice` | Literal | yes | `true` or `false`. [Repo][Core] |
| Roll Up: parent reference | `ParentProduct` | Parameter | when Roll Up | Context tag holding the parent line's `LineItem` id; the engine links each line to the line whose `LineItem` equals this value. Help calls it "Parent Product ... ParentReference". [Core][Help] |
| Roll Up: termination condition | `rollup-condition`, `rollup-condition-operator`, `rollup-condition-output-data`, `rollup-condition-data-type` | Parameter / Literal | optional | Builder label "Termination Condition": marks which lines are roots. Same operator set. Repo ships only `rollup-condition-data-type=Text`. [Core][Repo] |

## Modes

| Mode | Settings | Result |
|---|---|---|
| Header / whole-transaction | `group-count=0`, `RollUpPrice=false` | One value for the transaction (e.g. `TotalAmount = SUM(ItemNetTotalPrice)`). [Repo] |
| GroupBy | `group-count>=1`, `group-0=<tag>` | One value per distinct group key, written to each line in the group. Help example: group by product category, `SUM(ItemNetTotalPrice)` into `ItemGroupSummarySubtotal`. [Help] |
| Roll Up Price | `RollUpPrice=true`, `ParentProduct=<parent ref tag>` | Each child priced first, then added to the parent line. Help example: `SUM(NetUnitPrice)` into `ItemNetTotalPrice` for a bundle. [Help] See "Roll Up semantics". No shipped example. |

## Multiple sections

`section-count` greater than 1 is supported by the engine. [Core] Each section N
has its own group-count, group tags, function, aggregated tag and output; the
engine runs the sections in order over the same lines.

- Where conditions are NOT per section: every `condition-K-*` entry is pooled and ANDed for every section. Write Back is pooled too (the first one defined). [Core]
- The Builder authors one section [Core]; sections 2+ are metadata-only. Whether the Builder preserves them on re-save is untested; Simulate before relying on it.
- Roll Up uses section 0 only; later sections are ignored when `RollUpPrice=true`. [Core]
- A section missing its `section-N-group-count` fails parsing. [Core]

## Where operators

Conditions are checked per line, in index order, ANDed; the first false stops the
check. A condition whose field is absent from the line is skipped. [Core]

| Operator | Meaning / types | Quirk |
|---|---|---|
| `isNull` / `isNotNull` | tag is null / not null | Safe on any type. |
| `isTrue` / `isFalse` | Boolean tag | Null input throws; put `isNotNull` on the same tag earlier. |
| `equalTo` / `notEqualTo` | Numeric, Currency, Text, DateTime | Boolean comparison is not implemented (`equalTo` always false); use `isTrue`/`isFalse`. Null input throws. |
| `greaterThan` | Numeric, Currency, DateTime | Strict `>`. Text/Boolean: always false. |
| `lessThan` | Numeric, Currency, DateTime | Implemented as NOT greaterThan, so it behaves as `<=` (equal values pass). Text/Boolean: always true. |

Where decides which lines contribute VALUES to the function. It does not decide
which lines receive the result. [Core]

## Write Back

Write Back (`write-back` tag + operator + value) is a second condition that picks
which lines in a group RECEIVE the aggregate. [Core] Without it, every line in the
group (including lines Where excluded) receives the value. With it, only lines
satisfying it do; others keep their current output-tag value. Ignored for Roll Up
[Help]. A comparison operator here requires the value parameter (save fails otherwise). [Core]

## Roll Up semantics

[Core] Runs once, over section 0; Where, Group By and Write Back are not applied.
1. Build a tree: each line keyed by its `LineItem` id, attached to the line whose id is in its `ParentProduct` tag.
2. Roots: lines satisfying the termination condition when set, else lines with a null `ParentProduct`.
3. For each node, output = function over (own value of the aggregated tag + each direct child's value of the aggregated tag), nulls skipped. Children run first, but the parent reads the children's aggregated tag, not their output tag, so grandchildren do not flow up unless the output tag is the same tag as the aggregated tag.
4. A node with no non-null values is left unset.

## Placement and ordering

- Place after Derived Price, with a Where condition that targets only contributing lines. Shipped steps use `DerivedPricingAttribute isNotNull` + `DerivedPricingAttribute isFalse` plus `<aggregated tag> isNotNull` (and `SalesTransactionItemGroup isNotNull` for GroupBy). [Help][Repo]
- Aggregates sit in the fixed tail after Discount Distribution Service (DDS rewrites `NetUnitPrice` and `ItemNetTotalPrice`, so a SUM above DDS is pre-header-discount), before/with Rounding. Do not add a `FormulaBasedPricing` step after the aggregate tail; the platform rejects it with a misleading DDS message. Full rules: [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md). [Repo]
- Output and GroupBy tags must sit at the same context hierarchy level. [Help]
- Avoid loops: if `NetUnitPrice` is set from `InputUnitPrice` and an aggregate rewrites `InputUnitPrice` while reading `NetUnitPrice`, the value never settles. [Help]
- Derived products on quote lines are unsupported. [Help]
- The output variable is materialized implicitly from `section-N-output`. Never also list it in an overlay's `addVariables` (fails with `A context variable with the name '<Name>' already exists`). See `../../expression-sets/authoring-and-overlays.md` ("addVariables is for INPUT Constants only").

## Rules and limits

| Rule | Source |
|---|---|
| Functions: AVG, SUM, MAX, MIN only. COUNT does not exist. | [Core] |
| Aggregated tag and output: Currency or Numeric. | [Core] |
| Group By tags: Text, Numeric or Currency; maximum 5; duplicates rejected. | [Core] |
| Maximum 3 Where conditions. | [Core] |
| Group key = concatenation of Group By tag values with no separator, so values can collide (`1`+`23` equals `12`+`3`). | [Core] |
| Group By tags and the output must be on the same context path, else the run fails (code SF_PRICING_00017). | [Core] |
| Currency AVG can carry up to 16 decimal places. | [Help] |
| Write Back cannot be combined with Roll Up Price. | [Help] |
| Aggregate changes are not in the waterfall; read them in the Simulate JSON. | [Help] |
| Setting Include in Output exposes the output in the JSON. | [Help] |

Server save-time validation (label text not quoted): Group By tags not under one
parent node; Group By and output not under the same parent node; aggregated tag
and output data types incompatible; Write Back or Termination comparison
operator without a value. [Core] Builder checks: empty required field; tag not a
known variable; tag type outside the allowed list; unknown function; more than 5
Group By tags; more than 3 Where conditions. [Core] Run time: an empty function
value fails parsing; a null reaching the function fails with
`Null Value cannot be aggregated value<values>`. [Core]

## Metadata shape

Header SUM, trimmed from the shipped encoding (`<input>true</input>` on every
parameter except the output, which is `<output>true</output>`). Numbering is
zero-based and contiguous.

```xml
<steps>
  <actionType>GroupingAndAggregatePricing</actionType>
  <customElement>
    <parameters><name>section-count</name><type>Literal</type><value>1</value></parameters>
    <parameters><name>section-0-group-count</name><type>Literal</type><value>0</value></parameters>
    <parameters><name>section-0-aggr-func</name><type>Literal</type><value>SUM</value></parameters>
    <parameters><name>section-0-aggr-func-tag</name><type>Parameter</type><value>ItemNetTotalPrice</value></parameters>
    <parameters><name>section-0-aggr-func-tag-type</name><type>Literal</type><value>Currency</value></parameters>
    <parameters><name>section-0-output-type</name><type>Literal</type><value>Currency</value></parameters>
    <parameters><name>condition-0-input</name><type>Parameter</type><value>ItemNetTotalPrice</value></parameters>
    <parameters><name>condition-0-operator</name><type>Literal</type><value>isNotNull</value></parameters>
    <parameters><name>condition-0-input-data-type</name><type>Literal</type><value>Currency</value></parameters>
    <parameters><name>condition-1-input</name><type>Parameter</type><value>DerivedPricingAttribute</value></parameters>
    <parameters><name>condition-1-operator</name><type>Literal</type><value>isNotNull</value></parameters>
    <parameters><name>condition-1-input-data-type</name><type>Literal</type><value>Boolean</value></parameters>
    <parameters><name>condition-2-input</name><type>Parameter</type><value>DerivedPricingAttribute</value></parameters>
    <parameters><name>condition-2-operator</name><type>Literal</type><value>isFalse</value></parameters>
    <parameters><name>condition-2-input-data-type</name><type>Literal</type><value>Boolean</value></parameters>
    <parameters><name>write-back-data-type</name><type>Literal</type><value>Text</value></parameters>
    <parameters><name>rollup-condition-data-type</name><type>Literal</type><value>Text</value></parameters>
    <parameters><name>where-condition-count</name><type>Literal</type><value>3</value></parameters>
    <parameters><name>RollUpPrice</name><type>Literal</type><value>false</value></parameters>
    <parameters><output>true</output><name>section-0-output</name><type>Parameter</type><value>TotalAmount</value></parameters>
  </customElement>
  <description>Aggregate Price</description>
  <name>__STEP_NAME__</name>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```

GroupBy variant: set `section-0-group-count=1`, add
`section-0-group-0` (Parameter, e.g. `SalesTransactionItemGroup`) and
`section-0-group-0-type` (Literal `Text`), and add a Where on the group tag
`isNotNull`. [Repo]

Roll Up variant (parameter names from core, not shipped): `RollUpPrice=true`
plus `ParentProduct` (Parameter, the parent reference tag); omit Write Back; keep
`section-count=1`, `section-0-group-count=0`. [Core]

### Worked example (labelled example)

Sum net total by product category into a custom output tag (placeholders in angle
brackets; needs a custom context tag and mapping). Use the Header SUM XML above
with: `section-0-group-count=1`, `section-0-group-0=<category tag>`,
`section-0-group-0-type=Text`, `section-0-output=<CategorySubtotal tag>`, and a
Where `<category tag> isNotNull`. In an overlay, wrap the same parameters in an
`addSteps` entry (`actionType: GroupingAndAggregatePricing`, placement after the
last aggregate step).

Do not list `<CategorySubtotal tag>` in `addVariables`. Overlay mechanics:
`../../expression-sets/authoring-and-overlays.md`. To persist the output to a
record field, add a context mapping: `../../context-service/SKILL.md`. The
aggregate output lives only in the pricing context until mapped.

## Shipped in this repo (snapshot)

| Procedure | Step name (label) | Mode | Output |
|---|---|---|---|
| `RLM_DefaultPricingProcedure` | `Calculatetotalamountbyaddingitemnettotalpricesofallthelines` | header SUM `ItemNetTotalPrice` | `TotalAmount` |
| same | `Calculatesubtotalbyaddingtotallineamountsofallthelines` | header SUM `TotalLineAmount` | `Subtotal` |
| same | `Calculateitemgroupsubtotalbyaddingitemnettotalpricesofallthelines` | GroupBy `SalesTransactionItemGroup`, SUM `ItemNetTotalPrice` | `ItemGroupSummarySubtotal` |
| `RLM_PRM_DISTI_Pricing_Procedure`, `RLM_Revenue_Management_Recalc_Procedure` | same three | same | same |

All use `RollUpPrice=false`. Snapshot only. Discover live:
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify

1. Builder: Save, then Simulate with Include in Output set on the output.
2. Read the output tag in the Simulate JSON (not the waterfall). Help example: Electronics group = 141,615 + 4,975 = 146,590. [Help]
3. For a persisted tag, query the mapped record field after a reprice.

## Troubleshooting

| Symptom / error | Cause | Fix |
|---|---|---|
| `A context variable with the name '<X>' already exists` on overlay apply | Output also listed in `addVariables` | Remove it from `addVariables` [Repo] |
| `You can add the Discount Distribution Service element only before the Rounding Rules and Aggregate elements` on a formula step | Formula placed after the aggregate tail; message names DDS misleadingly | Move the formula before DDS or compute elsewhere [Repo] |
| Aggregate not in waterfall | By design | Read Simulate JSON [Help] |
| Total ignores header discount | Aggregate placed before DDS | Place after DDS [Repo] |
| Value never settles / slow | Circular `NetUnitPrice` / `InputUnitPrice` mapping | Break the loop [Help] |
| Derived lines counted | No `DerivedPricingAttribute` Where | Add `isNotNull` + `isFalse` conditions [Help][Repo] |
| Builder rejects tag | Type not Currency/Numeric (aggregated, output) or Text/Numeric/Currency (group) | Use an allowed tag type [Core] |
| Value computed but not on record | No context mapping for the output tag | Add mapping (inferred) |
| Write Back disabled/ignored with Roll Up | Unsupported combination | Use one or the other [Help] |
| Run fails on `isTrue`/`isFalse`/`equalTo` | Null reaches the check | Put `isNotNull` on the same tag first [Core] |
| `lessThan` includes equal values | Implemented as not-greaterThan | Add `notEqualTo` or shift threshold [Core] |
| Parent misses grandchildren | Roll Up reads direct children's aggregated tag | Use the same tag as input and output, or [price-propagation.md](./price-propagation.md) [Core] |

## Open questions

- Exact stored quoting of `condition-K-output-data` and the exact Write Back data-type key spelling: copy from a Builder-saved sample before hand-authoring.
- Whether the Builder preserves hand-authored sections 2+ on re-save: untested.

## Disagreements resolved

- COUNT: some secondary sources list it; the engine function enum has SUM/AVG/MIN/MAX only. Core wins.
- Write Back: Help says it overrides a variable's output; the engine uses it as a recipient filter on which lines get the aggregate. Core wins.
- Multi-section: Builder shows one; the engine loops all sections. Metadata-only sections run; verify with Simulate.
