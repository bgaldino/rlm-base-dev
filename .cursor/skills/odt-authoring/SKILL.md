# OmniDataTransform (ODT) Authoring

Use this skill for OmniDataTransform design and troubleshooting independent of
`.docx` template authoring.

## Quick Rules

1. Model **Extract internal hierarchy** (`OutputFieldName` on object queries)
   separately from **output JSON shape** (`OutputFieldName` on field mappings).
2. Use colon paths (`Parent:Child:Field`) in ODT mappings; avoid dot notation.
3. Every `OmniDataTransformItem` must have `OutputObjectName`.
4. Object query items must include `InputFieldName` and `FilterGroup`.
5. Validate before execution; execute before wiring into templates.
6. Commit ODT metadata via `.rpt-meta.xml`; use REST writes only in scratch-org
   experimentation.

## Entry Conditions

Use this skill when you need to:

- Create or edit Extract/Transform ODTs
- Analyze hierarchy/depth and join behavior
- Debug empty output or malformed arrays
- Compare ODT revisions

Use `document-generation/SKILL.md` when your primary task is `.docx` templates,
DocumentTemplate lifecycle, token rendering, or final output verification.

## Canonical ODT Scripts

```bash
python scripts/ai/docgen/docgen_odt_validate.py RLMQuoteProposalExtract --org dev-scratch
python scripts/ai/docgen/docgen_odt_compare.py RLMQuoteProposalExtract RLMQuoteProposalExtractV2 --org dev-scratch
python scripts/ai/docgen/docgen_odt_create.py spec.json --org dev-scratch
python scripts/ai/docgen/docgen_odt_execute.py RLMQuoteProposalExtract --record-id 0Q0XXXXXXXXXXXXAAA --org dev-scratch
python scripts/ai/docgen/docgen_odt_inspect_hierarchy.py RLMQuoteProposalExtract --org dev-scratch
```

## Deep References

- `document-generation/extract-engine-reference.md`
- `document-generation/data-mapper-authoring.md`
- `document-generation/dynamic-images.md`
