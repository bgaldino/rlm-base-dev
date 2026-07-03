# Extract & Transform Engine — Platform Behavior Reference

Parent skill: `document-generation/SKILL.md`

Verified on Release 262, API v67.0. All patterns below are live-tested
against scratch orgs, not inferred from documentation.

---

## Formula Engine

### FormulaConverted — Auto-Generated on Save

`FormulaConverted` (RPN notation) is computed automatically from
`FormulaExpression` when the item is saved — both via REST API and the
OmniStudio Designer UI. Manual RPN authoring is never required.

RPN format: variables prefixed `var:`, string literals in single quotes
(spaces escaped as `/\/\//\/\/`), pipe `|` marks function boundaries,
postfix notation (arguments before operator).

### Formula Function Catalog

The ODT formula engine is **not** the Salesforce formula engine — it's a
smaller custom evaluator. Only the following functions generate valid RPN:

| Category | Supported | Not Supported |
|----------|-----------|---------------|
| Arithmetic | `+`, `-`, `*`, `/` | |
| Comparison | `>`, `<`, `>=`, `<=`, `==`, `!=` | |
| Logical | `IF`, `NOT`, `AND`, `OR`, `&&`, `\|\|` | `CASE` |
| Math | `ABS`, `ROUND`, `FLOOR`, `CEILING`, `MAX`, `MIN`, `SQRT` | `MOD`, `POWER`, `LOG` |
| String | `CONCAT`, `SUBSTRING` | `LEN`, `UPPER`, `LOWER`, `TRIM`, `LEFT`, `RIGHT`, `CONTAINS`, `BEGINS`, `TEXT`, `FORMAT` |
| Date | `TODAY`, `NOW`, `YEAR`, `MONTH`, `DAY` | `DATEVALUE`, `DATETIMEVALUE`, `ADDDAYS` |
| Null check | `ISBLANK` | `ISNULL`, `NULLVALUE`, `BLANKVALUE` |
| Array | `LIST` | |
| Apex callout | `FUNCTION` | |
| Type conversion | *(none)* | `VALUE`, `TEXT`, `FORMAT` |

**Unsupported functions save without error** — the `FormulaExpression` is
stored but `FormulaConverted` remains null, so the formula silently
produces no output at runtime.

Common patterns:
```
IF(Amount > 1000, true, false)              -- conditional boolean
CONCAT(Name, ' - ', Status)                 -- string join
LIST(Lines, 'Name', ProductName, 'Qty', Quantity)  -- array for {{#Section}}
FUNCTION('pkg.Class', 'method', arg1, arg2)        -- Apex callout
IF(ISBLANK(Field), 'N/A', Field)            -- null handling (no NULLVALUE)
Amount > 100 && Status == 'Active'          -- compound condition
```

### Transform Cannot Add Per-Element Booleans to Existing Arrays

Transform formulas (e.g., `IF(ISBLANK(...), false, true)`) with a
`FormulaResultPath` targeting an array element path (e.g.,
`Grant:IF_hasGrants`) do NOT produce per-element booleans. The formula
engine operates on scalar/top-level values, not per-array-element. Use
section-as-conditional pattern (below) instead.

---

## Filter Mechanics

### FilterGroup Semantics

Filters within the **same FilterGroup** are combined with **AND**.
Filters in **different FilterGroups** are combined with **OR**.

```
FilterGroup 0: QuoteId = Quote:Id   ┐
FilterGroup 0: Type = "Charge"      ┘  → AND (both must match)

FilterGroup 0: Status = "Active"    ┐
FilterGroup 1: Status = "Pending"   ┘  → OR (either matches)
```

**IMPORTANT**: Different FilterGroups produce **UNION ALL** (no dedup) —
records matching multiple groups appear once per matching group. A record
matching both FG 0 and FG 1 appears **twice** in the result set.

**WARNING — FilterGroup OR causes cartesian explosion when nesting:**
When a sequence with multiple FilterGroups is nested under a parent that
returns multiple records, EACH parent record evaluates EACH FilterGroup
independently. Example: 3 parent QLIs × 2 FilterGroups = 6 evaluation
paths, each returning all matching children. This produces N×M×G results
(parents × children × groups) instead of the expected child count. Avoid
multi-FilterGroup on child sequences — use a separate independent
hierarchy instead.

All existing production ODTs in this repo use only FilterGroup `0`
(all-AND filtering). Use multiple FilterGroups only when you need OR
logic on a **root-level** query, not on nested child sequences.

### FilterValue — Literal vs Reference

`FilterValue` supports two formats:

| Format | Example | Meaning |
|--------|---------|---------|
| Path reference | `Quote:Id` | Value from a previously-queried record |
| Single-quoted literal | `'0'`, `''`, `'Active'` | Literal string/number for comparison |

**Unquoted literals are silently ignored** — they don't generate a WHERE
condition. Always single-quote literal values: `FilterValue: "'0'"` not
`FilterValue: "0"`.

### FilterOperator Values

| Operator | Purpose |
|----------|---------|
| `=` | Equals (most common — joins and literal matches) |
| `<>` | Not equals |
| `<`, `>`, `<=`, `>=` | Numeric/date comparisons |
| `LIKE` / `NOT LIKE` | Pattern matching |
| `IN` | Set membership |
| `IS NULL` | Null check |
| `INCLUDES` / `EXCLUDES` | Multi-select picklist |
| `LIMIT` | Row limit on query |
| `OFFSET` | Pagination offset |
| `ORDER BY` | Sort control |

---

## Extract Hierarchy — How Sequences Produce Output

### Internal vs Output Paths (Critical)

The Extract engine maintains **two independent path systems**:

1. **Internal hierarchy** (object query `OutputFieldName`) — defines join
   scope and filter resolution. Example: `Quote:GrantQLI`
2. **Output structure** (field mapping `OutputFieldName`) — defines the
   JSON shape of the Extract output. Example: `Grant:ProductName`

These are decoupled. The internal hierarchy determines WHICH records are
queried and how filters chain. The field mapping output paths determine
WHERE the data lands in the final JSON.

**The `Line` pattern demonstrates this:**
```
Internal (object queries):
  Seq 1: Quote (root)
  Seq 4: QuoteLineItem → OutputFieldName: "Quote:QuoteLineItem"
                          FilterValue: "Quote:Id"

Output (field mappings):
  InputFieldName: "Quote:QuoteLineItem:RLM_ProductName__c"
  OutputFieldName: "Line:ProductName"     ← top-level output, NOT internal path
```

The internal `Quote:QuoteLineItem` hierarchy resolves records and filters.
The output `Line:ProductName` creates the JSON array structure. They are
independent systems that happen to share colon notation.

**Rules:**
- Object query `OutputFieldName` establishes the internal path for
  filter resolution in downstream sequences
- Field mapping `InputFieldName` uses the internal path to locate data
- Field mapping `OutputFieldName` uses a SEPARATE namespace to build output
- Output paths with colons create nested structures: `Grant:Items:Name`
  → `{"Grant": [{"Items": [{"Name": "..."}]}]}`

### Singleton vs Array — When Does a Path Produce an Array?

A sequence produces an array when:
- Its filter matches **multiple records** from the parent context
- It is nested under a parent that itself resolves to an array

A sequence produces a **singleton** (object) when:
- It's at the root level (not nested under a parent array)
- Only one record matches its filter
- All matched records collapse to the same path context

**Key insight:** A root-level `OutputFieldName` (e.g., `AllItems`) always
produces a singleton because there's no parent array to iterate over.
To get an array, nest under a parent: `Root:AllItems` (under the root
document). A seq that queries multiple records matching the filter
produces an array because multiple records match.

### Extract Output — Cartesian Product

When an Extract has multiple multi-record query sequences at the same
nesting level with independent parent paths, the output is a
**cartesian product** across them. Each row in the response contains
one combination of records from each sequence. For example: 2 records
from Seq 2 × 6 records from Seq 3 = 12 output rows (each containing
fields from both). This is by design — the Transform's `LIST()` formula
then rolls these into nested arrays for the template.

**To avoid cartesian products:** nest child sequences under their parent
using hierarchical `OutputFieldName` paths (e.g., `Parent:Child`). Only
sequences at the same nesting level with different parents produce
cartesian products.

### Parent Scope Limits Child Visibility

A child sequence can only see records that match its parent's context.
If a parent sequence has restrictive filters, children inherit that scope.

**Example:** If Seq 2 queries LineItems with `ParentLineItemId = null`
(top-level only), then any child sequence nested under `Root:LineItem:*`
can only see children of those top-level items. Grandchildren are invisible.

**Fix:** Create a **separate independent hierarchy** with its own root
query that doesn't inherit the restrictive filter:
```
Seq 10: ChildObject → OutputFieldName: "Root:AllChildren"
         FilterValue: "Root:Id"   (gets ALL children, not just top-level)
Seq 11: GrandchildObject → OutputFieldName: "Root:AllChildren:Detail"
         FilterValue: "Root:AllChildren:Id"
```

### Relationship Traversals in Field Mappings

Field mappings can traverse relationships using the internal hierarchy:
`Root:Parent:Child:RelatedObj:Name` reads the `Name` field from
a RelatedObj joined at that path.

**However:** Traversals that require an intermediate join that hasn't
been explicitly queried will **silently return null**. Example:
`Root:LineItem:Product2:Name` fails because `Product2` was never
queried as its own sequence — only the LineItem record exists in the
internal hierarchy.

**Fix:** Either:
1. Use a direct field on the already-queried object (formula field, denormalized):
   `Root:LineItem:ProductName__c`
2. Add an explicit join sequence for the related object:
   `Seq N: Product2, FilterValue: "Root:LineItem:Product2Id"`
   Then use: `Root:LineItem:Product2:Name`

---

## Field Mapping Depth & Array Membership

### Depth Determines Output Array Membership (Critical)

All field mappings that output to the same array path MUST read from
the **same depth** in the internal hierarchy. Mixing parent-level and
child-level `InputFieldName` paths targeting the same output array causes
parent-level entries to leak into the array for ALL parents (including
those without children).

**The depth rule:** Count how many object-query path segments prefix the
`InputFieldName`. All mappings targeting the same output array root must
have the same count.

**Example of the problem:**
```
Hierarchy:
  Seq 10: Parent → "Root:Parent"        (7 records)
  Seq 11: Child  → "Root:Parent:Child"  (5 records, not every parent has children)

Mappings (WRONG — mixed depth):
  FM: Root:Parent:Name          → Output:ParentName  (depth 2 — reads from Parent level)
  FM: Root:Parent:Child:Amount  → Output:Amount      (depth 3 — reads from Child level)
```
Result: 10 Output entries — 7 from parent level + 5 from child level merged.
Parents without children appear with only ParentName populated (phantom rows).

**Fix — Redundant join pattern:** Re-join the parent object at the child
level so ALL mappings read from the same depth:
```
Seq 12: Parent → "Root:Parent:Child:ParentRef"  ← REDUNDANT JOIN
         Filter: Root:Parent:Child:ParentId

Mappings (CORRECT — uniform depth 3):
  FM: Root:Parent:Child:ParentRef:Name → Output:ParentName  (depth 3)
  FM: Root:Parent:Child:Amount         → Output:Amount      (depth 3)
```
Result: 5 Output entries — only records where Child exists.

**Why it works:** By querying the Parent object AGAIN at the Child level
(filtering by the child's FK back to the parent), you make parent fields
accessible at child depth. The engine only emits entries for paths where
data actually exists at that depth.

**Corollary:** Mapping a child-level field to a parent output path
(e.g., `Output:Items:X` from child → `Output:X` at parent) breaks
parent-child array grouping — the engine flattens everything into
one-entry-per-child.

**Validation:** Run `python scripts/ai/docgen/docgen_inspect_hierarchy.py`
to detect mixed-depth violations automatically.

### Filtering to "Only Parents That Have Children" (No Subquery Support)

The Extract engine does not support subqueries or semi-joins. You cannot
write `WHERE Id IN (SELECT ParentId FROM Child)`. Instead, the redundant
join pattern inherently solves this: by making ALL mappings read from
child depth, parents without children produce no entries.

**General pattern:**
```
Seq N:   ParentObject → "Anchor:Parent"         (all potential parents)
          Filter: Root:Id
Seq N+1: ChildObject → "Anchor:Parent:Child"    (children per parent)
          Filter: Anchor:Parent:Id
Seq N+2: RelatedObj → "Anchor:Parent:Child:Related"  (optional: related to child)
          Filter: Anchor:Parent:Child:RelatedId
Seq N+3: ParentObject → "Anchor:Parent:Child:ParentRef"  ← REDUNDANT JOIN
          Filter: Anchor:Parent:Child:ParentId

Field mappings (ALL from child depth):
  Anchor:Parent:Child:ParentRef:Name    → Output:ParentName
  Anchor:Parent:Child:Amount            → Output:ChildAmount
  Anchor:Parent:Child:Related:Label     → Output:RelatedLabel
```

**When to use:**
- You need parent-record fields on each child array element
- You want ONLY parents that have children (no empty rows)
- Any parent-child-grandchild hierarchy where the output is child-centric

**Concrete example** (Usage Resource Grants on a Quote):
```
Seq 10: QuoteLineItem → "GrantParent"
         Filter: Quote:Id
Seq 11: QuotLineItmUseRsrcGrant → "GrantParent:GrantItem"
         Filter: GrantParent:Id
Seq 12: UsageResource → "GrantParent:GrantItem:Resource"
         Filter: GrantParent:GrantItem:UsageResourceId
Seq 13: QuoteLineItem → "GrantParent:GrantItem:QLI"    ← redundant join
         Filter: GrantParent:GrantItem:QuoteLineItemId

All mappings at child depth:
  GrantParent:GrantItem:QLI:ProductName__c → Grant:ProductName
  GrantParent:GrantItem:GrantQuantity      → Grant:GrantQuantity
  GrantParent:GrantItem:GrantType          → Grant:GrantType
  GrantParent:GrantItem:Resource:Name      → Grant:ResourceName
```
Result: flat array with one entry per grant, only for products that have grants.

---

## Architecture Patterns

### Independent Hierarchy Pattern

When you need data from a different scope than an existing hierarchy
(e.g., one hierarchy filters to top-level records, but you need all
records including children), create a **separate root hierarchy** with
its own object queries and filters. Multiple independent hierarchies can
coexist in the same Extract — they produce independent output arrays.

### Flat vs Grouped Output

Two fundamental patterns for multi-record output:

**Pattern A — Flat array (one entry per child record):**
Best when you want a simple repeating table. Each child record becomes
one array element with its parent's data denormalized onto it via the
redundant join pattern.

```
Internal hierarchy:            Output:
  Anchor                         Items: [
    Anchor:Child                   {ParentName, ChildField1, ChildField2, ...},
      Anchor:Child:ParentRef       {ParentName, ChildField1, ChildField2, ...},
      Anchor:Child:Related         ...
                                  ]
```

Template: `{{#Items}}| {{ParentName}} | {{ChildField1}} | ...{{/Items}}`

**Pattern B — Grouped array (one entry per parent, children nested):**
Best when you want per-parent sections. Each parent becomes an array
element with a nested child array.

```
Internal hierarchy:            Output:
  Root:Parent                    Groups: [
    Root:Parent:Child              {ParentName, Details: [{...}, {...}]},
                                   {ParentName, Details: [{...}]},
                                  ]
```

**WARNING:** Pattern B includes ALL parents (even those without children).
Parents without children appear as `{ParentName: "X"}` with no `Details`
key. Use `{{#Details}}` in the template to conditionally render only
populated entries, or combine with a `{{#ChildField}}` truthy check.

**Template pattern (grouped with conditional skip):**
```
{{#Groups}}{{#ChildField}}
  {{ParentName}} | {{ChildField}} | ...
{{/ChildField}}{{/Groups}}
```

`{{#ChildField}}` acts as a conditional — renders only when the field
exists (truthy string). Absent fields (childless parent entries) are skipped.

**Pattern A + redundant join** is generally preferred when you want a
clean array with no phantom rows. Pattern B is appropriate when you need
per-parent headers or section breaks in the template.

### Section Tokens as Conditionals (Truthy/Falsy Behavior)

`{{#FieldName}}...{{/FieldName}}` renders its content when `FieldName` is:
- A **non-empty string** (e.g., `"Grant"`) — renders
- A **non-empty array** — iterates and renders per element
- A **non-empty object** — renders once

Skips when `FieldName` is:
- **Absent** from the JSON entirely — skipped
- **`false`** (boolean) — skipped
- **`null`** — skipped
- **Empty string** `""` — skipped
- **Empty array** `[]` — skipped

This makes any string field usable as a conditional gate. To hide
table rows for entries missing a field, wrap with `{{#ThatField}}`.

---

## Operational Details

### Error Propagation — Sequences Are Independent

Failed sequences do **not** block downstream sequences. Each runs
independently; a failure is silently skipped (its mapped fields are
absent from the output — not null, not empty string).

- Bad field reference → sequence skipped, others unaffected
- Nonexistent object → sequence skipped, others unaffected
- No validation at save time — errors surface only at execution time

This means ODTs degrade gracefully across orgs with different field
sets. Missing fields produce absent output tokens rather than a
complete failure.

### ODT Name Constraints

The `Name` field on `OmniDataTransform` requires **alphanumeric characters
only** — no underscores, spaces, or special characters. Use camelCase
(e.g., `RLMQuoteExtractBasic`).

### Scale Observations

No API-level limit observed for item count or sequence count:
- 25 `InputObjectQuerySequence` values: accepted
- 225 items per ODT (25 queries + 200 field mappings): accepted

(UI/runtime performance at scale not yet verified.)

### ODT Preview / Simulate API

The OmniStudio Designer "Preview" button invokes an Aura controller action.
This is the only known programmatic execution path for ODTs against arbitrary
input data (outside of the `generateDocument` invocable, which is Invoice/CreditMemo only).

**Endpoint:**
```
POST /aura?r=N&aura.OmniDesigner.simulateDataraptor=1
```

**Controller:** `aura://OmniDesignerController/ACTION$simulateDataraptor`

**Payload (key params):**
```json
{
  "dataraptorSimualateInputParams": {
    "name": "<ODT_Record_Id>",
    "simulationParams": [
      {"simulationParamName": "inputData", "simulationParamValue": "{\"Id\": \"<recordId>\"}"},
      {"simulationParamName": "inputType", "simulationParamValue": "JSON"},
      {"simulationParamName": "ignoreCache", "simulationParamValue": "true"}
    ]
  }
}
```

Note: `name` takes the ODT **record Id** (0jI prefix), not the API Name.

**Response (`result` field, JSON-escaped string):**
```json
{
  "error": "OK",
  "hasErrors": false,
  "ActualTime": 147,
  "response": [{"field": "value"}],
  "debugLog": [
    "timestamp: Query: SELECT ... FROM ... WHERE ... LIMIT 50000",
    "timestamp: Query results found: N",
    "timestamp: Query time: Nms"
  ]
}
```

**Key behaviors:**
- `debugLog` shows exact SOQL generated — invaluable for debugging filters
- All queries get `LIMIT 50000` appended automatically
- `ActualTime` reports execution in milliseconds
- Requires active Lightning session auth (`sid` cookie + `aura.token` + `aura.context`) — cannot be invoked with just an OAuth access token
