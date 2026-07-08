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

### InputFieldName on Object Queries — Join Semantics (Critical)

**Common mistake:** Setting `InputFieldName: "Id"` on all object queries.
`InputFieldName` specifies **which field on the TARGET object** to match
against the `FilterValue` from the parent. It generates the WHERE clause:

```
WHERE <InputFieldName> = <resolved FilterValue>
```

**Two join patterns:**

| Pattern | InputFieldName | FilterValue | Generated WHERE | Cardinality |
|---------|---------------|-------------|-----------------|-------------|
| Child-of (1:many) | Child's FK field | `Parent:Id` | `WHERE ChildFKField = '<parentId>'` | 0..N children per parent |
| FK lookup (many:1) | `Id` | `Parent:FKField` | `WHERE Id = '<parentFKValue>'` | 0..1 target per parent |

**Examples:**
```
# Child-of: "Give me all QLIs belonging to this Quote"
OQ: QuoteLineItem, InputFieldName: "QuoteId", FilterValue: "Quote:Id"
→ WHERE QuoteLineItem.QuoteId = '<quoteId>'

# FK lookup: "Give me the Product2 record for this QLI's Product2Id"
OQ: Product2, InputFieldName: "Id", FilterValue: "Quote:QLI:Product2Id"
→ WHERE Product2.Id = '<product2IdFromQLI>'
```

**Rule:** `InputFieldName: "Id"` is correct ONLY for FK lookups (where you're
resolving a parent's FK value to get the target record). For child-of joins,
use the child's FK field name (e.g., `QuoteId`, `QuoteLineItemId`).

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

**Validation:** Run `python scripts/docgen/docgen_odt_inspect_hierarchy.py`
to detect mixed-depth violations automatically.

### Mixed Depth — When It's Safe vs Dangerous (Live-Verified)

All scenarios below were live-tested via `docgen_odt_execute.py` against
`dev-scratch` (Quote `0Q0XXXXXXXXXXXXAAA`, 7 QLIs, 5 Grants
on 2 of 7 QLIs).

---

#### Scenario A — Child-of join (one-to-many): DANGEROUS

**ODT:** `RESEARCHDepthMixV2`
```
Hierarchy:
  Quote (root, FilterValue: Id)
  Quote:QLI (InputFieldName: QuoteId, FilterValue: Quote:Id)       ← 7 records
  Quote:QLI:Grant (InputFieldName: QuoteLineItemId, FilterValue: Quote:QLI:Id) ← 5 on 2 QLIs

Mappings (mixed depth 2 + 3 → same output):
  Quote:QLI:RLM_ProductName__c     → Items:ProductName  (depth 2)
  Quote:QLI:Grant:GrantQuantity    → Items:GrantQty     (depth 3)
```
**Result: 10 entries** — 5 with GrantQty (real), 5 without GrantQty (phantoms).
Engine iterates at SHALLOWEST depth. QLIs with grants expand; QLIs without
grants still emit one entry with the deeper field **absent** (not null).

---

#### Scenario B — FK lookup (many-to-one): SAFE

**ODT:** `RLMQuoteProposalExtract` Grant sub-tree + `RESEARCHNonUniqueFKv2`
```
Hierarchy:
  Quote:QLI (pivot, 7 records)
  Quote:QLI:Product (InputFieldName: Id, FilterValue: Quote:QLI:Product2Id)  ← FK lookup

Mappings (mixed depth 2 + 3):
  Quote:QLI:Quantity          → Items:Qty          (depth 2)
  Quote:QLI:Product:ProductCode → Items:SKU        (depth 3)
```
**Result: 7 entries, ALL fields populated.** Each QLI resolves exactly
one Product2 via FK — no expansion, no phantoms.

---

#### Scenario C — Orphan FK (FK value is null): SAFE

**ODT:** `RESEARCHOrphanFKv2`
```
Hierarchy:
  Quote:QLI (pivot, 7 records — ALL have OpportunityLineItemId = null)
  Quote:QLI:OpptyLine (InputFieldName: Id, FilterValue: Quote:QLI:OpportunityLineItemId)

Mappings (mixed depth 2 + 3):
  Quote:QLI:RLM_ProductName__c    → Items:ProductName  (depth 2)
  Quote:QLI:OpptyLine:TotalPrice  → Items:OpptyPrice   (depth 3)
```
**Result: 7 entries with ProductName only; OpptyPrice ABSENT (not null).**
When the FK resolves to null, the deeper OQ simply finds 0 records — the
engine gracefully skips that join. The deeper field is absent from output
(same as an error/skipped sequence). No phantoms.

---

#### Scenario D — Mixed FK + child-of on same pivot: DANGEROUS

**ODT:** `RESEARCHMixedJoinsv2`
```
Hierarchy:
  Quote:QLI (pivot, 7 records)
  Quote:QLI:Product (InputFieldName: Id, FilterValue: Quote:QLI:Product2Id)  ← FK (safe)
  Quote:QLI:Grant (InputFieldName: QuoteLineItemId, FilterValue: Quote:QLI:Id)  ← child-of (dangerous)

Mappings (depth 2 + 3 + 3):
  Quote:QLI:RLM_ProductName__c  → Items:ProductName      (depth 2)
  Quote:QLI:Product:Name        → Items:ProductFullName  (depth 3, FK)
  Quote:QLI:Grant:GrantQuantity → Items:GrantQty         (depth 3, child-of)
```
**Result: 10 entries.**
- 5 QLIs without grants: 1 entry each (ProductName + ProductFullName, GrantQty absent)
- 2 QLIs with grants: expanded (2+3 entries), each has all 3 fields

**Key finding:** The child-of join DOMINATES expansion even when a safe FK
join is also present. The FK join's fields are correctly resolved on every
expanded entry (no phantoms in the FK-joined field), but the child-of
expansion still creates multiple entries per parent.

---

#### Scenario E — 3+ levels of mixed depth (all FK): SAFE

**ODT:** `RESEARCHThreeLevelsv2`
```
Hierarchy:
  Quote (root, depth 1)
  Quote:QLI (depth 2)
  Quote:QLI:Product (depth 3, FK join)

Mappings (depths 1 + 2 + 3 → same output):
  Quote:Name                  → Items:QuoteName        (depth 1)
  Quote:QLI:RLM_ProductName__c → Items:ProductName     (depth 2)
  Quote:QLI:Product:Name      → Items:ProductFullName  (depth 3)
```
**Result: 7 entries, ALL 3 fields populated on every entry.**
Multi-level mixed depth is perfectly safe when all deeper joins are FK
lookups. The engine resolves parent fields "down" to the deepest level
without phantom expansion.

---

#### Summary Table

These rules apply to ANY object hierarchy — the test data used Quote/QLI
but the behavior is engine-level, not object-specific.

| Scenario | Deeper join type | FilterValue pattern | Result | Safe? |
|----------|-----------------|---------------------|--------|-------|
| A | Child-of (1:many) | `Pivot:Id` | Phantoms | NO |
| B | FK lookup (many:1) | `Pivot:FKField` | Clean | YES |
| C | FK to null value | `Pivot:NullFKField` | Field absent | YES |
| D | FK + child-of mix | Both patterns | Phantoms (child-of dominates) | NO |
| E | Multi-level FK | All `Pivot:FKField` | Clean | YES |

**Canonical rule:** Mixed depth produces phantoms **if and only if** at
least one deeper OQ is a child-of join (`FilterValue` ends with `:Id` on
the pivot's path). FK lookups (where `FilterValue` references a specific
FK field on the pivot) are always safe regardless of depth mixing.

**How to tell them apart (applies to any object):**
- **Child-of** (dangerous): deeper OQ's `InputFieldName` is a FK field on
  the child (e.g., `QuoteId`, `ParentId`, `AccountId`) and `FilterValue`
  references the parent's Id. Pattern: "find all children of this parent."
- **FK lookup** (safe): deeper OQ's `InputFieldName` is `Id` and
  `FilterValue` references a FK field on the pivot (e.g., `Pivot:Product2Id`,
  `Pivot:UsageResourceId`). Pattern: "resolve this FK to its target record."

**Automated validation:**
- `python scripts/docgen/docgen_odt_inspect_hierarchy.py` — static analysis
  using the FilterValue heuristic (HIGH = child-of, LOW = all FK lookups)
- `python scripts/docgen/docgen_odt_execute.py` — live execution to
  empirically verify actual output entry count for any Extract + record
- `python scripts/docgen/docgen_template_generate.py` — full end-to-end
  generation (Extract → Transform → .docx → PDF) for template testing

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

### ODT Execution via REST API (Recommended for CLI/Agent Use)

The OmniStudio REST API provides a clean programmatic execution path for
Extract ODTs. Uses standard OAuth — no Lightning session required.

**Endpoint:**
```
POST /services/data/v67.0/omnistudio/dataraptor/<ODTName>
```

**Body:**
```json
{"Id": "<recordId>"}
```

**Example (via `sf` CLI):**
```bash
sf api request rest --method POST \
  --body '{"Id":"0Q0XXXXXXXXXXXXAAA"}' \
  /services/data/v67.0/omnistudio/dataraptor/RLMQuoteProposalExtract \
  --target-org dev-scratch
```

**Helper script (wraps the above with summary/count/json modes):**
```bash
python scripts/docgen/docgen_odt_execute.py RLMQuoteProposalExtract \
  --record-id 0Q0XXXXXXXXXXXXAAA --org dev-scratch
python scripts/docgen/docgen_odt_execute.py RLMQuoteProposalExtract \
  --record-id 0Q0XXXXXXXXXXXXAAA --org dev-scratch --json
python scripts/docgen/docgen_odt_execute.py RLMQuoteProposalExtract \
  --record-id 0Q0XXXXXXXXXXXXAAA --org dev-scratch --count
```

**Response:** Direct JSON — the Extract output array or object. No wrapper envelope.
```json
[
  {"ProductName": "Widget", "Quantity": 5, "Grant": [...]},
  {"ProductName": "Gadget", "Quantity": 3, "Grant": [...]}
]
```

**Key behaviors (live-verified):**
- Takes the ODT **Name** (not Id)
- Requires the ODT to be Active (`IsActive: true`)
- Returns the Extract output directly (no `response`/`debugLog` wrapper)
- Works with standard OAuth via `sf api request rest`
- No SOQL debug log available (use the Aura Preview API below for that)

**Use cases:**
- Automated testing: execute an Extract and assert record counts / field presence
- Phantom entry detection: compare expected vs actual entry count
- Regression testing: execute before/after a change and diff the output
- Agent validation: any agent can run this without browser automation

---

---

## Transform Engine (Live-Verified)

The Transform ODT reshapes Extract output into template-ready JSON. It does
NOT query the org — it operates purely on the JSON passed as input.

### Execution Model

**Input:** The Transform receives the Extract's full JSON output (typically
a single-element array: `[{key: value, ...}]`). In the production pipeline,
this is automatic. For standalone testing, pass the Extract output directly:

```bash
# Step 1: Execute Extract
python scripts/docgen/docgen_odt_execute.py MyExtract \
  --record-id 0Q0XXXXXXXXXXXXAAA --org dev-scratch --json > /tmp/extract_output.json

# Step 2: Pass Extract output to Transform
sf api request rest --method POST \
  --body @/tmp/extract_output.json \
  /services/data/v67.0/omnistudio/dataraptor/MyTransform \
  --target-org dev-scratch
```

**CRITICAL:** Passing `{"Id": "<recordId>"}` to a Transform produces
only formula-constant fields (e.g., hardcoded dimensions). The Transform
cannot query the org — it needs the Extract's data as input.

### Execution Order (OutputCreationSequence)

| OCS | Phase | What runs | Can reference |
|-----|-------|-----------|---------------|
| 0 | Formula phase | All formula items (by `FormulaSequence` order) | Raw input fields only |
| 1 | Mapping phase | All pass-throughs and field mappings | Raw input fields + formula results |

Formulas at OCS=0 inject computed values into the data pool via
`FormulaResultPath`. Pass-throughs at OCS=1 then map both raw input
fields AND formula-produced values to the final output structure.

**Example flow:**
```
Input: {"Amount": 5000, "FirstName": "John", "LastName": "Doe"}

OCS=0 formulas:
  CONCAT(FirstName, ' ', LastName)  → FormulaResultPath: "FullName"    → "John Doe"
  IF(Amount > 1000, true, false)    → FormulaResultPath: "IsLarge"     → true

OCS=1 pass-throughs:
  FullName  → ComputedName     (references formula result)
  IsLarge   → IF_large_amount  (references formula result)
  Amount    → Amount           (references raw input)

Output: {"ComputedName": "John Doe", "IF_large_amount": true, "Amount": 5000}
```

### Item Types

#### Pass-through (Field Mapping)

Maps an input field to an output field. Can rename, restructure, or pass
through unchanged.

```
InputFieldName: "AccountName"    OutputFieldName: "AccountName"    → simple rename/pass
InputFieldName: "Items:Price"    OutputFieldName: "Line:Amount"    → restructure array path
```

#### Formula

Computes a value from input fields using the formula engine (same function
catalog as Extract formulas — see Formula Engine section above).

Required fields: `FormulaExpression`, `FormulaResultPath`, `FormulaSequence`,
`OutputCreationSequence: 0`, `OutputObjectName: "Formula"`,
`OutputFieldName: "Formula"`.

#### Object Output

Bridges formula-built arrays into the `json` output namespace. Used with
`LIST()` formulas to pass arrays to templates.

Required fields: `InputFieldName` (= FormulaResultPath of the LIST formula),
`OutputFieldName` (template token name), `OutputFieldFormat: "Object"`,
`OutputObjectName: "json"`, `OutputCreationSequence: 1`.

### Building Nested Objects — Colon-Path Pattern (Live-Verified)

Colon-separated `OutputFieldName` on pass-throughs builds nested JSON objects:

```
Input:   {"DocId": "069...", "ImgW": "200", "ImgH": "80"}
Items:
  DocId → IMG_Logo:src       (OutputObjectName: "json", OCS: 1)
  ImgW  → IMG_Logo:width     (OutputObjectName: "json", OCS: 1)
  ImgH  → IMG_Logo:height    (OutputObjectName: "json", OCS: 1)

Output:  {"IMG_Logo": {"src": "069...", "width": "200", "height": "80"}}
```

**This is the ONLY way to build nested objects.** The `OutputObjectName`
field does NOT create namespacing — items targeting `OutputObjectName: "MyGroup"`
still appear at the top level (same as `"json"`). Only colon-paths in
`OutputFieldName` create structure.

**Supported prefixes using this pattern:**
- `IMG_<name>:<prop>` — Dynamic images (`src`, `width`, `height`)
- `HYP_<name>:<prop>` — Hyperlinks (`url`, `text`)
- Any custom nested object

### Array Pass-Through — Colon-Path Iteration (Live-Verified)

When the input contains an array, colon-path `InputFieldName` automatically
iterates over array elements:

```
Input:   {"Lines": [{"Name": "W", "Price": 100}, {"Name": "G", "Price": 200}]}
Items:
  Lines:Name  → Lines:ProductName   (renames field within array)
  Lines:Price → Lines:Amount        (renames field within array)

Output:  {"Lines": [{"ProductName": "W", "Amount": 100}, {"ProductName": "G", "Amount": 200}]}
```

**Renaming the array path:**
```
  Lines:Name  → Output:ProductName  (moves to different array name)
  Lines:Price → Output:Amount

Output:  {"Output": [{"ProductName": "W", "Amount": 100}, ...]}
```

**WARNING — Cross-array merge produces cartesian product:**

Mapping fields from TWO different input arrays to the SAME output path
produces N×M entries (identical to Extract behavior):

```
Input:   {"Items": [{A}, {B}], "Details": [{X}, {Y}]}
Items:
  Items:Name    → Combined:Name
  Details:SKU   → Combined:SKU

Output:  {"Combined": [{A,X}, {A,Y}, {B,X}, {B,Y}]}  ← 2×2 = 4 entries
```

**Rule:** Each output array path should source from exactly ONE input array.
Use the Extract hierarchy to pre-join related data, not the Transform.

### OutputFieldFormat — Value Formatting (Live-Verified)

| Format | Effect | Example |
|--------|--------|---------|
| *(blank)* | Pass-through unchanged | `123.456` → `123.456` |
| `Boolean` | Coerces string → boolean | `"true"` → `true` |
| `Number(N)` | Rounds to N decimals, returns **string** | `123.456` → `"123.46"` |
| `Currency` | Adds `$` prefix + comma separators | `1234.5` → `"$1,234.50"` |
| `Object` | Marks value as a nested object/array (for Object Output items) | |

**Key behaviors:**
- `Boolean` format is needed when the input is a **string** `"true"`/`"false"`.
  When a formula already produces a boolean (`IF(..., true, false)`), the
  format is redundant — the value is already typed correctly.
- `Number(N)` converts the number to a **formatted string** — not a rounded
  number. Use only for display tokens, not for values that downstream
  formulas will reference.
- `Currency` similarly produces a formatted string.

### OutputObjectName — No Effect on Structure (Live-Verified)

For pass-through items, `OutputObjectName` has **no effect** on output
structure. Items targeting `OutputObjectName: "SomeGroup"` produce the
exact same top-level output as `OutputObjectName: "json"`.

**Valid values:**
- `"json"` — standard for pass-throughs and field mappings (use this)
- `"Formula"` — required for formula items (formulas break with other values)
- Any other string — accepted but functionally identical to `"json"`

**Do NOT use** `OutputObjectName` to group output. Use colon-separated
`OutputFieldName` instead (see Nested Objects section above).

### Transform Cannot Add Per-Element Booleans to Existing Arrays

(Detailed in Formula Engine section above.) Transform formulas operate on
the scalar/top-level data pool. They cannot iterate over array elements to
produce per-element values. For per-element conditionals, add the field in
the Extract phase (e.g., a formula field on the queried object) or use the
section-as-conditional pattern in the template.

### When to Use Transform Formulas vs Extract Formulas

| Need | Use Transform formula | Use Extract mapping |
|------|-----------------------|---------------------|
| String concatenation for display | YES — `CONCAT(First, ' ', Last)` | No (Extract queries raw fields) |
| Conditional boolean for `{{#IF_x}}` | YES — `IF(val > 0, true, false)` | No |
| Computed URL for hyperlinks | YES — `CONCAT('https://.../', Id)` | No |
| Constant values (dimensions, defaults) | YES — `CONCAT('200', '')` | No |
| Array building from flat cross-joins | YES — `LIST(...)` | Or use Extract hierarchy |
| Per-record field extraction | No | YES — Extract queries the field |
| Related-object traversal | No | YES — Extract joins related objects |
| Aggregate/rollup values | Limited (no SUM/COUNT) | Must pre-compute in Apex/formula field |

### Missing Input Behavior (Live-Verified)

| Situation | Behavior |
|-----------|----------|
| Pass-through references missing key | Field **absent** from output (not null) |
| Formula references missing variable | Treated as **empty string** for CONCAT, **falsy** for comparisons |
| Formula IF(missing > N) | Evaluates to **false** (undefined < any number) |
| Input is array `[{...}]` | Works identically to object `{...}` |
| Input has extra keys not mapped | Silently ignored |

### FormulaSequence Ordering (Live-Verified)

Formulas within OCS=0 execute in `FormulaSequence` order. A formula at
seq=2 CAN reference the `FormulaResultPath` of a formula at seq=1.
Formulas at the SAME sequence number cannot reference each other.

```
Seq 1: CONCAT(First, ' ', Last) → "FullName"     ← runs first
Seq 2: CONCAT('Hello, ', FullName, '!') → "Greeting"  ← can reference FullName ✓
Seq 1: CONCAT(Greeting, ' Welcome.') → "Welcome"  ← CANNOT reference Greeting (same seq, runs in parallel)
```

### LIST() Formula — Extract vs Transform Context

`LIST()` is designed for **Extract** context where cartesian-product flat
rows need to be rolled into template arrays. In Transform context, LIST()
produces a raw flat array `[null, "key1", val1, "key2", val2, ...]` which
is NOT template-ready.

**For Transforms: use colon-path pass-throughs for array manipulation.**
They automatically iterate input array elements and can rename/restructure:
```
Input:  {"Lines": [{"Name": "W", "Price": 100}]}
Item:   InputFieldName: "Lines:Name" → OutputFieldName: "Products:Label"
Output: {"Products": [{"Label": "W"}]}
```

### REST API Testing Pattern for Transforms

```bash
# Full pipeline test (Extract → Transform → verify output)
python scripts/docgen/docgen_odt_execute.py MyExtract \
  --record-id 0Q0XXXXXXXXXXXXAAA --org dev-scratch --json > /tmp/extract.json

python scripts/docgen/docgen_odt_execute.py MyTransform \
  --input /tmp/extract.json --org dev-scratch

# With --json for raw output, --count for quick validation
python scripts/docgen/docgen_odt_execute.py MyTransform \
  --input /tmp/extract.json --org dev-scratch --json
```

**Endpoint:** Same as Extract: `POST /services/data/v67.0/omnistudio/dataraptor/<Name>`
**Body:** The full Extract output JSON (array or object)
**Response:** The template-ready JSON with all tokens resolved

---

### ODT Preview / Simulate API (Aura — Debug Use Only)

The OmniStudio Designer "Preview" button invokes an Aura controller action.
Provides `debugLog` with exact SOQL, but requires active Lightning session
auth (cannot be used from CLI/agents without a browser session).

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
- Use for **debugging** filter/query issues; use the REST API above for **automated validation**
