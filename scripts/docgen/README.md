# Docgen Script Structure

This directory is organized by two user-facing domains:

- **ODT operations** (`docgen_odt_*`) for OmniDataTransform authoring, validation,
  comparison, execution, and hierarchy analysis.
- **Template operations** (`docgen_template_*`) for `.docx` template build/token
  work, DocumentTemplate lifecycle management, and end-to-end generation.

## Canonical entrypoints

### ODT

- `docgen_odt_validate.py`
- `docgen_odt_compare.py`
- `docgen_odt_create.py`
- `docgen_odt_execute.py`
- `docgen_odt_inspect_hierarchy.py`

### Template

- `docgen_template_build.py`
- `docgen_template_extract_tokens.py`
- `docgen_template_manage.py`
- `docgen_template_generate.py`

All command logic now lives directly in the canonical entrypoints above
(no wrapper/import indirection).

## Representative Output

Typical successful output patterns:

- `docgen_odt_validate.py`:
  - `Validation PASSED: 0 errors, 0 warnings`
- `docgen_odt_execute.py --count`:
  - `QuoteLineItems: 7`
  - `Grants: 5`
- `docgen_template_manage.py status ...`:
  - `Template: RLM_QuoteProposal (Status: Active)`
  - `ContentDocument: 069XXXXXXXXXXXXAAA`
- `docgen_template_generate.py`:
  - `DGP Id: a3eXXXXXXXXXXXXAAA`
  - `Status: Completed`
  - `ContentVersion: 068XXXXXXXXXXXXAAA`
