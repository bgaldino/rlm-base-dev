# Template Lifecycle, Execution and Testing

Read when managing a DocumentTemplate (list, replace, create, download), executing an Extract or Transform on its own, linting or diffing ODTs, or running a full generation to verify output. Parent: [document-generation](SKILL.md).

## ODT Context for Template Authors

| Path | Use When | Supportability |
|------|----------|----------------|
| **Metadata API** (`.rpt-meta.xml`) | Committed assets, CI/CD, `prepare_docgen` | Fully supported — official metadata type since API v54.0 |
| **OmniStudio Designer UI** | Prototyping, visual editing | Fully supported |
| **SObject REST API** (`docgen_odt_*`) | Scratch-org repair, rapid iteration, debugging | **Internal use only** — not supported for production |

### Metadata API (Primary)

ODTs are source-controlled as XML in `unpackaged/post_docgen/omniDataTransforms/`:
```
unpackaged/post_docgen/omniDataTransforms/
  RLMQuoteExtractBasic_1.rpt-meta.xml
  RLMQuoteTransformBasic_1.rpt-meta.xml
  BillingDocumentGenerationGetInvoiceDetails_1.rpt-meta.xml
  ...
```

Deploy via `cci flow run prepare_docgen --org dev-scratch`. See
`docs/guides/docgen-setup.md` for the full 10-step deployment sequence
(formula field pre-deploy, ODT seed workaround, binary fix).

### SObject REST API (ODT Experimentation Only)

> **Salesforce official warning** (from [SObject API reference](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-omnidatatransform.html)):
> *"This object and associated records are only for internal use. Don't perform
> any create, edit, or delete operations on this object. Modifying or deleting
> this object's records may result in errors with your implementation."*

The ODT helper scripts (`docgen_odt_*`) use this API for rapid scratch-org
iteration. They are appropriate for:
- Debugging blank output (inspecting/fixing items quickly)
- Cloning an ODT to experiment with variations
- Validating item structure before committing as Metadata API XML
- **Executing Extracts/Transforms** for automated testing (`docgen_odt_execute.py`)
- **Full document generation** end-to-end (`docgen_template_generate.py`)

They are **NOT** appropriate for production deployment.

### Template Lifecycle Management

The `docgen_template_manage.py` script manages the full DocumentTemplate
lifecycle: list, inspect, activate/deactivate, upload/replace binary,
create new templates, and download source or generated files.

```bash
# List all templates in an org
python scripts/docgen/docgen_template_manage.py list --org dev-scratch

# Show detail for a specific template
python scripts/docgen/docgen_template_manage.py status RLM_QuoteProposal --org dev-scratch

# Full replace lifecycle (deactivate → upload → reactivate)
python scripts/docgen/docgen_template_manage.py replace RLM_QuoteProposal template.docx --org dev-scratch

# Download template source .docx
python scripts/docgen/docgen_template_manage.py download --template RLM_QuoteProposal --org dev-scratch -o out.docx

# Download generated output by ContentVersion ID (from DGP ResponseText)
python scripts/docgen/docgen_template_manage.py download --version-id 068XXXXXXXXXXXXAAA --org dev-scratch -o out.pdf

# Create new template with ODT wiring
python scripts/docgen/docgen_template_manage.py create RLM_NewProposal template.docx --org dev-scratch \
  --extract-odt RLMQuoteProposalExtract --transform-odt RLMQuoteProposalTransform \
  --usage-type Revenue_Lifecycle_Management --activate
```

Use `--template-id <2dt...>` or `--content-doc-id <069...>` on mutating
commands when disambiguation is needed.

**Key behaviors:**
- DGP `ResponseText` returns 15-char ContentVersion IDs (e.g., `068xxxxxxxxxxxx`);
  the download command accepts both 15- and 18-char IDs.
- Generated `.docx` output is inspectable with `python-docx` (tables, paragraphs,
  token fill values). PDF output is compressed and requires `poppler` for text
  extraction — prefer downloading the `.docx` intermediate for verification.
- To get both `.docx` and `.pdf` from a single DGP run, set
  `"keepIntermediate": true` in `RequestText`.
- `RequestText` must include `templateContentVersionId` (the 068 ID of the
  template binary). Without it, DGP returns `INVALID_INPUT`.

### Context Service DGP Contract

When `DocumentTemplate.TokenMappingMethodType` is `ContextService`, the
Document Generation engine resolves the definition and mapping from the template.
Set the DGP fields as follows:

| Field | Required value |
|-------|----------------|
| `ReferenceObject` | Root source-record ID |
| `DocGenAdditionalInputType` | `ContextService` |
| `DocGenAdditionalInput` | The same root source-record ID as a plain string |

Do not put the Context Service runtime API's `{"inputData": ...}` request body in
`DocGenAdditionalInput`. For a hierarchical context, map each auto-created child
`ParentReference` to the child SObject's lookup to its parent (for example,
`QuoteLineItem.QuoteId`) so repeating template sections hydrate correctly.

### OmniStudio REST API (Execution & Testing)

The OmniStudio REST endpoint executes ODTs with standard OAuth (no
Lightning session needed). Works for both Extracts and Transforms:

```bash
# Execute an Extract against a record
python scripts/docgen/docgen_odt_execute.py RLMQuoteProposalExtract --record-id 0Q0XXXXXXXXXXXXAAA --org dev-scratch

# Execute a Transform (pass Extract output as input)
python scripts/docgen/docgen_odt_execute.py RLMQuoteProposalTransform --input extract_output.json --org dev-scratch

# Pipeline: Extract → Transform (--json pipes output)
python scripts/docgen/docgen_odt_execute.py RLMQuoteProposalExtract --record-id 0Q0XXXXXXXXXXXXAAA --org dev-scratch --json > /tmp/e.json
python scripts/docgen/docgen_odt_execute.py RLMQuoteProposalTransform --input /tmp/e.json --org dev-scratch

# Full end-to-end generation: see the docgen_template_generate.py examples under Helper scripts below
```

Use this for:
- Automated validation of Extract output (entry counts, field presence)
- Phantom-entry detection (compare expected vs actual entry count)
- Transform output verification before wiring to a template
- End-to-end template smoke tests (DGP script triggers generation + polls)

### Static inspection — validate and diff without executing

Two helpers read an ODT's items straight from the org, so they work before you
have a record to execute against:

```bash
# Lint one ODT's items: null fields, duplicate keys, malformed dot notation
python scripts/docgen/docgen_odt_validate.py RLMQuoteProposalExtract --org dev-scratch

# Diff two ODTs item-by-item — the fastest way to find what a clone lost
python scripts/docgen/docgen_odt_compare.py RLMQuoteProposalExtract RLMInvoiceExtract --org dev-scratch

# Create an ODT from a JSON spec (--example extract|transform emits a starter spec)
python scripts/docgen/docgen_odt_create.py spec.json --org dev-scratch
```

`docgen_odt_create.py`'s spec format, cloning patterns, and shell-escaping
pitfalls are in `data-mapper-authoring.md`; `odt-authoring/SKILL.md` covers
authoring the mapper itself.

Reach for `docgen_odt_validate.py` when an Extract returns empty or partial
output and you want to rule out the mapper before blaming the data, and for
`docgen_odt_compare.py` when a cloned ODT misbehaves — cloning is the pattern
this skill recommends (see `data-mapper-authoring.md`), and a silent item drop
during a clone is its characteristic failure.

## Helper scripts

Scripts in `scripts/docgen/` support document generation workflows.
Install deps first: `pip install -r scripts/docgen/requirements.txt`

```bash
# ODT workflows are covered by ../odt-authoring/SKILL.md (docgen_odt_* commands).

# Extract all mustache tokens from a .docx template
python scripts/docgen/docgen_template_extract_tokens.py template.docx
python scripts/docgen/docgen_template_extract_tokens.py template.docx --validate-transform RLMQuoteProposalTransform --org dev-scratch

# Build/modify .docx templates programmatically (requires python-docx)
# NOTE: replace/audit operate on body + tables only — headers/footers NOT searched.
# Use docgen_template_extract_tokens.py for full-template token inventory (includes headers/footers).
python scripts/docgen/docgen_template_build.py create layout.json --output template.docx
python scripts/docgen/docgen_template_build.py replace template.docx --tokens '{"Old": "New"}'
python scripts/docgen/docgen_template_build.py audit template.docx
python scripts/docgen/docgen_template_build.py --example > layout.json   # generate layout spec

# Full document generation (DGP): Extract → Transform → .docx → PDF
python scripts/docgen/docgen_template_generate.py --record-id 0Q0XXXXXXXXXXXXAAA --template-id 2dtXXXXXXXXXXXXAAA --org dev-scratch
python scripts/docgen/docgen_template_generate.py --record-id 0Q0XXXXXXXXXXXXAAA --template-id 2dtXXXXXXXXXXXXAAA --org dev-scratch --no-convert  # .docx only
python scripts/docgen/docgen_template_generate.py --record-id 0Q0XXXXXXXXXXXXAAA --template-id 2dtXXXXXXXXXXXXAAA --org dev-scratch --title "Custom Name"
python scripts/docgen/docgen_template_generate.py --record-id 0Q0XXXXXXXXXXXXAAA --template-id 2dtXXXXXXXXXXXXAAA --org dev-scratch --dry-run
```
