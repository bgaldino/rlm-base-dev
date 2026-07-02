# Dynamic Images in Document Generation

Sub-file of `document-generation/SKILL.md`. Use when implementing dynamic
(data-driven) image rendering in OmniStudio document templates.

## Quick Summary

Dynamic images in `.docx` templates require:
1. A `{{IMG_tokenname}}` **plain text** token in the template (not an embedded image)
2. A Transform ODT that produces a **nested JSON object** with `src`, `width`, `height`
3. A ContentDocument Id (`069` prefix) in the `src` field
4. The image file must be accessible to the **Integration User** (e.g., in a
   Content Library that grants the Integration User access)
5. `DocGenApiVersionType` must be `'Advanced'` on the DocumentGenerationProcess record
6. Server-side support requires org Release 256+ (Spring '24)

---

## Verified Contract

Tested on Release 262 (API v67.0). Server-side support requires Release 256+.

### Required Transform Output Structure

```json
{
  "IMG_CompanyLogo": {
    "src": "069xxxxxxxxx",
    "width": "200",
    "height": "80"
  }
}
```

| Field | Required | Value | Notes |
|-------|----------|-------|-------|
| `src` | **Yes** | ContentDocument ID (`069` prefix) | NOT ContentVersion (`068`), NOT file Title |
| `width` | **Yes** | Pixel value as string | e.g., `"200"` |
| `height` | **Yes** | Pixel value as string | e.g., `"80"` |

**All three fields are mandatory.** Omitting `width`/`height` results in the token
being consumed (not visible as raw text) but no image rendered. Using ContentVersion
ID (`068`) or file Title as `src` crashes the engine with:
`"Cannot read properties of undefined (reading '0')"`.

### Template Placement

Place `{{IMG_tokenname}}` as **plain text** anywhere in the `.docx`:
- In paragraphs
- In table cells
- In text boxes
- In headers/footers
- Inside repeating sections (`{{#Section}}...{{IMG_x}}...{{/Section}}`)

No embedded placeholder image is needed — the engine replaces the text token with
the resolved image at that position.

### Prerequisites

| Requirement | How to Verify |
|-------------|---------------|
| Image in Salesforce Files | Upload via Files tab; PNG/JPG/GIF supported |
| Integration User has access | Add Integration User to the Content Library containing the image |
| `DocGenApiVersionType = 'Advanced'` | Set on the DocumentGenerationProcess record (our Apex class `RLM_DocumentGenerationCreate` does this) |
| Image < 4.9 MB | Check ContentVersion.ContentSize |
| Org Release 256+ | Earlier releases render `[object Object]` as text |

---

## Static vs Dynamic Images

| Approach | When to Use | Pros | Cons |
|----------|------------|------|------|
| **Static embed** | Fixed branding (company logo) | Simple, always works, no ODT wiring | Can't change per-record |
| **Dynamic IMG_ token** | Per-account logos, product images, signatures | Data-driven, flexible | Requires library access + all 3 fields |
| **RTB_ with `<img>` HTML** | Images inside rich text, complex layouts | Uses existing RTB infrastructure | Limited sizing control |

For static branding, embed the image directly in the `.docx` using python-docx:
```python
run.add_picture("/path/to/logo.png", width=Inches(2.5))
```

---

## Extract Setup

### Query ContentDocument to get the ID for `src`

```
Object Query Item:
  InputObjectName: ContentDocument
  InputFieldName: Title
  OutputFieldName: MyImage
  OutputObjectName: json
  InputObjectQuerySequence: 9
  FilterOperator: =
  FilterValue: "'Company_Logo'"
  FilterGroup: 0

Field Mapping Item:
  InputFieldName: MyImage:Id
  OutputFieldName: ImageDocId
  OutputObjectName: json
  OutputCreationSequence: 1
```

The `Id` field on ContentDocument IS the `069`-prefix ContentDocument ID —
exactly what `src` needs.

### Alternative: Query via linked record

If the image is linked to the record (e.g., via ContentDocumentLink):
```
Object Query Item:
  InputObjectName: ContentDocumentLink
  InputFieldName: ContentDocumentId
  OutputFieldName: Quote:ImageLink
  OutputObjectName: json
  InputObjectQuerySequence: 10
  FilterOperator: =
  FilterValue: Quote:Id
  FilterGroup: 0
```

---

## Transform Setup — Building the Nested Object

Use formula items for static strings (`"200"`, `"80"`) and colon-path notation
to build the nested object:

```
Formula Item 1 (width):
  OutputFieldName: Formula
  OutputObjectName: Formula
  FormulaExpression: CONCAT('200', '')
  FormulaResultPath: ImgWidth
  FormulaSequence: 10
  OutputCreationSequence: 0

Formula Item 2 (height):
  OutputFieldName: Formula
  OutputObjectName: Formula
  FormulaExpression: CONCAT('80', '')
  FormulaResultPath: ImgHeight
  FormulaSequence: 11
  OutputCreationSequence: 0

Mapping 1 (src):
  InputFieldName: ImageDocId
  OutputFieldName: IMG_CompanyLogo:src
  OutputObjectName: json
  OutputCreationSequence: 1

Mapping 2 (width):
  InputFieldName: ImgWidth
  OutputFieldName: IMG_CompanyLogo:width
  OutputObjectName: json
  OutputCreationSequence: 1

Mapping 3 (height):
  InputFieldName: ImgHeight
  OutputFieldName: IMG_CompanyLogo:height
  OutputObjectName: json
  OutputCreationSequence: 1
```

The colon in `IMG_CompanyLogo:src` builds a nested object:
`{"IMG_CompanyLogo": {"src": "069...", "width": "200", "height": "80"}}`.

**IMPORTANT:** `OutputObjectName` must always be `"json"` for these items —
custom values (e.g., `"IMG_CompanyLogo"`) break the entire ODT.

---

## Sizing Rules

- Both `width` and `height` are required for the image to render
- Values are strings (not integers): `"200"` not `200`
- No proportional scaling — both dimensions must be specified
- Maximum dimensions not formally documented; original image aspect ratio
  is not automatically preserved (stretching/squashing can occur)

---

## Known Issues and Gotchas

### Image not rendered (empty space, no error)

- **Cause 1**: Missing `width` or `height` — both are required
- **Cause 2**: Integration User cannot access the file — add user to Content Library
- **Cause 3**: File not in Salesforce Files (e.g., in Static Resources)
- **Fix**: Ensure all 3 fields present + Integration User has library access

### Engine crash: `Cannot read properties of undefined (reading '0')`

- **Cause**: `src` contains a ContentVersion ID (`068`) or file Title instead of
  ContentDocument ID (`069`)
- **Fix**: Always use the ContentDocument ID. Query `ContentDocument.Id` directly,
  or if you have a ContentVersion, traverse `ContentVersion.ContentDocumentId`.

### `[object Object]` rendered as text

- **Cause**: Org is below Release 256 (DocGen 2.0 not available)
- **Fix**: Upgrade org; or use RTB_ with HTML `<img>` as fallback

### Image token shows as raw text `{{IMG_xxx}}`

- **Cause**: Transform output key doesn't match template token (case-sensitive)
- **Fix**: Template uses `{{IMG_CompanyLogo}}`, Transform must output key
  `IMG_CompanyLogo` (exact match)

### HYP_ hyperlink error on same page

If `{{HYP_xxx}}` tokens produce a red "URL is invalid" error, this does NOT
affect IMG_ rendering. HYP_ tokens have a separate issue with URL resolution;
use RTB_ with `<a>` tags for hyperlinks instead (confirmed working).

---

## RTB_ Alternative for Images

Per official Salesforce docs: *"If you must use rich text with images, use the
RTB_token instead of the IMG_token."*

For simpler cases or when IMG_ prerequisites can't be met, embed an image via
HTML in a rich text field and use `{{RTB_xxx}}`:

```html
<img src="data:image/png;base64,..." width="200" height="80" />
```

Or reference a URL-accessible image (note: external URLs may not work in all
contexts for server-side generation).

---

## References

- Help: [Tokens in Microsoft Word or Microsoft PowerPoint Documents](https://help.salesforce.com/s/articleView?id=ind.nCino_Tokens_Word_ppt.htm&type=5)
- Help: [Dynamic Images in Server-Side Document Generation 2.0](https://help.salesforce.com/s/articleView?id=ind.sf_docgen_dynamic_images_server_side.htm&type=5)
- Help: [Known Limitations](https://help.salesforce.com/s/articleView?id=ind.doc_gen_known_limitations_in_dynamic_rich_texts__hyperlinks__and_images.htm&type=5)
- Help: [Generate Invoice PDFs with Your Company Logo](https://help.salesforce.com/s/articleView?id=ind.billing_document_generation_logo.htm&type=5)
- Developer Guide: [OpenInterface](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/apex_interface_ind_docgen_api_OpenInterface.htm)
