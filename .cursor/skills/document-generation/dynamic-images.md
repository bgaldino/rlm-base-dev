# Dynamic Images in Document Generation

Sub-file of `document-generation/SKILL.md`. Use when implementing dynamic
(data-driven) image rendering in OmniStudio document templates.

## Quick Summary

Dynamic images in `.docx` templates require:
1. A `{{IMG_tokenname}}` text token in the template
2. A Transform ODT that produces a **nested JSON object** (not flat strings)
3. A ContentVersion Id (068 prefix) pointing to the image file in the org
4. Server-side support requires org Release 256+ (Spring '24)

---

## Static vs Dynamic Images

| Approach | When to Use | Pros | Cons |
|----------|------------|------|------|
| **Static embed** | Fixed branding (company logo) | Simple, always works, no ODT wiring | Can't change per-record |
| **Dynamic token** | Per-account logos, product images, signatures | Data-driven, flexible | Complex wiring, version-sensitive |

For static branding, embed the image directly in the `.docx` using python-docx:
```python
run.add_picture("/path/to/logo.png", width=Inches(2.5))
```

---

## Prerequisites

- **Org release**: 256+ for server-side generation (earlier versions render
  `[object Object]` as text)
- **Image location**: Must be uploaded as a File (ContentVersion) in Salesforce.
  External URLs are NOT supported without a custom Apex class.
- **Image format**: PNG, JPG, GIF supported

---

## Transform Output Structure

The Transform must produce a nested object for each image token. **Flat
`:src`/`:height`/`:width` string mappings do not work server-side.**

### Required JSON structure

```json
{
  "IMG_CompanyLogo": {
    "ImageBlobField": "VersionData",
    "SObject": "ContentVersion",
    "Id": "068xxxxxxxxx",
    "size": "200X80",
    "centered": "false"
  }
}
```

| Field | Value | Notes |
|-------|-------|-------|
| `ImageBlobField` | `"VersionData"` | Always — tells engine which blob field to read |
| `SObject` | `"ContentVersion"` | Always — the object the engine queries |
| `Id` | ContentVersion Id | **Must be 068 prefix**, not ContentDocument (069) |
| `size` | `"WIDTHxHEIGHT"` | Pixels, e.g., `"200X80"` |
| `centered` | `"true"` / `"false"` | Horizontal alignment |

### Sizing rules

- Neither dimension set → original size (max 350px W x 400px H on A4 portrait)
- One dimension set → proportionally scaled
- Both set → exact dimensions (max 600px W x 800px H on A4 portrait)

---

## Extract Setup

### Option A: Query ContentVersion directly

```
Object Query Item:
  InputObjectName: ContentVersion
  InputFieldName: Id
  OutputFieldName: LogoVersion
  OutputObjectName: json
  InputObjectQuerySequence: 10
  FilterOperator: =
  FilterValue: "ContentDocumentId from a parent path or literal"
  FilterGroup: 0

Field Mapping Item:
  InputFieldName: LogoVersion:Id
  OutputFieldName: LogoContentVersionId
  OutputObjectName: json
  OutputCreationSequence: 1
```

### Option B: Query ContentDocument + get LatestPublishedVersionId

```
Object Query Item:
  InputObjectName: ContentDocument
  InputFieldName: Title
  OutputFieldName: Invoice:Logo
  OutputObjectName: json
  InputObjectQuerySequence: 7
  FilterOperator: =
  FilterValue: "\"Company_Logo\""
  FilterGroup: 0

Field Mapping Item:
  InputFieldName: Invoice:Logo:LatestPublishedVersionId
  OutputFieldName: LogoContentVersionId
  OutputObjectName: json
  OutputCreationSequence: 1
```

---

## Transform Setup

### Building the nested object

The Transform needs to output the nested JSON structure. Two approaches:

#### Approach 1: Multiple items with shared OutputObjectName

Create items at `OutputCreationSequence: 0` with `OutputObjectName: "IMG_CompanyLogo"`:

```
Item 1: OutputFieldName="ImageBlobField", InputFieldName=(static "VersionData")
Item 2: OutputFieldName="SObject", InputFieldName=(static "ContentVersion")
Item 3: OutputFieldName="Id", InputFieldName="LogoContentVersionId"
Item 4: OutputFieldName="size", InputFieldName=(static "200X80")
Item 5: OutputFieldName="centered", InputFieldName=(static "false")
```

#### Approach 2: Formula item

Use a formula expression to construct the object (if supported by the formula
engine in your org version):

```
OutputFieldName: Formula
OutputObjectName: Formula
FormulaResultPath: IMG_CompanyLogo
FormulaSequence: 2
OutputCreationSequence: 0
```

---

## Known Issues and Gotchas

### `[object Object]` rendered as text
- **Cause**: Org is below Release 256 (server-side), or the Transform output is
  structured incorrectly
- **Fix**: Verify org version; ensure Transform produces nested object, not flat
  string

### Image renders as empty space
- **Cause**: ContentDocument Id (069) passed instead of ContentVersion Id (068)
- **Fix**: Map `LatestPublishedVersionId` from ContentDocument, or query
  ContentVersion directly

### Image token not found
- **Cause**: Token in template doesn't match the Transform output key
- **Fix**: Template uses `{{IMG_CompanyLogo}}`, Transform must output key
  `IMG_CompanyLogo` (exact match, case-sensitive)

### Static embed as fallback
When dynamic images cause issues, embed the image directly in the `.docx`.
This is reliable for any branding element that doesn't change per-record.

---

## Custom Apex Class (`ind_docgen_api.OpenInterface`)

For advanced scenarios (URL-based images, custom resolution logic):

```apex
global class ImageResolver implements ind_docgen_api.OpenInterface {
    public Boolean invokeMethod(
        String methodName,
        Map<String, Object> inputMap,
        Map<String, Object> outMap
    ) {
        // methodName dispatched by engine
        // Return image data in outMap
        return true;
    }
}
```

This interface is poorly documented. The `getImageUrl` method exists in the
platform symbol table but its contract is not publicly specified. Prefer the
ContentVersion approach for production use.

---

## References

- Help: [Dynamic Images (Client-Side)](https://help.salesforce.com/s/articleView?id=ind.doc_gen_dynamic_images_for_client_side_document_generation.htm&type=5)
- Help: [Known Limitations](https://help.salesforce.com/s/articleView?id=ind.doc_gen_known_limitations_in_dynamic_rich_texts__hyperlinks__and_images.htm&type=5)
- Developer Guide: [OpenInterface](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/apex_interface_ind_docgen_api_OpenInterface.htm)
