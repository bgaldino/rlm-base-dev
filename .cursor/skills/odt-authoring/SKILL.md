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

## DO NOT

- **DO NOT** use dot notation (`Parent.Child.Field`) in `InputFieldName` or
  `OutputFieldName` — it breaks SOQL generation. Use colon paths.
- **DO NOT** mix Object-Query and Field-Mapping item types in a single
  `InputObjectQuerySequence` value — queries define hierarchy; mappings define fields.
- **DO NOT** skip `OutputObjectName` on any item — the engine silently drops items
  without it rather than erroring.
- **DO NOT** create depth-uneven hierarchies (sibling branches at different depths) —
  the engine flattens them unpredictably. See the depth-uniformity rule in
  `document-generation/extract-engine-reference.md`.

## Validation Checks

After creating or editing an ODT:

1. `python scripts/ai/docgen/docgen_odt_validate.py <name> --org <alias>` — catches
   null fields, duplicate sequences, dot-notation misuse
2. `python scripts/ai/docgen/docgen_odt_inspect_hierarchy.py <name> --org <alias>` —
   visualizes hierarchy tree, validates depth uniformity
3. `python scripts/ai/docgen/docgen_odt_execute.py <name> --record-id <id> --org <alias>` —
   runs Extract against live data; confirms output shape

## Canonical ODT Scripts

```bash
python scripts/ai/docgen/docgen_odt_validate.py RLMQuoteProposalExtract --org dev-scratch
python scripts/ai/docgen/docgen_odt_compare.py RLMQuoteProposalExtract RLMQuoteProposalExtractV2 --org dev-scratch
python scripts/ai/docgen/docgen_odt_create.py spec.json --org dev-scratch
python scripts/ai/docgen/docgen_odt_execute.py RLMQuoteProposalExtract --record-id 0Q0XXXXXXXXXXXXAAA --org dev-scratch
python scripts/ai/docgen/docgen_odt_inspect_hierarchy.py RLMQuoteProposalExtract --org dev-scratch
```

## Deep References

- `document-generation/extract-engine-reference.md` — formula catalog, filter
  mechanics, hierarchy semantics, depth-uniformity rule, redundant join pattern
- `document-generation/data-mapper-authoring.md` — programmatic ODT creation via
  REST API, cloning patterns, shell escaping pitfalls
- `document-generation/dynamic-images.md` — dynamic image rendering contract

## Examples

### Minimal Extract ODT (2 objects, 1 field mapping each)

```json
{
  "name": "MyExtract",
  "type": "Extract",
  "items": [
    {
      "type": "object_query",
      "inputObjectName": "Quote",
      "inputObjectQuerySequence": 1,
      "outputFieldName": "Quote",
      "outputObjectName": "Quote",
      "inputFieldName": "Id",
      "filterGroup": "Id = ':recordId'"
    },
    {
      "type": "field_mapping",
      "inputFieldName": "Quote:Name",
      "outputFieldName": "QuoteName",
      "outputObjectName": "Quote"
    }
  ]
}
```
