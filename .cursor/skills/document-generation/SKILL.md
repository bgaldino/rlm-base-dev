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
   crash: `"getOutputObjectName()" is null`. Always set to `"json"` for
   Extract/Transform items.
5. **Object queries need `InputFieldName` + `FilterGroup`** — the match field
   (usually `Id`) and filter group (`0`) are mandatory on every object query item.
6. **ContentVersion for dynamic images** — the `:src` mapping expects a
   ContentVersion Id (068 prefix), not ContentDocument Id (069 prefix).
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
- **DO NOT** pass a ContentDocument Id to `IMG_token:src` — the engine cannot
  resolve the blob from a 069-prefix Id.
- **DO NOT** use flat `:src`/`:height` string mappings for images expecting them to
  work server-side — the engine requires a nested JSON object structure.
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

They are **NOT** appropriate for production deployment.

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
    │   InputType: "JSON" │    │   OutputType:       │
    │   OutputType: "JSON"│    │   "Document Template│
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

**Data flow:** Input JSON (`{"Id": "recordId"}`) → Extract queries org → raw data
→ Transform reshapes → token-keyed JSON → engine merges with `.docx` template.

---

## Token Reference

| Token Type | Syntax | Example | Transform Output |
|-----------|--------|---------|-----------------|
| Scalar | `{{Name}}` | `{{InvoiceNumber}}` | `"InvoiceNumber": "INV-001"` |
| Repeating section | `{{#List}}...{{/List}}` | `{{#InvoiceLines}}{{ProductName}}{{/InvoiceLines}}` | `"InvoiceLines": [{...}, ...]` |
| Image | `{{IMG_name}}` | `{{IMG_CompanyLogo}}` | Nested object (see `dynamic-images.md`) |
| Hyperlink | `{{HYP_name}}` | `{{HYP_PaymentLink}}` | `"HYP_PaymentLink:src": "url"` |

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
| `InputFieldName` | Field to match on (usually `Id`) | `Id` |
| `OutputFieldName` | Alias for query results | `Invoice` |
| `OutputObjectName` | Always `json` | `json` |
| `InputObjectQuerySequence` | Execution order (1, 2, 3...) | `1` |
| `FilterOperator` | Match operator | `=` |
| `FilterValue` | Value or path to match | `Id` (for root), `Invoice:BillingAccountId` (for joins) |
| `FilterGroup` | Required grouping | `0` |

**Join pattern:** Later sequences reference earlier ones via colon paths:
```
Seq 1: Invoice (FilterValue: "Id")                    ← root, matches input Id
Seq 4: Account (FilterValue: "Invoice:BillingAccountId")  ← joins on FK
Seq 5: Contact (FilterValue: "Invoice:BillToContactId")
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
| `FormulaConverted` | RPN form (auto-generated in UI) | `\| ... FUNCTION` |
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

### Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| All tokens blank | Extract failing (duplicates, NPE) | Check for duplicate object queries, null OutputObjectName |
| `getOutputObjectName() is null` | Item missing OutputObjectName | Set `OutputObjectName: "json"` on all items |
| "mandatory details missing" in UI | Same as above, or missing InputFieldName on object queries | Add required fields |
| `[object Object]` for images | Flat string instead of nested JSON | Use nested object structure (see `dynamic-images.md`) |
| Logo blank | ContentDocument Id used instead of ContentVersion Id | Use `LatestPublishedVersionId` from ContentDocument |
| Template locked for edits | Active status | Deactivate (`IsActive: false, Status: Draft`) first |
| Specific token blank | Field not in Extract or Transform | Trace: is field queried? Is it mapped through both ODTs? |
| Repeating section empty | Formula item missing or wrong ResultPath | Check formula at `OutputCreationSequence: 0` |

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
python scripts/ai/docgen/docgen_build_template.py create layout.json --output template.docx
python scripts/ai/docgen/docgen_build_template.py replace template.docx --tokens '{"Old": "New"}'
python scripts/ai/docgen/docgen_build_template.py audit template.docx
python scripts/ai/docgen/docgen_build_template.py --example > layout.json   # generate layout spec
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
