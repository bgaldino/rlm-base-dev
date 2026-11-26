# Architecture and Token Reference

Read when mapping a template token to its Transform output, or tracing a generation stage by stage. Parent: [document-generation](SKILL.md).

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
- Stage 2: `python scripts/docgen/docgen_odt_execute.py RLMQuoteProposalExtract --record-id 0Q0XXXXXXXXXXXXAAA --org dev-scratch`
- Stage 3: `sf api request rest --method POST --body @extract_output.json /services/data/v68.0/omnistudio/dataraptor/RLMQuoteProposalTransform --target-org dev-scratch`
- Full pipeline: `python scripts/docgen/docgen_template_generate.py --record-id 0Q0XXXXXXXXXXXXAAA --template-id 2dtXXXXXXXXXXXXAAA --org dev-scratch`

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
