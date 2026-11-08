# Assignment (`AssignmentElement`)

> Release 264 / API v68.0. Sources: `ind.pricing_assignment.htm`; dev guide
> `meta_expressionsetdefinition.htm`; shipped XML: `RLM_DefaultPricingProcedure`,
> `RLM_PRM_DISTI_Pricing_Procedure`, `RLM_Price_Distribution_Procedure`,
> `RLM_Revenue_Management_Recalc_Procedure`; core source (row JSON parsing).

Copies a value from a variable, constant or context tag into another context
tag. It works on outputs of earlier elements and does not touch the database.

## When to use it
- Use to default or override a tag (e.g. fill a null Effective To from the quote date) before a later element reads it [Help].
- Use to set a flag/label from a constant, or stage values for DDS (e.g. header discount type/value) [Repo].
- Supports currency, number, date-time and date types [Help].
- Do not use for computed values: use [Formula-Based Pricing](./formula-based-pricing.md).

## Configuration
| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Input variable N | `section-{N-1}-input1` | `Parameter` | yes | Source tag/variable/constant name; `input=true` [Repo] |
| Output variable N | `section-{N-1}-output` | `Parameter` | yes | Target tag; `output=true` [Repo] |
| (section count) | `sectionCount` | `Literal` | yes | Number of assignment rows [Repo] |
| (row definition) | `sectionJsonString{K}` | `Literal` | yes | JSON per row; see Metadata shape [Repo] |

Indexing rule [Core]: the element reads an unsuffixed `sectionJsonString` first; if present it is the only source. Otherwise it reads `sectionJsonString1`, `2`, `3`... in order until one is missing and concatenates their `whereConditions` arrays. Each array entry is one row: `field` = input (`name` `section-N-input1`, `value` = source), `value` = output (`name` `section-N-output`, `value` = target). The shipped empty `sectionJsonString1` (`{"whereConditions":[]}`) contributes no rows and is harmless; rows can sit in any numbered part. Use one scheme per step. With no JSON at all a legacy path rebuilds Currency rows from `sectionCount` [Core].

Row limit: an org-level value, "context tag mappings the Assignment element can have": Help lists default 20, maximum 50 [Help] (`ind.pricing_limits.htm`). The org value in core (API 256+) defaults to 25, minimum 1, maximum 50 [Core]. The defaults disagree; the effective limit is whatever the org has, so keep to 20 or fewer rows. Save fails when `sectionCount` exceeds the limit: `The limit of {0} assignments that can be added to the Assignment element was reached in the org. Delete some assignments and try again.` [Core]

## Placement and ordering
- Runs on outputs of preceding elements; put it after the element that produces the input and before the element that consumes the output [Help].
- Typical wrapper is a ListGroup with a filter (e.g. `EffectiveTo IsNull`) so only matching lines are assigned [Help].
- Assigned values hydrate from the record at reprice start, so a branch-only assignment leaves stale values (see Conditional assignments below).
- Ordering relative to DDS/aggregate tail: [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).

## Rules and limits
- Runs on tax-inclusive lines; skips stopped and errored lines [Core].
- No database writes by itself; persistence depends on the output tag being mapped to a record field in the context definition [Help; inferred for persistence].
- Input and output tag data types must match, except Numeric and Currency, which may be mixed; any other mismatch fails save with `Ensure that you use the same data type for both the variable's tags and try again.` [Core]. Checked per row index, only when both tags resolve to a data type [Core]. Shipped rows set `allowCompatibleDataTypes: true` [Repo].
- At run time the value is copied as is: if the input tag is absent on the line, the output is left unchanged; no conversion happens [Core].
- An empty-string `Constant` assigned to a Text field persists as null, so `""` is a true clear [Repo skill `../../expression-sets/authoring-and-overlays.md`].

### Conditional assignments: reset every line first
Each reprice hydrates the field's prior value from the record. If you assign only inside filtered branches, a line that stops matching keeps its stale value. Start with an unconditional assignment (a ListGroup whose filter matches every line) that resets the field, then add the branch groups after it. Full pattern and apply timing: [`authoring-and-overlays.md`](../../expression-sets/authoring-and-overlays.md) → *Conditional assignments — reset every line first*; worked example `datasets/expression_set_overlays/approval_flags.json` (group `RLMApprovalFlagsReset`).

## Metadata shape
From the shipped header-discount step (two rows):
```xml
<steps>
    <actionType>AssignmentElement</actionType>
    <customElement>
        <parameters><input>true</input><name>section-0-input1</name><output>false</output><type>Parameter</type><value>AppliedDiscountAmount__std</value></parameters>
        <parameters><input>true</input><name>section-1-input1</name><output>false</output><type>Parameter</type><value>Constant_DDS_Amount</value></parameters>
        <parameters><input>true</input><name>sectionCount</name><output>false</output><type>Literal</type><value>2</value></parameters>
        <parameters><input>true</input><name>sectionJsonString1</name><output>false</output><type>Literal</type><value>{&quot;whereConditions&quot;:[]}</value></parameters>
        <parameters><input>true</input><name>sectionJsonString2</name><output>false</output><type>Literal</type>
            <value>{&quot;whereConditions&quot;:[{&quot;field&quot;:{&quot;dataType&quot;:&quot;Currency&quot;,&quot;name&quot;:&quot;section-0-input1&quot;,&quot;value&quot;:&quot;AppliedDiscountAmount__std&quot;,&quot;allowCompatibleDataTypes&quot;:true},&quot;value&quot;:{&quot;dataType&quot;:&quot;Numeric&quot;,&quot;name&quot;:&quot;section-0-output&quot;,&quot;value&quot;:&quot;HeaderDiscountValue&quot;,&quot;allowCompatibleDataTypes&quot;:true}}]}</value></parameters>
        <!-- sectionJsonString3 = row 1 (Text: Constant_DDS_Amount -> HeaderDiscountType) -->
        <parameters><input>false</input><name>section-0-output</name><output>true</output><type>Parameter</type><value>HeaderDiscountValue</value></parameters>
        <parameters><input>false</input><name>section-1-output</name><output>true</output><type>Parameter</type><value>HeaderDiscountType</value></parameters>
    </customElement>
    <name>AssignAmountBasedHeaderDiscount</name>
    <parentStep>ListApplyAmountBasedHeaderDiscount</parentStep>
    <sequenceNumber>2</sequenceNumber>
    <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
The JSON is XML-escaped inside `<value>`; in Connect JSON it is a normal string (HTML-unescape rules: [../../expression-sets/SKILL.md](../../expression-sets/SKILL.md)). Constants are version variables (`type: Constant`) referenced by name.

## Shipped in this repo (snapshot)
| Procedure | Steps | What it does |
|---|---|---|
| Default (18) | `AssignAmountBasedHeaderDiscount`, `AssignPercentageBasedHeaderDiscount`, `AssignTotalPriceOverride` | header discount / override staging |
| Default (18) | `Assignthepricingdatevariable`, `AssigntheEffectiveFromdatetoPricingDate` (top level, seq 7), `PassPricingContractIDfromQuotetoQuoteLines` (top level, seq 3), `AssignItemContracttoItemPricingContract`, `Assignment` (under `ListContainer`) | pricing date and contract defaults |
| Default (18) | `AssignInclusivePriceConstanttoTotalLineAmount`, `AssignTotalLineAmounttoItemSubtotalandItemNetTotalPricetoItemTotalPrice` (top level, seq 35) | tax-inclusive total; closing subtotal copy |
| PRM (seq 37), Recalc (seq 30) | `AssignTotalLineAmounttoItemSubtotalandItemNetTotalPricetoItemTotalPrice` (top level, after the aggregates) | closing subtotal copy; these procedures have no DDS, so a step may follow the aggregates |
| Default, PRM, Recalc | `AssignListPricetoInputUnitPrice`, `AssignNetUnitPricetoInputUnitPrice`, `AssignItemContractPricetoInputUnitPrice`, `AssignInputUnitPricetoNetUnitPrice` | unit-price staging between list, contract, input and net price |
| Default, PRM, Recalc | `AssignEvergreenPricingTermCountConstanttoPricingTermCount`, `AssignOneTimePricingTermCountConstanttoPricingTermConstant` | term-count constants |
| Default only | `ClearContractAppliedUnitPrice`, `Assigncontractinputunitpricetonetunitprice` | contract-price clear / net copy |
| `RLM_Price_Distribution_Procedure` (3) | `AssignHeaderDiscountAmount`, `AssignHeaderOverrideAmount`, `AssignHeaderPercentageAmount` | header discount staging |
| Approval overlay (not in base XML) | `RLMApprovalFlagsAssignNone` | reset level/label constants to `RLM_Approval_*__c` |

41 `AssignmentElement` steps in the shipped XML: Default 18, PRM distributor 10, Price Distribution 3, Recalc 10. Most are seq 2 under a List Group/filter parent; the top-level ones (no parent) are noted above.

Snapshot; refresh with `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`.

## Verify
- Simulate and read the JSON output: the output tag shows the assigned value; the waterfall shows the downstream element using it [Help].
- Reprice a line that no longer matches a branch and confirm the field cleared.

## Troubleshooting
| Symptom / error | Cause | Fix |
|---|---|---|
| Flag stays after line stops matching | No reset-first step | Add unconditional reset group before branches |
| Value not saved to record | Output tag not mapped to a record field | Map tag in the context definition |
| Row ignored / wrong row mapped | Gap in `sectionJsonString1..N` numbering, or an unsuffixed `sectionJsonString` that overrides the numbered parts | Number parts without gaps, use one scheme; keep `sectionCount` equal to rows (the limit check reads it); copy a shipped step |

## Open questions
- Literal inputs (not a named constant): row JSON carries per-side `isFormula`/`isContextTag` flags [Core], which hints non-tag inputs exist, but nothing ships; test live. Use a version-variable constant as shipped.
