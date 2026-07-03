# OmniStudio Document Generation

Use this skill when creating, modifying, or troubleshooting Salesforce OmniStudio
document templates (`.docx`) and their associated OmniDataTransform (ODT) data
mappers. Covers the full pipeline: template authoring, Extract/Transform ODT
wiring, token mapping, image handling, and deployment to an org.

## Quick Rules

1. **Two ODTs per template** — an Extract (queries org data) and a Transform
   (reshapes it for template tokens). The DocumentTemplate record references both
   by name.
2. **Token syntax** — `{{FieldName}}` for scalars, `{{#Section}}...{{/Section}}`
   for repeating rows, `{{IMG_name}}` for images.
3. **Colon notation in Extract** — field paths use colons: `Invoice:Account:Name`,
   never dots.
4. **Every item needs `OutputObjectName`** — omitting it causes a null-pointer
   crash: `"getOutputObjectName()" is null`. Set to `"json"` for field mappings
   and pass-throughs; set to `"Formula"` for formula items.
5. **Object queries need `InputFieldName` + `FilterGroup`** — the match field
   (usually `Id`) and filter group (`0`) are mandatory on every object query item.
6. **ContentDocument for dynamic images** — the `IMG_` nested object's `src`
   field requires a ContentDocument Id (`069` prefix). ContentVersion Id (`068`)
   or file Title crashes the engine.
7. **Metadata API for committed work** — production ODTs are authored as
   `.rpt-meta.xml` under `unpackaged/post_docgen/omniDataTransforms/` and deployed
   via `prepare_docgen`. The SObject REST API (helper scripts) is for scratch-org
   experimentation and repair only.
8. **Activate after changes** — toggle `IsActive` false→true on both ODTs after
   creating or modifying items; the cache doesn't refresh automatically.
   (Applies to REST-based scratch-org edits only.)


## DO NOT

- **DO NOT** use dot notation in Extract `InputFieldName` — use colons
  (`Invoice:PaymentTerm:Name`, not `Invoice.PaymentTerm.Name`).
- **DO NOT** leave `OutputObjectName` null on any OmniDataTransformItem — this
  causes a runtime NPE that silently produces empty output.
- **DO NOT** create duplicate object query items — duplicates can cause the entire
  Extract to fail silently, producing no data.
- **DO NOT** pass a ContentVersion Id (`068`) or file Title to `IMG_token:src` —
  only ContentDocument Id (`069`) works; others crash the engine.
- **DO NOT** omit `width` or `height` from `IMG_` token objects — the image
  silently fails to render if either dimension is missing.
- **DO NOT** edit `TargetOutputFileName` or `MapperOmniDataTransformName` while the
  DocumentTemplate or ODT is Active — deactivate first.
- **DO NOT** use the SObject REST API to create/edit/delete ODTs in shared,
  production, or customer orgs — the official docs say these records are "for
  internal use only." Use Metadata API XML instead.

---

## Entry Conditions

| Task | Use this skill? |
|------|-----------------|
| Create a new `.docx` invoice/quote/contract template | Yes |
| Wire up Extract + Transform ODTs for a template | Yes |
| Add fields/tokens to an existing template | Yes |
| Troubleshoot blank output or generation errors | Yes |
| Add dynamic images to a template | Yes — see `dynamic-images.md` |
| Create ODT items programmatically via API | Yes — see `data-mapper-authoring.md` |

---

## Supported Paths for ODT Authoring

| Path | Use When | Supportability |
|------|----------|----------------|
| **Metadata API** (`.rpt-meta.xml`) | Committed assets, CI/CD, `prepare_docgen` | Fully supported — official metadata type since API v54.0 |
| **OmniStudio Designer UI** | Prototyping, visual editing | Fully supported |
| **SObject REST API** (helper scripts) | Scratch-org repair, rapid iteration, debugging | **Internal use only** — not supported for production |

### Metadata API (Primary)

ODTs are source-controlled as XML in `unpackaged/post_docgen/omniDataTransforms/`:
```
unpackaged/post_docgen/omniDataTransforms/
  RLMQuoteExtractBasic_1.rpt-meta.xml
  RLMQuoteTransformBasic_1.rpt-meta.xml
  BillingDocumentGenerationGetInvoiceDetails_1.rpt-meta.xml
  ...
```

Deploy via `cci flow run prepare_docgen --org <alias>`. See
`docs/guides/docgen-setup.md` for the full 10-step deployment sequence
(formula field pre-deploy, ODT seed workaround, binary fix).

### SObject REST API (Experimentation Only)

> **Salesforce official warning** (from [SObject API reference](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_omnidatatransform.htm)):
> *"This object and associated records are only for internal use. Don't perform
> any create, edit, or delete operations on this object. Modifying or deleting
> this object's records may result in errors with your implementation."*

The helper scripts in `scripts/ai/docgen/` use this API for rapid scratch-org
iteration. They are appropriate for:
- Debugging blank output (inspecting/fixing items quickly)
- Cloning an ODT to experiment with variations
- Validating item structure before committing as Metadata API XML
- **Executing Extracts/Transforms** for automated testing (`docgen_execute_odt.py`)
- **Full document generation** end-to-end (`docgen_generate_document.py`)

They are **NOT** appropriate for production deployment.

### OmniStudio REST API (Execution & Testing)

The OmniStudio REST endpoint executes ODTs with standard OAuth (no
Lightning session needed). Works for both Extracts and Transforms:

```bash
# Execute an Extract against a record
python scripts/ai/docgen/docgen_execute_odt.py <odt_name> --record-id <id> --org <alias>

# Execute a Transform (pass Extract output as input)
python scripts/ai/docgen/docgen_execute_odt.py <odt_name> --input extract_output.json --org <alias>

# Pipeline: Extract → Transform (--json pipes output)
python scripts/ai/docgen/docgen_execute_odt.py MyExtract --record-id <id> --org <alias> --json > /tmp/e.json
python scripts/ai/docgen/docgen_execute_odt.py MyTransform --input /tmp/e.json --org <alias>

# Full end-to-end document generation (DGP: Extract → Transform → .docx → PDF)
python scripts/ai/docgen/docgen_generate_document.py \
  --record-id <id> --template-id <templateId> --org <alias>
```

Use this for:
- Automated validation of Extract output (entry counts, field presence)
- Phantom-entry detection (compare expected vs actual entry count)
- Transform output verification before wiring to a template
- End-to-end template smoke tests (DGP script triggers generation + polls)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DocumentTemplate                          │
│  Name: "RLM_InvoiceTemplate_v2"                             │
│  Type: MicrosoftWord                                        │
│  ExtractOmniDataTransformName: "RLMInvoiceGetDetails"       │
│  MapperOmniDataTransformName: "RLMInvoiceTransformDetails"  │
│  TokenMappingMethodType: "OmniDataTransform"                │
│  UsageType: "Invoice"                                       │
└──────────────┬──────────────────────────┬───────────────────┘
               │                          │
    ┌──────────▼──────────┐    ┌──────────▼──────────┐
    │   Extract ODT       │    │   Transform ODT     │
    │   Type: "Extract"   │    │   Type: "Transform" │
    │   InputType: "JSON" │    │   InputType: "JSON" │
    │   OutputType: "JSON"│    │   OutputType: "JSON" │
    └──────────┬──────────┘    └──────────┬──────────┘
               │                          │
    ┌──────────▼──────────┐    ┌──────────▼──────────┐
    │  OmniDataTransform  │    │  OmniDataTransform  │
    │  Items (2 types):   │    │  Items (3 types):   │
    │  • Object Queries   │    │  • Pass-through     │
    │  • Field Mappings   │    │  • Formula          │
    └─────────────────────┘    │  • Image objects    │
                               └─────────────────────┘
```

**Data flow (live-verified via REST API):**

```
1. TRIGGER: DocumentGenerationProcess record inserted
   Input: {"Id": "<recordId>"}
   (DGP reads DocumentTemplate → resolves Extract + Transform names)

2. EXTRACT: POST /omnistudio/dataraptor/<ExtractName>
   - Receives: {"Id": "<recordId>"}
   - Executes object queries (SOQL) per sequence number
   - Applies filters (FilterValue + FilterOperator + FilterGroup)
   - Maps InputFieldName → OutputFieldName on field mapping items
   - Returns: raw data JSON (nested arrays/objects reflecting hierarchy)

3. TRANSFORM: POST /omnistudio/dataraptor/<TransformName>
   - Receives: Extract output JSON (entire response, as-is)
   - Applies: pass-through renames, formula computations (LIST, IF, CONCAT),
     object builders (IMG_, HYP_), Boolean casts (IF_ conditions)
   - Returns: template-ready JSON (keys = exact token names in .docx)

4. RENDER: Engine merges Transform output with .docx template
   - Scalar tokens: {{TokenName}} → replaced with string value
   - Repeating sections: {{#Array}}...{{/Array}} → one row per array element
   - Conditional sections: {{#IF_x}}...{{/IF_x}} → rendered/hidden by Boolean
   - Dynamic content: IMG_, HYP_, RTB_ → rendered per their contract
   - Output: .docx (intermediate)

5. CONVERT (optional): .docx → .pdf via Microsoft 365 service
   - Only when DGP.Type = "GenerateAndConvert"
   - Output: two ContentVersions (068 IDs) — .docx + .pdf

6. COMPLETE: DGP.Status → "Success", ResponseText = comma-separated 068 IDs
```

**Testable at each stage:**
- Stage 2: `python scripts/ai/docgen/docgen_execute_odt.py <extract> --record-id <id> --org <alias>`
- Stage 3: `sf api request rest --method POST --body @extract_output.json /services/data/v67.0/omnistudio/dataraptor/<transform> --target-org <alias>`
- Full pipeline: `python scripts/ai/docgen/docgen_generate_document.py --record-id <id> --template-id <id> --org <alias>`

---

## Token Reference

| Token Type | Syntax | Example | Transform Output |
|-----------|--------|---------|-----------------|
| Scalar | `{{Name}}` | `{{InvoiceNumber}}` | `"InvoiceNumber": "INV-001"` |
| Repeating section | `{{#List}}...{{/List}}` | `{{#InvoiceLines}}{{ProductName}}{{/InvoiceLines}}` | `"InvoiceLines": [{...}, ...]` |
| Truthy gate | `{{#Field}}...{{/Field}}` | `{{#GrantType}}row content{{/GrantType}}` | Renders when field is non-empty string/object; skips when absent/null/empty |
| Condition (boolean) | `{{#IF_x}}...{{/IF_x}}` | `{{#IF_has_discount}}...{{/IF_has_discount}}` | `"IF_has_discount": true` (Boolean only) |
| Inverse condition | `{{^IF_x}}...{{/IF_x}}` | `{{^IF_no_discount}}...{{/IF_no_discount}}` | Shows when value is `false`; hidden when `true` |
| Image | `{{IMG_name}}` | `{{IMG_CompanyLogo}}` | `{"src": "069...", "width": "200", "height": "80"}` (see `dynamic-images.md`) |
| Hyperlink | `{{HYP_name}}` | `{{HYP_PaymentLink}}` | `{"url": "https://...", "text": "label"}` |
| Rich text | `{{RTB_name}}` | `{{RTB_TermsContent}}` | HTML string: `"<b>Bold</b> <a href='...'>link</a>"` |

### Dynamic Content Token Notes

**RTB_ (Rich Text)** — **Confirmed working.** Pass an HTML string directly.
Supports `<b>`, `<i>`, `<ul>/<li>`, `<a href>` (renders clickable links),
and inline images. Best option for hyperlinks (renders with formatting).
- **Limitation:** RTB tokens must NOT be placed within a paragraph (causes
  generation failure). Place them as standalone blocks.
- **Limitation:** Bullets in template surrounding RTB tokens are not supported.

**IMG_ (Dynamic Images)** — **Confirmed working** with specific requirements:
- `src`: ContentDocument ID (`069` prefix) — **required**
- `width`: pixel string — **required**
- `height`: pixel string — **required**
- Image must be in a Content Library accessible to the Integration User
- See `dynamic-images.md` for full verified contract

**HYP_ (Hyperlinks)** — **Confirmed working.** Requires:
- Field name must be `"url"` (NOT `"src"`) — using `src` causes the "URL is invalid" error
- Template token must be **plain text** — do NOT format as a Word hyperlink (Cmd+K / Ctrl+K)
- `"text"` is optional — if omitted, the URL itself is displayed as the link text
- Alternative: RTB_ with `<a>` tags also works and offers richer formatting control

**IF_ (Conditions)** — Must receive **Boolean values only** (`true`/`false`).
Strings and numbers always evaluate as `true`, causing unexpected rendering.
Use `IF(expression, true, false)` formula in the Transform.

### Page Break and Token Spacing Guidelines

- **DO NOT** place page breaks directly before `{{#IF_` or `{{#Section}}` start
  tokens — creates blank pages when condition is false or section is empty.
- **DO NOT** place page breaks directly after `{{/IF_` or `{{/Section}}` end
  tokens — same blank page issue.
- **DO** place page breaks **between** sections, not adjacent to token markers.
- **Remove empty lines between adjacent conditional tokens** — the engine
  interprets whitespace between tokens as content, creating blank pages.

### Repeating Sections in Tables

Place `{{#SectionName}}` in the first cell of the data row and
`{{/SectionName}}` in the last cell. The engine duplicates the entire row for
each array element:

```
| Product                         | Qty          | Amount                        |
| {{#InvoiceLines}}{{ProductName}}| {{Quantity}} | {{Subtotal}}{{/InvoiceLines}} |
```

---

## Extract ODT — Item Types

### Object Query Items

Define which SObjects to query and how to join them:

| Field | Purpose | Example |
|-------|---------|---------|
| `InputObjectName` | SObject to query | `Invoice` |
| `InputFieldName` | Field on this object to match against FilterValue (see below) | `Id`, `InvoiceId` |
| `OutputFieldName` | Internal hierarchy path (join scope) | `Invoice`, `Invoice:Account` |
| `OutputObjectName` | Always `json` | `json` |
| `InputObjectQuerySequence` | Execution order (1, 2, 3...) | `1` |
| `FilterOperator` | Match operator | `=` |
| `FilterValue` | Value or path to match | `Id` (for root), `Invoice:BillingAccountId` (for FK lookup) |
| `FilterGroup` | Required grouping | `0` |

**InputFieldName semantics (critical — generates the WHERE clause):**
```
WHERE <InputFieldName> = <resolved FilterValue>
```

Two join patterns:

| Pattern | InputFieldName | FilterValue | Meaning |
|---------|---------------|-------------|---------|
| **Root** (input param) | `Id` | `Id` | Match input `Id` param → this object's `Id` |
| **FK lookup** (many:1) | `Id` | `Parent:FKField` | Match parent's FK → target's `Id` (1 result per parent) |
| **Child-of** (1:many) | Child's FK field | `Parent:Id` | Match parent's Id → child's FK (0..N per parent) |

**Examples:**
```
Seq 1: Invoice,     InputFieldName="Id",        FilterValue="Id"                        ← root
Seq 4: Account,     InputFieldName="Id",        FilterValue="Invoice:BillingAccountId"  ← FK lookup (safe)
Seq 5: InvoiceLine, InputFieldName="InvoiceId", FilterValue="Invoice:Id"                ← child-of (1:many)
```

**Multi-filter objects** (e.g., InvoiceLine with type filter):
```
Seq 3: InvoiceLine, InputFieldName=InvoiceId, FilterValue="Invoice:Id"
Seq 3: InvoiceLine, InputFieldName=Type,      FilterValue="\"Charge\""
```
Note: literal string filters use embedded quotes: `"\"Charge\""`.

### Field Mapping Items

Extract specific fields from queried objects:

| Field | Purpose | Example |
|-------|---------|---------|
| `InputFieldName` | Source path (colon-separated) | `Invoice:Account:BillingCity` |
| `OutputFieldName` | Key in Extract output | `BillingCity` |
| `OutputObjectName` | Always `json` | `json` |
| `OutputCreationSequence` | Usually `1` | `1` |

---

## Transform ODT — Item Types

### Pass-through Mappings

Simple field rename from Extract output to template token:

| Field | Purpose | Example |
|-------|---------|---------|
| `InputFieldName` | Key from Extract output | `BillingCity` |
| `OutputFieldName` | Template token name | `BillingCity` |
| `OutputObjectName` | Always `json` | `json` |
| `OutputCreationSequence` | `1` for simple mappings | `1` |

### Formula Items (Repeating Sections)

Build arrays for `{{#Section}}` tokens:

| Field | Purpose | Example |
|-------|---------|---------|
| `OutputFieldName` | `Formula` | `Formula` |
| `OutputObjectName` | `Formula` | `Formula` |
| `FormulaExpression` | Function call | `FUNCTION('invoice_docgen.InvoiceDocumentGeneration', 'InvoiceLineCustom', ...)` |
| `FormulaConverted` | RPN form (auto-generated on save — UI and API) | `\| ... FUNCTION` |
| `FormulaResultPath` | Output key name | `InvoiceLines` |
| `FormulaSequence` | Execution order | `1` |
| `OutputCreationSequence` | `0` (runs before mappings) | `0` |

### Object Output Items (Array Pass-through)

After a formula builds an array, map it to the template:

| Field | Purpose | Example |
|-------|---------|---------|
| `InputFieldName` | Formula result key | `InvoiceLines` |
| `OutputFieldName` | Template section name | `InvoiceLines` |
| `OutputObjectName` | `json` | `json` |
| `OutputFieldFormat` | `Object` (for arrays/objects) | `Object` |
| `OutputCreationSequence` | `1` | `1` |

---

## DocumentTemplate Record

| Field | Value | Notes |
|-------|-------|-------|
| `Name` | Template name | No underscores in API Name |
| `Type` | `MicrosoftWord` | For `.docx` templates |
| `TokenMappingType` | `JSON` | Always JSON for ODT approach |
| `TokenMappingMethodType` | `OmniDataTransform` | Links to ODT framework |
| `ExtractOmniDataTransformName` | Extract ODT name | Must match exactly |
| `MapperOmniDataTransformName` | Transform ODT name | Must match exactly |
| `UsageType` | `Invoice`, `Quote`, etc. | Object context |
| `Status` | `Active` / `Draft` | Must be Draft to edit |
| `IsActive` | `true` / `false` | Must be false to edit |

---

## Validation Checks

### Before generation

1. Both ODTs are Active (`IsActive: true`)
2. DocumentTemplate references correct ODT names (exact match, case-sensitive)
3. No items with null `OutputObjectName`:
   ```sql
   SELECT Id, OutputFieldName FROM OmniDataTransformItem
   WHERE OmniDataTransformationId = '<id>' AND OutputObjectName = null
   ```
4. No duplicate object query items (same Seq + OutputFieldName + FilterValue)
5. All object queries have `InputFieldName` and `FilterGroup` set
6. Field mapping paths use colons, not dots

### Common Extract Architecture Pitfalls

| Pitfall | Symptom | Root Cause | Fix |
|---------|---------|------------|-----|
| Cartesian product | N×M rows instead of N+M | Two multi-record sequences at the same nesting level | Nest child under parent via hierarchical OutputFieldName |
| FilterGroup cartesian | Records × groups explosion | Multiple FilterGroups on a nested child sequence | Use separate independent hierarchy instead of OR filters |
| Missing children | Only top-level records' children appear | Parent sequence has restrictive filter (e.g., ParentId = null) | Create separate root query without the restriction |
| Singleton instead of array | One object instead of array | Root-level OutputFieldName or all records collapse to same context | Nest under a parent (e.g., `Quote:MyArray` not just `MyArray`) |
| Null field values | Field silently blank | Relationship traversal without explicit join sequence | Use direct field or add join sequence for intermediate object |
| Output path confusion | Data in wrong JSON location | Using internal hierarchy paths for output field mappings | Use separate top-level output path (e.g., `Line:*` not `Quote:QuoteLineItem:*`) |
| Mixed-depth leakage | Parent + child count entries (e.g., 7+5=10 instead of 5) | Field mappings for same output array read from different hierarchy depths | All mappings must read from same depth — use redundant join for parent fields |
| Grantless parents in array | Empty rows for records without children | No subquery filtering; parent-level mapping includes all parents | Use child-first hierarchy with redundant parent join at child level |

### Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| All tokens blank | Extract failing (duplicates, NPE) | Check for duplicate object queries, null OutputObjectName |
| `getOutputObjectName() is null` | Item missing OutputObjectName | Set `OutputObjectName: "json"` on all items |
| "mandatory details missing" in UI | Same as above, or missing InputFieldName on object queries | Add required fields |
| `[object Object]` for images | Org below Release 256 (DocGen 1.0) | Upgrade org; or use RTB_ with HTML `<img>` as fallback |
| IMG_ token consumed, no image | Missing `width`/`height`, or Integration User can't access file | Add both dimensions + add Integration User to Content Library |
| Engine crash: `Cannot read properties of undefined (reading '0')` | `src` has ContentVersion ID (`068`) or file Title | Use ContentDocument ID (`069`) only |
| HYP_ shows red "URL is invalid" error | Wrong field name (`src` instead of `url`) or token formatted as Word hyperlink | Use `"url"` field (not `"src"`); ensure token is plain text in template |
| Template locked for edits | Active status | Deactivate (`IsActive: false, Status: Draft`) first |
| Specific token blank | Field not in Extract or Transform | Trace: is field queried? Is it mapped through both ODTs? |
| Repeating section empty | Formula item missing or wrong ResultPath | Check formula at `OutputCreationSequence: 0` |
| Formula produces no output | Unsupported function (FormulaConverted is null) | Check `FormulaConverted` field — if null, the function isn't supported. See Formula Function Catalog below |
| ODT Name rejected on create | Contains underscores or spaces | Use camelCase only — alphanumeric, no special chars |
| More array entries than expected | Field mappings at mixed hierarchy depths | Run `docgen_inspect_hierarchy.py` — all mappings for same output array must be at uniform depth |
| Array is singleton (object, not list) | OutputFieldName at root level | Nest under parent: use `Root:ArrayName` not just `ArrayName` |
| Missing child records in output | Parent sequence has restrictive filter | Child sequences inherit parent scope — create independent hierarchy with broader filter |
| N×M×G explosion in child results | Multiple FilterGroups on nested sequence | Each parent × each FilterGroup evaluated independently — use single FilterGroup or separate hierarchy |

---

## Platform Behavior Reference

> Full detail: **[`extract-engine-reference.md`](extract-engine-reference.md)**
> (formula catalog, filter mechanics, hierarchy semantics, array patterns, Preview API)

Verified on Release 262, API v67.0. Key concepts summarized below;
read the sub-file when designing or debugging complex Extracts.

### Critical Rules (quick reference)

| Rule | Detail |
|------|--------|
| **Internal ≠ Output paths** | Object query `OutputFieldName` (join scope) is decoupled from field mapping `OutputFieldName` (JSON shape). They share colon syntax but are independent namespaces. |
| **Depth uniformity** | ALL field mappings for the same output array must read from the same internal hierarchy depth. Mixed depths → parent entries leak into child array. |
| **Redundant join for parent fields** | To get a parent's field at child level without leaking grantless parents, re-join the parent object at the child level (Seq N filtering by child FK). |
| **Section-as-conditional** | `{{#FieldName}}...{{/FieldName}}` acts as truthy/falsy gate — renders when non-empty string/array/object; skips when absent, null, false, or empty. |
| **FilterGroup = OR** | Multiple FilterGroups are UNION ALL — on nested sequences this causes N×M×G cartesian explosion. Use only on root queries. |
| **Literals must be quoted** | `FilterValue: "'Active'"` not `FilterValue: "Active"`. Unquoted literals generate no WHERE clause. |
| **No subqueries** | Cannot filter "only parents with children." Use child-first hierarchy + redundant join pattern. |
| **Transform formulas are scalar** | `FormulaResultPath` cannot target per-array-element paths. Use section-as-conditional instead. |

### Formula Quick Reference

Supported: `IF`, `ISBLANK`, `CONCAT`, `SUBSTRING`, `LIST`, `FUNCTION`,
arithmetic, comparisons, `AND`/`OR`/`NOT`, `ABS`/`ROUND`/`FLOOR`/`CEILING`/`MAX`/`MIN`.

**Not supported** (saves silently, produces no output): `CASE`, `LEN`,
`UPPER`/`LOWER`, `TEXT`, `FORMAT`, `VALUE`, `MOD`, `POWER`.

### ODT Naming

Alphanumeric only (no underscores/spaces). Use camelCase: `RLMQuoteExtractBasic`.

---

## Examples

### Creating a complete template pipeline

See `data-mapper-authoring.md` for the programmatic API approach to creating
Extract + Transform ODTs with all items.

### Adding a new field to an existing template

1. **Template**: Add `{{NewField}}` token in the `.docx`
2. **Extract**: Add field mapping item — `InputFieldName: "Object:FieldApiName"`,
   `OutputFieldName: "NewField"`, `OutputObjectName: "json"`
3. **Transform**: Add pass-through — `InputFieldName: "NewField"`,
   `OutputFieldName: "NewField"`, `OutputObjectName: "json"`
4. **If field is on a new object**: Add object query item first (with proper
   Seq, InputFieldName, FilterValue, FilterGroup)
5. **Re-toggle** both ODTs (`IsActive` false → true)
6. **Upload** new `.docx` (deactivate template → replace file → reactivate)

---

## Helper Scripts

Scripts in `scripts/ai/docgen/` support document generation workflows.
Install deps first: `pip install -r scripts/ai/docgen/requirements.txt`

```bash
# Validate an ODT for common issues (null OutputObjectName, missing fields, duplicates)
python scripts/ai/docgen/validate_odt.py <odt_name_or_id> --org <sf_alias>

# Compare two ODTs item-by-item (find differences after cloning/editing)
python scripts/ai/docgen/compare_odts.py <source> <target> --org <sf_alias>

# Create an ODT from a JSON spec (no cloning required)
python scripts/ai/docgen/docgen_create_odt.py spec.json --org <sf_alias>
python scripts/ai/docgen/docgen_create_odt.py --example extract > my_spec.json   # generate spec template

# Extract all mustache tokens from a .docx template
python scripts/ai/docgen/docgen_extract_tokens.py template.docx
python scripts/ai/docgen/docgen_extract_tokens.py template.docx --validate-transform <odt_name> --org <alias>

# Build/modify .docx templates programmatically (requires python-docx)
# NOTE: replace/audit operate on body + tables only — headers/footers NOT searched.
# Use docgen_extract_tokens.py for full-template token inventory (includes headers/footers).
python scripts/ai/docgen/docgen_build_template.py create layout.json --output template.docx
python scripts/ai/docgen/docgen_build_template.py replace template.docx --tokens '{"Old": "New"}'
python scripts/ai/docgen/docgen_build_template.py audit template.docx
python scripts/ai/docgen/docgen_build_template.py --example > layout.json   # generate layout spec

# Inspect Extract hierarchy tree + validate field mapping depth uniformity
python scripts/ai/docgen/docgen_inspect_hierarchy.py <odt_name_or_id> --org <sf_alias>
python scripts/ai/docgen/docgen_inspect_hierarchy.py <odt_name_or_id> --org <alias> --validate-only
python scripts/ai/docgen/docgen_inspect_hierarchy.py <odt_name_or_id> --org <alias> --json

# Execute an Extract or Transform via REST API (automated testing)
python scripts/ai/docgen/docgen_execute_odt.py <odt_name> --record-id <id> --org <alias>
python scripts/ai/docgen/docgen_execute_odt.py <odt_name> --record-id <id> --org <alias> --json   # raw output
python scripts/ai/docgen/docgen_execute_odt.py <odt_name> --record-id <id> --org <alias> --count  # quick counts

# Full document generation (DGP): Extract → Transform → .docx → PDF
python scripts/ai/docgen/docgen_generate_document.py --record-id <id> --template-id <id> --org <alias>
python scripts/ai/docgen/docgen_generate_document.py --record-id <id> --template-id <id> --org <alias> --no-convert  # .docx only
python scripts/ai/docgen/docgen_generate_document.py --record-id <id> --template-id <id> --org <alias> --title "Custom Name"
```

---

## Deployment & Repo Integration

For the full deployment guide, see **`docs/guides/docgen-setup.md`**.

### Key points:

- **Metadata path**: `unpackaged/post_docgen/omniDataTransforms/*.rpt-meta.xml`
- **Deploy flow**: `cci flow run prepare_docgen --org <alias>` (10 steps)
- **Fresh-org bug**: ODT INSERT fails when formula fields referenced in
  `inputFieldName` don't exist yet. Steps 3–5 of `prepare_docgen` pre-deploy
  formula fields and seed stub ODT records as a workaround.
- **Binary fix**: `fix_document_template_binaries` uploads correct `.docx` binary
  after metadata deploy (Metadata API drops binary content on deploy).
- **Feature gate**: All steps gated by `project_config.project__custom__docgen`.
- **Context Service alternative**: `RLM_QuoteProposal_CS` uses Context Service
  instead of ODTs — see the setup guide for that path.

### Retrieve an ODT from a scratch org:

```bash
sf project retrieve start --metadata OmniDataTransform:RLMInvoiceGetDetails --target-org <alias>
```

Then move the retrieved `.rpt-meta.xml` to `unpackaged/post_docgen/omniDataTransforms/`.

---

## Related Skills

- `expression-sets/SKILL.md` — Expression Set authoring (pricing procedures use
  similar Connect/Metadata API patterns)
- `repo-integration/SKILL.md` — Where to place template metadata in the repo
- `sfdmu-data-plans/SKILL.md` — Loading template/ODT records via data plans
- `docs/guides/docgen-setup.md` — Full deployment sequence, bug workarounds, Context Service
