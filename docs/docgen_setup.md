# Document Generation Setup

This document covers the automated setup of Salesforce Revenue Cloud Document Generation (DocGen) in RLM environments, including both OmniDataTransform and Context Service template approaches, deployment quirks, and the post-deploy binary fix.

---

## Overview

Document Generation allows Quote and Invoice PDFs to be generated from Word `.docx` templates. The system supports two token-mapping approaches:

| Approach | Task Class | Template | Token Population |
|---|---|---|---|
| OmniDataTransform | `RLMQuoteExtractBasic` + `RLMQuoteTransformBasic` | `RLM_QuoteProposal` | OmniStudio DataRaptor extract + transform |
| Context Service | `RLM_QuoteDocGenContext` | `RLM_QuoteProposal_CS` | Context Service connect API |
| Invoice (Server-Side) | `BillingDocumentGenerationGetInvoiceDetails` | `RLM_InvoiceTemplate` | OmniDataTransform (billing-managed) |

Both Quote templates use the same Quick Action (`Quote.RLM_Create_Proposal`) and flow (`RLM_Quote_Doc_Gen_wAttachments`). The user picks the desired template from the flow's template selector.

---

## Deployment Flow: `prepare_docgen`

```
1. create_docgen_library            → Creates "Docgen Document Template Library" ContentWorkspace
2. enable_document_builder_toggle   → Enables Document Builder in Revenue Settings (Robot task)
3. deploy_post_docgen               → Deploys all metadata under unpackaged/post_docgen/
4. activate_docgen_templates        → Activates the latest version of each RLM_ template (Apex)
5. fix_document_template_binaries   → Uploads correct DOCX binary to each template (see below)
6. apply_context_docgen             → Creates RLM_QuoteDocGenContext via Context Service API
7. assign_permission_sets           → Grants read access to RLM_Seller_*__c formula fields (RLM_DocGen permset)
```

All steps are gated by `project_config.project__custom__docgen`.

---

## Templates

### `RLM_QuoteProposal` — OmniDataTransform

- **Token mapping:** OmniDataTransform pair (`RLMQuoteExtractBasic` / `RLMQuoteTransformBasic`)
- **Meta file:** `unpackaged/post_docgen/documentTemplates/RLM_QuoteProposal_1.dt-meta.xml`
- **Binary:** `unpackaged/post_docgen/documentTemplates/RLM_QuoteProposal_1.dt`
- **Token list:** `AccountName`, `BillingStreet`, `BillingCity`, `BillingState`, `BillingPostalCode`, `SalesRep`, `QuoteNumber`, `CreatedDate`, `ExpirationDate`, `Line:ProductName`, `Line:Quantity`, `Line:ListPrice`, `Line:Discount`, `Line:NetUnitPrice`, `Line:NetTotalPrice` (including nested `CQL` and `CQL2` repeating sections), `GrandTotal`, `SellerCompanyName`, `SellerStreet`, `SellerCity`, `SellerState`, `SellerPostalCode`, `SellerPhone`, `SellerFax`, `SellerEmail`, `SellerWebsite`, `SellerCountry`

### `RLM_QuoteProposal_CS` — Context Service ⚠️ Work in Progress

> **Status:** End-to-end document generation with this template has not been fully verified in an automated build. `AccountName` and `SalesRep` require manual mapping in Setup → Context Service after deploy (see [Manual Step Required After Deploy](#manual-step-required-after-deploy)). Do not rely on this template in production builds until those steps are automated or documented as a known post-deploy requirement.

- **Token mapping:** `RLM_QuoteDocGenContext` / `QuoteDocGenMapping` (Context Service)
- **Meta file:** `unpackaged/post_docgen/documentTemplates/RLM_QuoteProposal_CS_1.dt-meta.xml`
- **Binary:** `unpackaged/post_docgen/documentTemplates/RLM_QuoteProposal_CS_1.dt`
- **Token list:** same Quote/Line attributes as the OmniDataTransform version, populated via Context Service instead of DataRaptor

### `RLM_InvoiceTemplate` — Billing

- **Token mapping:** `BillingDocumentGenerationGetInvoiceDetails` (billing-managed OmniDataTransform)
- **Meta file:** `unpackaged/post_docgen/documentTemplates/RLM_InvoiceTemplate_1.dt-meta.xml`
- **Usage type:** `Invoice`

---

## Dynamic Seller Info

Both Quote Proposal templates (`RLM_QuoteProposal` and `RLM_QuoteProposal_CS`) include a document header with seller contact details. These values are now populated dynamically from the Quote Owner's associated Account record rather than being hardcoded.

### Token Source

| Token | Source |
|---|---|
| `SellerCompanyName` | `Quote.Owner.Account.Name` |
| `SellerStreet` | `Quote.Owner.Account.BillingStreet` |
| `SellerCity` | `Quote.Owner.Account.BillingCity` |
| `SellerState` | `Quote.Owner.Account.BillingState` |
| `SellerPostalCode` | `Quote.Owner.Account.BillingPostalCode` |
| `SellerPhone` | `Quote.Owner.Account.Phone` |
| `SellerFax` | `Quote.Owner.Account.Fax` |
| `SellerEmail` | `Quote.Owner.Email` (User record) |
| `SellerWebsite` | `Quote.Owner.Account.Website` |
| `SellerCountry` | `Quote.Owner.Account.BillingCountry` |

### Implementation

**ODT template (`RLM_QuoteProposal`):** The `RLMQuoteExtractBasic` ODT reads the 10 `RLM_Seller_*__c` formula fields directly from the Quote object (`Quote:RLM_Seller_*__c`). No new query sequences are required because formula fields are resolved at the platform level before the DataRaptor reads them. `RLMQuoteTransformBasic` passes the values through unchanged.

**CS template (`RLM_QuoteProposal_CS`):** The Context Service API does not support relationship traversal in `sObjectField`. Ten formula fields (`RLM_Seller_CompanyName__c` through `RLM_Seller_Country__c`) are deployed on the Quote object under `unpackaged/post_docgen/objects/Quote/fields/`. The `QuoteDocGenMapping` references these as direct `sObjectField` values, so no traversal is needed in the context plan.

The `RLM_DocGen` permission set (deployed in step 7 of `prepare_docgen`) grants `readable: true` on all 10 fields.

### Address Format

The document header renders seller address as three lines:

```
{{SellerStreet}}
{{SellerCity}}, {{SellerState}}
{{SellerPostalCode}}, {{SellerCountry}}
```

### Partner vs. Internal Context

For users operating in a Partner Community context, `Owner.AccountId` resolves to their company's Account — seller fields populate from the partner Account.

For internal (non-portal) users, `Owner.AccountId` is null. The Account-based formula fields fall back to `$Organization.*` (the org's Company Information from Setup → Company Information), so generated documents always show valid seller data. Only `SellerWebsite` has no `$Organization` fallback (`$Organization.Website` is not a valid formula merge field) — it renders blank for internal users whose Account has no Website set. `SellerCountry` uses `$Organization.Country` as its fallback and is always populated.

The priority is: **Partner Account** → **`$Organization`** (Account fields) / **`Owner:User.Email`** (email, always populated).

> **Scratch org note:** Fresh scratch orgs have a blank `Organization` record (Name = org alias, all address/phone/fax fields null), so the `$Organization` fallback produces blank seller tokens on new scratch builds. A `set_org_company_info` task is planned (see `scripts/apex/setOrgCompanyInfo.apex` TODO and the `# TODO` comment before `insert_scratch_data` in `cumulusci.yml`) to populate these fields as step 2 of `prepare_scratch`.

### Logo

Template logos cannot be updated dynamically post-deploy because logo image bytes are embedded inside the DOCX ZIP binary. A `PatchDocumentTemplateLogos` CCI task is planned (see `tasks/rlm_docgen.py` TODO) to fetch the org's active BrandingSet logo and patch the template binaries automatically during `prepare_docgen`.

---

## Metadata API Batch-Deploy Bug and Fix

### The Bug

When multiple `DocumentTemplate` records are deployed in a single Metadata API request, **all templates receive the same ContentDocument binary** — the first one processed (alphabetically: `RLM_InvoiceTemplate`). As a result:

- `RLM_QuoteProposal` ContentDocument contains invoice-template DOCX content
- `RLM_QuoteProposal_CS` ContentDocument also contains invoice-template DOCX content
- Generated documents render with invoice layout/tokens instead of quote layout

This is silent — the deploy succeeds, templates activate, but the generated DOCX is wrong.

### The Fix: `fix_document_template_binaries`

**Task:** `fix_document_template_binaries`
**Class:** `tasks.rlm_docgen.FixDocumentTemplateBinaries`

After `activate_docgen_templates`, this task:

1. Finds the `DocgenDocumentTemplateLibrary` ContentWorkspace
2. For each `.dt` file in `unpackaged/post_docgen/documentTemplates/` (excluding macOS temp files starting with `~`):
   - Reads the template `<name>` from the corresponding `.dt-meta.xml`
   - Queries the most recently created ContentDocument in the library with that title
   - Creates a new `ContentVersion` for that ContentDocument, uploading the `.dt` binary directly

The `.dt` file format is a standard DOCX ZIP with embedded fonts. Uploading it as a ContentVersion replaces the wrong binary with the correct one for each template.

### Idempotency

Running `deploy_post_docgen` → `activate_docgen_templates` → `fix_document_template_binaries` multiple times is safe:
- Each deploy creates a new DocumentTemplate version (v1, v2, … vN)
- `activate_docgen_templates` activates the highest version per template name
- `fix_document_template_binaries` corrects the ContentDocument binary for each newly deployed version

### Why the `.dt` Binary in the Repo Matters

The `RLM_QuoteProposal_1.dt` file in the repo **must** be the correct Quote template DOCX (with embedded fonts, ~3.9MB). The repo originally contained the wrong binary (invoice content at the same size), requiring a manual fix after every deploy. The committed binary was sourced from the org's active template after a manual Document Builder correction.

---

## Context Service Template: `RLM_QuoteProposal_CS`

### Why Context Service

The Context Service approach decouples token population from OmniStudio DataRaptors. Instead of `extractOmniDataTransformName` + `mapperOmniDataTransformName`, the template uses a `ContextDefinition` (`RLM_QuoteDocGenContext`) and a `ContextMapping` (`QuoteDocGenMapping`) to supply field values at generation time.

### Context Definition: `RLM_QuoteDocGenContext`

**Deployed by:** `apply_context_docgen` (step 6 of `prepare_docgen`)
**Plan file:** `datasets/context_plans/DocGen/manifest.json`
**Task class:** `tasks.rlm_context_service.ManageContextDefinition`

#### Node Structure

```
RLM_QuoteDocGenContext (primaryObject: Quote)
├── Quote  (root node)
│   ├── AccountName       STRING   INPUTOUTPUT
│   ├── BillingStreet     STRING   INPUTOUTPUT
│   ├── BillingCity       STRING   INPUTOUTPUT
│   ├── BillingState      STRING   INPUTOUTPUT
│   ├── BillingPostalCode STRING   INPUTOUTPUT
│   ├── SalesRep          STRING   INPUTOUTPUT
│   ├── QuoteNumber       STRING   INPUTOUTPUT
│   ├── CreatedDate       DATE     INPUTOUTPUT
│   ├── ExpirationDate    DATE     INPUTOUTPUT
│   ├── GrandTotal        CURRENCY INPUTOUTPUT
│   ├── SellerCompanyName STRING   INPUTOUTPUT
│   ├── SellerStreet      STRING   INPUTOUTPUT
│   ├── SellerCity        STRING   INPUTOUTPUT
│   ├── SellerState       STRING   INPUTOUTPUT
│   ├── SellerPostalCode  STRING   INPUTOUTPUT
│   ├── SellerPhone       STRING   INPUTOUTPUT
│   ├── SellerFax         STRING   INPUTOUTPUT
│   ├── SellerEmail       STRING   INPUTOUTPUT
│   ├── SellerWebsite     STRING   INPUTOUTPUT
│   └── SellerCountry     STRING   INPUTOUTPUT
└── Line (child of Quote)
    ├── ProductName   STRING   INPUTOUTPUT
    ├── Quantity      NUMBER   INPUTOUTPUT
    ├── ListPrice     CURRENCY INPUTOUTPUT
    ├── Discount      PERCENT  INPUTOUTPUT
    ├── NetUnitPrice  CURRENCY INPUTOUTPUT
    └── NetTotalPrice CURRENCY INPUTOUTPUT
```

#### Mapping: `QuoteDocGenMapping` (default)

| Context Node | Attribute | SObject | Field |
|---|---|---|---|
| Quote | BillingStreet | Quote | BillingStreet |
| Quote | BillingCity | Quote | BillingCity |
| Quote | BillingState | Quote | BillingState |
| Quote | BillingPostalCode | Quote | BillingPostalCode |
| Quote | QuoteNumber | Quote | QuoteNumber |
| Quote | CreatedDate | Quote | CreatedDate |
| Quote | ExpirationDate | Quote | ExpirationDate |
| Quote | GrandTotal | Quote | GrandTotal |
| Quote | SellerCompanyName | Quote | RLM_Seller_CompanyName__c |
| Quote | SellerStreet | Quote | RLM_Seller_Street__c |
| Quote | SellerCity | Quote | RLM_Seller_City__c |
| Quote | SellerState | Quote | RLM_Seller_State__c |
| Quote | SellerPostalCode | Quote | RLM_Seller_PostalCode__c |
| Quote | SellerPhone | Quote | RLM_Seller_Phone__c |
| Quote | SellerFax | Quote | RLM_Seller_Fax__c |
| Quote | SellerEmail | Quote | RLM_Seller_Email__c |
| Quote | SellerWebsite | Quote | RLM_Seller_Website__c |
| Quote | SellerCountry | Quote | RLM_Seller_Country__c |
| Line | ProductName | QuoteLineItem | RLM_ProductName__c |
| Line | Quantity | QuoteLineItem | Quantity |
| Line | ListPrice | QuoteLineItem | ListPrice |
| Line | Discount | QuoteLineItem | Discount |
| Line | NetUnitPrice | QuoteLineItem | UnitPrice |
| Line | NetTotalPrice | QuoteLineItem | TotalPrice |

#### Manual Step Required After Deploy

`AccountName` and `SalesRep` require relationship traversal (`Account.Name`, `Owner.Name`) which the Context Service connect API does not support for `sObjectField`. These two attributes must be mapped manually in Setup → Context Service after `apply_context_docgen` runs.

#### Plan File Location

```
datasets/context_plans/DocGen/
  manifest.json                    → lists contexts/quote_docgen.json
  contexts/
    quote_docgen.json              → full create plan with nodes, attributes, mappings, tags
```

The plan uses `"create": true`, so `ManageContextDefinition` creates the context definition if it does not exist. On re-runs, the existing definition is updated (attributes/tags/mappings are added idempotently).

---

## Context Service Utility Changes

The `ManageContextDefinition` task (`tasks/rlm_context_service.py`) supports the DocGen use case through the following capabilities used by `apply_context_docgen`:

### New-Context Creation (`"create": true`)

When the plan declares `"create": true`, the task:
1. Creates the `ContextDefinition` via `POST /connect/context-definitions`
2. Creates nodes declared in `contextNodeDefinitions` (supports `parentNodeName` for child nodes)
3. Creates `contextMappings` (via the create payload, not update flow)
4. Re-fetches the definition to get node and mapping IDs
5. Applies attributes, mapping rules, and tags in the standard update flow
6. Activates if `"activate": true`

This differs from the update flow used by `extend_context_*` tasks, which assume the context already exists as a standard context extension.

### `contextNodeDefinitions` vs `contextNodes`

New-context plans use `contextNodeDefinitions` (an array) instead of `contextNodes` (the update form). Each entry supports `parentNodeName` to reference a previously created node:

```json
"contextNodeDefinitions": [
  { "name": "Quote",  "label": "Quote" },
  { "name": "Line",   "label": "Quote Line Item", "parentNodeName": "Quote" }
]
```

### `contextMappings` Block

In the create plan, the `contextMappings` block creates named mappings before mapping rules are applied. The `isDefault: true` mapping becomes the template's default mapping:

```json
"contextMappings": {
  "contextMappings": [
    { "name": "QuoteDocGenMapping", "description": "QuoteDocGenMapping", "isDefault": true }
  ]
}
```

This differs from `contextMappingUpdates` used in update plans.

---

## Flow: `RLM_Quote_Doc_Gen_wAttachments`

The Quote Proposal generation flow (`unpackaged/post_docgen/flows/RLM_Quote_Doc_Gen_wAttachments.flow-meta.xml`) launched by Quick Action `Quote.RLM_Create_Proposal`:

1. **Template selection** — displays active `DocumentTemplate` records filtered by `UsageType = Revenue_Lifecycle_Management`
2. **Attachment selection** — datatable of product-linked ContentDocuments (via `RLM_DocGen_Get_Product_Attachments` sub-flow)
3. **File upload** — optional manual attachment uploads
4. **Generate** — calls `RLM_DocumentGenerationCreate` Apex invocable → creates `DocumentGenerationProcess`
5. **Status polling** — `rlmDocStatusMonitor` LWC subscribes to `DocGenProcStsChgEvent` platform event; wire-based polling fallback ensures flow advances even if EMP event is dropped
6. **PDF extraction** — calls `RLM_ReturnPDFDocument` to get ContentDocumentId/ContentVersionId from the completed DGP
7. **Merge** — calls `RLM_DocumentGenerationMerge` to merge generated PDF with attachments
8. **Preview** — `mulesoft_idp:configEditorPreviewPlayer` renders inline; `rlmDocPreview` LWC (invisible companion, `display:none`) injects a global `<style>` tag into `document.head` targeting `community_content-file-previewer .bodyContainer` to force `height: 500px` (see [Preview Height Fix](#preview-height-fix))

### Preview Height Fix

`mulesoft_idp:configEditorPreviewPlayer` uses `height: 100%` internally but collapses to ~150px because its host element has no explicit height set by the flow screen container.

**Why `querySelector` / `renderedCallback` does not work:** Lightning Web Security (LWS) blocks `shadowRoot` access across namespaces from LWC JavaScript. Attempting to reach into `mulesoft_idp-config-editor-preview-player` from another component's JS is silently denied.

**The fix — global CSS injection:** `rlmDocPreview` is an invisible companion LWC (`display: none`) placed on each preview screen in the flow. Its `connectedCallback` injects a `<style>` tag into `document.head` targeting `community_content-file-previewer .bodyContainer`:

```javascript
connectedCallback() {
    if (!document.getElementById(STYLE_ID)) {
        const style = document.createElement('style');
        style.id = STYLE_ID;
        style.textContent =
            `community_content-file-previewer .bodyContainer { height: 500px !important; min-height: 500px !important; }`;
        document.head.appendChild(style);
    }
}
```

This works because `community_content-file-previewer` (the inner renderer used by the preview player) uses **LWC synthetic shadow**, not native shadow DOM. Global CSS rules applied to `document.head` penetrate synthetic shadow boundaries, so `.bodyContainer` inside that component receives the height override. The `STYLE_ID` guard ensures the tag is injected only once even when the flow navigates back and re-mounts the component.

---

## Quick Reference

```bash
# Full docgen setup
cci flow run prepare_docgen --org beta

# Individual steps
cci task run deploy_post_docgen --org beta
cci task run activate_docgen_templates --org beta
cci task run fix_document_template_binaries --org beta
cci task run apply_context_docgen --org beta

# Validate context definition only
cci task run manage_context_definition \
  -o plan_file datasets/context_plans/DocGen/manifest.json \
  -o validate_only true \
  --org beta
```

---

## Known Limitations

| Issue | Detail |
|---|---|
| `AccountName`, `SalesRep` not auto-mapped | Context Service API does not support relationship traversal (`Account.Name`, `Owner.Name`). Map manually in Setup after deploy. |
| Template binary bug | Salesforce Metadata API batch deploy assigns the same ContentDocument binary to all templates. `fix_document_template_binaries` corrects this automatically. |
| Template versions accumulate | Each deploy creates a new DocumentTemplate version. `activateDocgenTemplates.apex` activates the highest version. Old versions remain as Archived but do not cause issues. |
| `enable_document_builder_toggle` | Uses Robot Framework; requires Robot deps. May fail if the Revenue Settings page is slow. Run `validate_setup` to check Robot deps. |
| Template logo is static | Logo image bytes are embedded inside the DOCX binary and cannot be updated via metadata deploy. A `PatchDocumentTemplateLogos` CCI task is planned to automate this (see `tasks/rlm_docgen.py`). |
| `SellerWebsite` blank for internal users | `$Organization.Website` is not a valid formula merge field. `RLM_Seller_Website__c` returns blank when the Quote Owner's Account has no Website set and there is no org-level fallback available. |
