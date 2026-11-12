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
| Group By tag M type | `section-N-group-M-type` | Literal | per count | Data type of the tag (`Text` shipped). Builder allows Text, Numeric, Currency. [Core] |
| Formula (function) | `section-N-aggr-func` | Literal | yes | Exactly `SUM`, `AVG`, `MIN`, `MAX` (upper case). No COUNT: an empty value fails parsing; the Builder offers only these four. [Core] |
| Formula (aggregated tag) | `section-N-aggr-func-tag` | Parameter | yes | Tag being aggregated. Builder allows Currency or Numeric only; run time supports no other type (null function, see Rules). [Core] |
| (tag type) | `section-N-aggr-func-tag-type` | Literal | yes | `Currency` shipped. |
| Output Variable | `section-N-output` | Parameter, `output=true` | yes | Implicit variable; see Placement. Save requires its type to be compatible with the aggregated tag. [Core] |
| (output type) | `section-N-output-type` | Literal | yes | `Currency` shipped. |
| Where: field | `condition-K-input` | Parameter | per count | Zero-based K. [Repo][Core] |
| Where: operator | `condition-K-operator` | Literal | per count | One of `greaterThan`, `lessThan`, `equalTo`, `notEqualTo`, `isNull`, `isNotNull`, `isTrue`, `isFalse`. Shipped uses `isNotNull`, `isFalse`. See "Where operators". [Core] |
| Where: value | `condition-K-output-data` | Literal | comparison operators | Comparison value; omit for the is* operators. Runtime strips the first and last character of the stored string (the Builder stores it wrapped), so copy a Builder-saved sample. [Core] |
| Where: data type | `condition-K-input-data-type` | Literal | per count | Type of the Where field: `Text`, `Boolean`, `Currency`, `Numeric`, `DateTime`. [Repo][Core] |
| Where: count | `where-condition-count` | Literal | yes | Builder limits Where conditions to 3. [Core] Shipped = `3`. |
| Write Back: tag | `write-back` | Parameter | no | Condition field choosing which lines receive the aggregate (see "Write Back"). Not allowed with Roll Up. [Help][Core] |
| Write Back: operator / value / type | `write-back-operator`, `write-back-output-data`, `write-back-data-type` | Literal | no | Same operator set as Where. Shipped only `write-back-data-type=Text` (placeholder, nothing configured). [Core][Repo] |
| Roll Up Price | `RollUpPrice` | Literal | yes | `true` or `false`. [Repo][Core] |
| Roll Up: parent reference | `ParentProduct` | Parameter | when Roll Up | Context tag holding the parent line's `LineItemId`; the engine links each line to the line whose `LineItemId` equals this value. Help calls it "Parent Product ... ParentReference". [Core][Help] |
| Roll Up: termination condition | `rollup-condition`, `rollup-condition-operator`, `rollup-condition-output-data`, `rollup-condition-data-type` | Parameter / Literal | optional | Builder label "Termination Condition": marks which lines are roots. Same operator set. Repo ships only `rollup-condition-data-type=Text`. [Core][Repo] |

## Modes

| Mode | Settings | Result |
|---|---|---|
| Header / whole-transaction | `group-count=0`, `RollUpPrice=false` | One value for the transaction (e.g. `TotalAmount = SUM(ItemNetTotalPrice)`). [Repo] |
| GroupBy | `group-count>=1`, `group-0=<tag>` | One value per distinct group key, written to each line in the group. Help example: group by product category, `SUM(ItemNetTotalPrice)` into `ItemGroupSummarySubtotal`. [Help] |
| Roll Up Price | `RollUpPrice=true`, `ParentProduct=<parent ref tag>` | Each child priced first, then added to the parent line. Help example: `SUM(NetUnitPrice)` into `ItemNetTotalPrice` for a bundle. [Help] See "Roll Up semantics". No shipped example. |

## Multiple sections

The encoding allows `section-count` greater than 1 and the parser reads each section N
(own group-count, group tags, function, aggregated tag and output). [Core]

- Run time: the step opens one line stream and every section consumes it, so a second section is expected to fail with a reused-stream error. Use one Aggregate step per output, as the shipped procedures do. Read from code, not run live. [Core][inferred]
- Where conditions are NOT per section: every `condition-K-*` entry is pooled and ANDed for every section. Write Back is pooled too (the first one defined). [Core]
- The Builder authors one section [Core]; do not hand-author sections 2+.
- Roll Up uses section 0 only; later sections are ignored when `RollUpPrice=true`. [Core]
- A section missing its `section-N-group-count` fails parsing. [Core]

## Where operators

Conditions are checked per line, in index order, ANDed; the first false stops the
check, so later conditions are not evaluated once one fails: put the cheapest or most selective first
[Platform behaviour, traced; the same check, called from the Roll Up (propagation) path, runs with null handling on, so the null throw below applies to direct line evaluation]. A condition whose field is absent from the line is skipped. On aggregate lines every comparison (not `isNull`/`isNotNull`) on a present-but-null value throws. [Core]

| Operator | Meaning / types | Quirk |
|---|---|---|
| `isNull` / `isNotNull` | tag is null / not null | Safe on any type. |
| `isTrue` / `isFalse` | Boolean tag | `isFalse` is NOT `isTrue`: any non-"true" value passes. Null input throws; put `isNotNull` on the same tag earlier. |
| `equalTo` / `notEqualTo` | Numeric, Currency, Text, DateTime | Boolean comparison is not implemented (`equalTo` always false, `notEqualTo` always true); use `isTrue`/`isFalse`. Null input throws. |
| `greaterThan` | Numeric, Currency, DateTime | Strict `>`. Text/Boolean: always false. |
| `lessThan` | Numeric, Currency, DateTime | Implemented as NOT greaterThan, so it behaves as `<=` (equal values pass). Text/Boolean: always true. |

Where decides which lines contribute VALUES to the function. It does not decide
which lines receive the result. [Core]

## Write Back

Write Back (`write-back` tag + operator + value) is a second condition that picks
which lines in a group RECEIVE the aggregate. [Core] Without it, every line in the
group (including lines Where excluded) receives the value. With it, only lines
satisfying it do; others keep their current output-tag value. Ignored for Roll Up
[Help]. Save rejects a Write Back comparison operator with no value, as for Where and Termination Condition. [Core]

## Roll Up semantics

[Core] Runs once, over section 0; Where, Group By and Write Back are not applied.
1. Build a tree: each line keyed by its `LineItemId`, attached to the line whose id is in its `ParentProduct` tag.
2. Roots: lines satisfying the termination condition when set, else lines with a null `ParentProduct`.
3. For each node, output = function over (own value of the aggregated tag + each direct child's value of the aggregated tag), nulls skipped. Children run first, but the parent reads the children's aggregated tag, not their output tag, so grandchildren do not flow up unless the output tag is the same tag as the aggregated tag.
4. A node with no non-null values is left unset. Lines whose parent is not found and that are not roots are never rolled up.

## Placement and ordering

- Place after Derived Price, with a Where condition that targets only contributing lines. Shipped steps use `DerivedPricingAttribute isNotNull` + `DerivedPricingAttribute isFalse` plus `<aggregated tag> isNotNull` (and `SalesTransactionItemGroup isNotNull` for GroupBy). [Help][Repo] When Pricing Setting maps `IsDerived`, the engine also drops derived lines from every element but Derived Price in the calculation phase [Core]. Keep the two conditions anyway: Help recommends them and they guard a procedure whose Pricing Setting does not map `IsDerived`.
- Unlike other elements, aggregates include aborted lines (Stop Pricing marks lines with the same aborted flag; see [Stop Pricing](./stop-pricing.md)), skipped delta lines and inclusive-pricing lines; ignored and error-state lines are excluded. [Core]
- After Discount Distribution Service (DDS) only Aggregate or Rounding Values steps may follow [Core]. DDS rewrites `NetUnitPrice` and `ItemNetTotalPrice`, so a SUM above DDS is pre-header-discount. Any other step after DDS, e.g. `FormulaBasedPricing`, is rejected with the DDS message in Troubleshooting. [Core][Repo] Full rules: [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).
- Output and GroupBy tags must sit at the same context hierarchy level. [Help]
- Avoid loops: if `NetUnitPrice` is set from `InputUnitPrice` and an aggregate rewrites `InputUnitPrice` while reading `NetUnitPrice`, the value never settles. [Help]
- Derived products on quote lines are unsupported. [Help]
- The output variable is materialized implicitly from `section-N-output`. Never also list it in an overlay's `addVariables` (fails with `A context variable with the name '<Name>' already exists`). See `../../expression-sets/authoring-and-overlays.md` ("addVariables is for INPUT Constants only").

## Rules and limits

| Rule | Source |
|---|---|
| Aggregated tag and output: Currency or Numeric. | [Core] |
| Group By tags: Text, Numeric or Currency; maximum 5 (Builder). Duplicate tags: untested. | [Core][inferred] |
| Maximum 3 Where conditions. | [Core] |
| Group key = concatenation of Group By tag values with no separator, so values can collide (`1`+`23` equals `12`+`3`). | [Core] |
| Aggregated tag data type other than Currency or Numeric: no function exists, fails with the null-value error below. | [Core] |
| Group By tags and the output must be on the same context path, else the run fails with `SF-Pricing-00017: The Group By and Output fields belong to different parent nodes. Make sure that the tags for Group By and Output fields belong to the same parent node.` | [Core] |
| Currency AVG is sum / count at 16 decimal places (half-even), trailing zeros stripped. Numeric AVG is a plain double sum / count with no rounding; an empty list gives 0. | [Help][Core] |
| Write Back cannot be combined with Roll Up Price. | [Help] |
| Aggregate changes are not in the waterfall; read them in the Simulate JSON (set Include in Output). Core still runs waterfall generation after every aggregate step (in delta mode also for lines flagged skip-waterfall); whether entries reach the output waterfall is unconfirmed, so rely on Help. | [Help][Core] |

Save-time messages: `All groupBy tag should belong to same parent in context.`;
`Output and GroupBy tag should belong to same parent in context.`;
`Aggregate element output and formula should be of compatible Data Type .`;
`To save <element>, Specify a valid output value and try again.` (Where or
Write Back or Termination Condition comparison without a value). Builder: empty
required field, disallowed type, over 5 Group By or 3 Where. Run time: an empty
function fails parsing; a null or unsupported type reaching the function fails with
`Null Value cannot be aggregated value` plus the joined values. [Core]

## Metadata shape

Header SUM, in the shipped encoding: every parameter sets both flags (`input` and
`output` are required and default to true [Dev guide], so an omitted flag declares an
input as an output too). Numbering is zero-based and contiguous.

```xml
<steps>
  <actionType>GroupingAndAggregatePricing</actionType>
  <customElement>
    <parameters><input>true</input><name>section-count</name><output>false</output><type>Literal</type><value>1</value></parameters>
    <parameters><input>true</input><name>section-0-group-count</name><output>false</output><type>Literal</type><value>0</value></parameters>
    <parameters><input>true</input><name>section-0-aggr-func</name><output>false</output><type>Literal</type><value>SUM</value></parameters>
    <parameters><input>true</input><name>section-0-aggr-func-tag</name><output>false</output><type>Parameter</type><value>ItemNetTotalPrice</value></parameters>
    <parameters><input>true</input><name>section-0-aggr-func-tag-type</name><output>false</output><type>Literal</type><value>Currency</value></parameters>
    <parameters><input>true</input><name>section-0-output-type</name><output>false</output><type>Literal</type><value>Currency</value></parameters>
    <parameters><input>true</input><name>condition-0-input</name><output>false</output><type>Parameter</type><value>ItemNetTotalPrice</value></parameters>
    <parameters><input>true</input><name>condition-0-operator</name><output>false</output><type>Literal</type><value>isNotNull</value></parameters>
    <parameters><input>true</input><name>condition-0-input-data-type</name><output>false</output><type>Literal</type><value>Currency</value></parameters>
    <parameters><input>true</input><name>condition-1-input</name><output>false</output><type>Parameter</type><value>DerivedPricingAttribute</value></parameters>
    <parameters><input>true</input><name>condition-1-operator</name><output>false</output><type>Literal</type><value>isNotNull</value></parameters>
    <parameters><input>true</input><name>condition-1-input-data-type</name><output>false</output><type>Literal</type><value>Boolean</value></parameters>
    <parameters><input>true</input><name>condition-2-input</name><output>false</output><type>Parameter</type><value>DerivedPricingAttribute</value></parameters>
    <parameters><input>true</input><name>condition-2-operator</name><output>false</output><type>Literal</type><value>isFalse</value></parameters>
    <parameters><input>true</input><name>condition-2-input-data-type</name><output>false</output><type>Literal</type><value>Boolean</value></parameters>
    <parameters><input>true</input><name>write-back-data-type</name><output>false</output><type>Literal</type><value>Text</value></parameters>
    <parameters><input>true</input><name>rollup-condition-data-type</name><output>false</output><type>Literal</type><value>Text</value></parameters>
    <parameters><input>true</input><name>where-condition-count</name><output>false</output><type>Literal</type><value>3</value></parameters>
    <parameters><input>true</input><name>RollUpPrice</name><output>false</output><type>Literal</type><value>false</value></parameters>
    <parameters><input>false</input><name>section-0-output</name><output>true</output><type>Parameter</type><value>TotalAmount</value></parameters>
  </customElement>
  <description>Aggregate Price</description>
  <name>__STEP_NAME__</name>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```

GroupBy variant (the shipped group subtotal step): set `section-0-group-count=1`, add
`section-0-group-0` (Parameter, `SalesTransactionItemGroup`) and
`section-0-group-0-type` (Literal `Text`), set `section-0-output=ItemGroupSummarySubtotal`
(the group-level tag), and replace condition 0 with the group tag `isNotNull` (data type
`Text`), keeping `where-condition-count=3`. Don't add a fourth condition: Builder allows 3. [Repo][Core]

Roll Up variant (parameter names from core, not shipped): `RollUpPrice=true`
plus `ParentProduct` (Parameter, the parent reference tag); omit Write Back; keep
`section-count=1`, `section-0-group-count=0`. [Core]

### Worked example (labelled example)

Sum net total by product category into a custom output tag (placeholders in angle
brackets; needs a custom context tag and mapping). Start from the GroupBy variant
with `section-0-group-0=<category tag>`, `section-0-output=<CategorySubtotal tag>` (at the
same context level as the category tag) and condition 0 replaced by
`<category tag> isNotNull`, still three conditions. In an overlay, wrap the same parameters in an
`addSteps` entry placed after the last aggregate step. Do not list the output in
`addVariables` (`../../expression-sets/authoring-and-overlays.md`). It lives only in
the pricing context until mapped to a record field (`../../context-service/SKILL.md`).

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
2. Read the output tag in the Simulate JSON (not the waterfall). Help example: Electronics group = 141,615 + 4,975 = 146,590. [Help] For a persisted tag, query the mapped record field after a reprice.

## Troubleshooting

| Symptom / error | Cause | Fix |
|---|---|---|
| `A context variable with the name '<X>' already exists` on overlay apply | Output also listed in `addVariables` | Remove it from `addVariables` [Repo] |
| `You can add the Discount Distribution Service element only before the Rounding Rules and Aggregate elements` on a formula step | Formula placed after DDS; message names DDS, not the formula | Move the formula before DDS or compute elsewhere [Core][Repo] |
| Total ignores header discount | Aggregate placed before DDS | Place after DDS [Repo] |
| Derived lines counted | No `DerivedPricingAttribute` Where | Add `isNotNull` + `isFalse` conditions (the engine filter applies only when Pricing Setting maps `IsDerived`) [Help][Repo][Core] |
| Builder rejects tag | Type not Currency/Numeric (aggregated, output) or Text/Numeric/Currency (group) | Use an allowed tag type [Core] |
| Run fails on `isTrue`/`isFalse`/`equalTo`/`greaterThan` | Null reaches the check | Put `isNotNull` on the same tag first [Core] |
| `Null Value cannot be aggregated value...` | Null in the aggregated tag, or tag type not Currency/Numeric | Add `isNotNull` Where; use a Currency/Numeric tag [Core] |
| Parent misses grandchildren | Roll Up reads direct children's aggregated tag | Use the same tag as input and output, or [price-propagation.md](./price-propagation.md) [Core] |

## Open questions
- Stored quoting of `condition-K-output-data`: copy from a Builder-saved sample. Write Back key spellings in the Configuration table match core. A second section failing at run time is read from code, not run live.
