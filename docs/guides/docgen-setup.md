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

The repository also ships a fourth template, `RLM_Sales_Proposal_Document` (OmniDataTransform pair `RLMQuoteProposalExtract` / `RLMQuoteProposalTransform`, usage type `Revenue_Lifecycle_Management`; `unpackaged/post_docgen/documentTemplates/RLM_Sales_Proposal_Document_1.dt-meta.xml`). It has no seller tokens and is not described further here.

Both Quote templates above use the same Quick Action (`Quote.RLM_Create_Proposal`) and flow (`RLM_Quote_Doc_Gen_wAttachments`). The user picks the desired template from the flow's template selector.

---

## Deployment Flow: `prepare_docgen`

```
1.  create_docgen_library            → Creates "Docgen Document Template Library" ContentWorkspace and
                                        gives runtime users read-only access to it (see below)
2.  enable_document_builder_toggle   → Enables Document Builder in Revenue Settings (Robot task)
3.  deploy_docgen_seller_fields      → Pre-deploys Quote formula fields (RLM_Seller_*__c,
                                        RLM_Account_Name__c, RLM_Sales_Rep_Name__c) before ODTs
4.  deploy_docgen_qli_fields         → Pre-deploys QuoteLineItem.RLM_ProductName__c before ODTs
5.  deploy_docgen_odt_seed           → Seeds minimal ODT stubs to work around fresh-org INSERT bug
6.  deploy_post_docgen               → Deploys all metadata under unpackaged/post_docgen/
7.  activate_docgen_templates        → Activates the latest version of each RLM_ template (Apex)
8.  fix_document_template_binaries   → Uploads correct DOCX binary to each template (see below)
9.  apply_context_docgen             → Creates RLM_QuoteDocGenContext via Context Service API
10. assign_permission_sets           → Grants read access to formula fields (RLM_DocGen permset)
```

All steps are gated by `project_config.project__custom__docgen`.

**Steps 3–5** exist to work around two Salesforce platform bugs on fresh orgs: the ODT deploy validates that formula fields referenced in `inputFieldName` exist at INSERT time (steps 3–4 pre-deploy them), and the platform rejects ODT INSERT when those fields are present (`-692085439`), requiring stub records to exist so the full deploy runs as UPDATE (step 5). All three steps are idempotent.

---

## Template Library Access

Document generation reads the template's file, a ContentVersion in the `DocgenDocumentTemplateLibrary` library, **as the user who generates**. Library files are visible only to library members, and the build admin who creates the library is its only member. Without more, every other user's generation fails, for every template in the library: the Create Proposal flow shows "The document generation process ended with status Failure." and the user's `DocumentGenerationProcess.ResponseText` reads:

```
Could not generate document: Could not Enqueue to Kafka for Generate And Convert. The contentVersion with ID : {0} is either deleted/non-existent or the user does not have access to it.
```

Salesforce Help ("Create a Document Template Library", `docs/salesforce/264/help/articles/ind.sf_contracts_create_and_add_users_to_document_template_library.htm.md`) says to add the users as library members, or grant access to a group and add the users to the group. `create_docgen_library` (`scripts/apex/createDocgenTemplateLibrary.apex`) does the group form, each part find-or-create:

| Record | Value |
|---|---|
| Library | `DocgenDocumentTemplateLibrary` (ContentWorkspace) |
| Library permission | `RLM DocGen Template Viewer` (ContentWorkspacePermission, every permission flag off) |
| Public group | `RLM_DocGen_Template_Users`, seeded with **All Internal Users** while it has no members |
| Library member | the group, with that permission |

Why this shape:

- **A library takes only users and public groups as members.** Adding All Internal Users directly is refused ("You can only add individual users or public groups as library members"), so the public group carries it.
- **All internal users, through `RLM DocGen Template Viewer`: a library permission with every permission flag off.** Everyone who generates a document must read its template, and templates hold no record data. What a member can do was measured on 264 (todo 435, 2026-11-26): the sales rep persona read every template file in the library and generated quote documents as itself, and its attempt to add a new version of a library file was refused (`INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY`). The membership grants nothing beyond the library: generating also needs create access on `DocumentGenerationProcess` and access to the record.
- **One membership covers the templates in the library.** On a fresh 264 build (`DocumentTemplateContentDoc`, measured 2026-11-26), 12 of the 13 DocumentTemplates have their file in this library: the four `RLM_` templates from `unpackaged/post_docgen/documentTemplates/`, the billing templates (`DefaultInvoiceTemplate`, `DefaultInvoicePreviewTemplate`, `DefaultAccStmtTemplate` and their `sample*` sources) and the collections notices (`FinalDebtRecoveryNoticeAndLegalWarning`, `OverdueAccountCollectionNotice`). The rep read all of them. New versions of a template file need nothing more: the rep read the second version that `fix_document_template_binaries` uploads. Salesforce Help says the library stores the document templates you create, so templates made later in the designer should land there too `[inferred: not measured]`.
- **The exception is `Order_Form`.** The platform creates it, inactive, when the org is created, before this library exists, and its file has no library (the rep cannot read it). To offer it to users, move its file into the library first.

Measured on 264 scratch orgs (2026-11-26): a run where nothing existed yet created the library, the permission, the group, the group's All Internal Users member and the library membership in one transaction, with no mixed-DML error, and a rerun changed nothing (each step logs "already exists" or "left as is"). On an org where the library already existed (created by the build admin), the same run created the other four.

To narrow access, replace the group's members (for example with specific users or roles). A rerun leaves a group that has members, and an existing library membership, as they are. A rerun also **restores access an admin took away** in either of the other two ways: running `create_docgen_library` again (alone, or through `prepare_docgen` or `prepare_rlm_org`) re-seeds All Internal Users into an empty group and re-adds the group's library membership if it was removed. So to revoke access durably, replace the group's members rather than emptying the group or removing it from the library, or do not rerun the step on that org. On an org built before this fix, run `cci task run create_docgen_library --org <alias>` once.

Partner (community) users are not internal users, so the seed does not cover them. Add them to the group if they generate documents.

---

## Templates

### `RLM_QuoteProposal` — OmniDataTransform

- **Token mapping:** OmniDataTransform pair (`RLMQuoteExtractBasic` / `RLMQuoteTransformBasic`)
- **Meta file:** `unpackaged/post_docgen/documentTemplates/RLM_QuoteProposal_1.dt-meta.xml`
- **Binary:** `unpackaged/post_docgen/documentTemplates/RLM_QuoteProposal_1.dt`
- **Token list:** `AccountName`, `BillingStreet`, `BillingCity`, `BillingState`, `BillingPostalCode`, `SalesRep`, `QuoteNumber`, `CreatedDate`, `ExpirationDate`, `Line:ProductName`, `Line:Quantity`, `Line:ListPrice`, `Line:Discount`, `Line:NetUnitPrice`, `Line:NetTotalPrice` (including nested `CQL` and `CQL2` repeating sections), `GrandTotal`, `SellerCompanyName`, `SellerStreet`, `SellerCity`, `SellerState`, `SellerPostalCode`, `SellerPhone`, `SellerFax`, `SellerEmail`, `SellerWebsite`, `SellerCountry`

### `RLM_QuoteProposal_CS` — Context Service

- **Token mapping:** `RLM_QuoteDocGenContext` / `QuoteDocGenMapping` (Context Service)
- **Meta file:** `unpackaged/post_docgen/documentTemplates/RLM_QuoteProposal_CS_1.dt-meta.xml`
- **Binary:** `unpackaged/post_docgen/documentTemplates/RLM_QuoteProposal_CS_1.dt`
- **Token list:** the same rendered Quote/Line attributes as the OmniDataTransform version, populated via Context Service instead of DataRaptor. `SellerCompanyName` is mapped for parity but is not consumed by the current branded binary.

### `RLM_InvoiceTemplate` — Billing

- **Token mapping:** `BillingDocumentGenerationGetInvoiceDetails` (billing-managed OmniDataTransform)
- **Meta file:** `unpackaged/post_docgen/documentTemplates/RLM_InvoiceTemplate_1.dt-meta.xml`
- **Usage type:** `Invoice`

---

## Dynamic Seller Info

Both Quote Proposal templates (`RLM_QuoteProposal` and `RLM_QuoteProposal_CS`) include a document header with seller contact details. These values are now populated dynamically from the Quote Owner's associated Account record rather than being hardcoded.

### Token Source

| Token | Source | Formula Field |
|---|---|---|
| `AccountName` | `Quote.QuoteAccount.Name` | `RLM_Account_Name__c` |
| `SalesRep` | `Quote.Owner.FirstName + LastName` | `RLM_Sales_Rep_Name__c` |
| `SellerCompanyName` | `Quote.Owner.Account.Name` | `RLM_Seller_CompanyName__c` |
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

The `RLM_DocGen` permission set (deployed in step 10 of `prepare_docgen`) grants `readable: true` on all 13 formula fields.

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

> **Scratch org note:** Fresh scratch orgs have a blank `Organization` record (Name = org alias, all address/phone/fax fields null), so the `$Organization` fallback produces blank seller tokens on new scratch builds. If you need non-blank seller fields when generating documents as an internal (non-portal) user, populate the org's Company Information first — via **Setup → Company Information**, or anonymous Apex that updates the `Organization` record's Name/Phone/Fax/Street/City/State/PostalCode/Country.

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

**Deployed by:** `apply_context_docgen` (step 9 of `prepare_docgen`)
**Plan file:** `datasets/context_plans/DocGen/manifest.json`
**Task class:** `tasks.rlm_context_service.ManageContextDefinition`

#### Node Structure

```
RLM_QuoteDocGenContext
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
    ├── ParentReference (auto-created relationship attribute)
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
| Quote | AccountName | Quote | RLM_Account_Name__c |
| Quote | SalesRep | Quote | RLM_Sales_Rep_Name__c |
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
| Line | ParentReference | QuoteLineItem | QuoteId |
| Line | Quantity | QuoteLineItem | Quantity |
| Line | ListPrice | QuoteLineItem | ListPrice |
| Line | Discount | QuoteLineItem | Discount |
| Line | NetUnitPrice | QuoteLineItem | UnitPrice |
| Line | NetTotalPrice | QuoteLineItem | TotalPrice |

`AccountName` and `SalesRep` use formula fields (`RLM_Account_Name__c` = `QuoteAccount.Name`, `RLM_Sales_Rep_Name__c` = `Owner:User.FirstName + LastName`) rather than relationship traversal. The Context Service connect API does not support relationship traversal in `sObjectField`, so formula fields are the correct approach for cross-object lookups in this context.

`ParentReference` is automatically added when `Line` is created under `Quote`. It must map to `QuoteLineItem.QuoteId`; without this parent lookup, Context Service cannot associate hydrated line records with their quote and the `{{#Line}}` section cannot repeat reliably.

#### Generation Request Contract

For a Context Service `DocumentGenerationProcess`, set `DocGenAdditionalInputType` to `ContextService` and set `DocGenAdditionalInput` to the root Quote ID as a plain string. Do **not** pass the Context Service runtime `{"inputData": ...}` payload in this field. That runtime shape belongs to the Context API, while DocGen resolves the definition and mapping from the selected template.

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
5. **Status polling** — `rlmDocStatusMonitor` LWC subscribes to the `DocGenProcStsChgEvent` platform event and also re-reads the process status: once as soon as the subscription is live, then every 2 seconds. The flow moves on at the first status other than `InProgress`. The event alone is not enough: a process can finish before the subscription is live (the subscription receives only later events), and the record read happens once unless refreshed. On 264 a quote proposal finished 4 seconds after the process was created and the screen kept spinning after Success (todo 435). A failed status read is logged to the browser console and the component keeps polling. The component's lifecycle is two methods: `start()` tears down whatever ran before and, once the component is on the page and has a process Id, subscribes and starts polling; `teardown()` clears the poll interval and the navigation timer and releases the subscription, including one that is still being set up. A component put back on the page after it already moved the flow on (or while it was about to) starts again: it shows the waiting state, re-reads the status and moves the flow on when the status is final, so the screen is never left empty. After 5 minutes still `InProgress`, the component reports `TimedOut` and the flow shows its error screen with a TimedOut message (see below): the process may still finish, and the platform attaches its output to the quote, so the screen sends the user to the quote's Files instead of saying generation failed. Measured on 264 (2026-11-26) with requests created through the API as the sales rep persona, no flow running: a `GenerateAndConvert` request left its .docx and .pdf linked to the quote, and a `MergePDF` request (the attachment merge) left the merged PDF linked to the quote. Neither was a request that finished after a screen had timed out; the platform does not know whether a screen is waiting, so the same is expected then `[inferred]`. With the fix deployed, the sales rep persona's Create Proposal reached the preview in seconds (`RLM_QuoteProposal_CS`, 264, 2026-11-26).
6. **PDF extraction** — calls `RLM_ReturnPDFDocument` to get ContentDocumentId/ContentVersionId from the completed DGP
7. **Merge** — calls `RLM_DocumentGenerationMerge` to merge generated PDF with attachments
8. **Preview** — `mulesoft_idp:configEditorPreviewPlayer` renders inline; `rlmDocPreview` LWC (invisible companion, `display:none`) injects a global `<style>` tag into `document.head` targeting `community_content-file-previewer .bodyContainer` to force `height: 100%` (see [Preview Height Fix](#preview-height-fix))

### Errors in the flow

The three docgen Apex invocables run as the signed-in user (`with sharing`, `WITH USER_MODE`, `insert as user`), so a missing permission or an unreadable file surfaces as an exception. Every exception they throw carries a fixed sentence with no class names, request indexes or field API names. That includes a query or insert the platform refuses (a missing permission, a validation rule): the platform's own message goes to the debug log only. `RLM_ReturnPDFDocument` throws `IllegalArgumentException` when the request list is empty or holds a null request, and `PdfNotFoundException` when `ResponseText` is blank or holds no valid id, and when it holds ids but none is a PDF the user can read.

These elements have a fault connector to the `Document_Generation_Error` screen: the three Apex actions (`Create_PDF_File`, `Get_the_PDF_Document_Id`, `Merge_PDF_Documents`), the one ContentVersion lookup (`Get_Multi_Doc_Content_Id`) and the two DocumentGenerationProcess lookups (`Get_New_PDF_Content_Version_ID`, `Get_New_Merge_PDF_Content_Version_ID`). `Delete_Proposal_Doc` is housekeeping after the merged document exists, so its fault goes on to `View_Multi_Documents` instead. The `Get_Product_Attachments` subflow, the template choice set and the screens have no fault route. The two status checks (`Status_Check_Single` and `Merge_Doc_Status`) route their "Not Successful" outcome to the error screen too. The screen shows fixed sentences from three formulas. `forT_ErrorDetail` says "The document generation process ended with status <status>." after a status check, or "A step in the document generation could not be completed." after a fault. A `TimedOut` status (the status screen stopped waiting after 5 minutes) is not a failure, so it gets its own heading (`forT_ErrorHeading`: "The document is taking longer than expected."), detail and advice (`forT_ErrorAdvice`). The two waiting screens report into separate variables (`docStatus` for generation, `docMergeStatus` for the attachment merge), so the wording follows the step that timed out:

| Timed out while | Detail | Advice | What the user finds on the quote |
|---|---|---|---|
| Generating the document, no attachments chosen | "The document generation process was still running after 5 minutes…" | Check the Files list on the quote in a few minutes before generating again. | The proposal .docx and .pdf once generation finishes. |
| Generating the document, attachments chosen | Same | Same, plus "The files you chose to attach were not added to it." | The proposal .docx and .pdf; the merge never started. |
| Merging the attachments | "Merging the attachments into the PDF was still running after 5 minutes…" | The merged PDF can still finish; the quote also keeps the separate proposal PDF. | The proposal .docx and .pdf and, once it finishes, the merged PDF. The flow deletes the proposal PDF (`Delete_Proposal_Doc`) only after it sees the merge succeed, so after a timeout the user deletes it by hand if it is not wanted. |

Every other outcome keeps "The document could not be generated.", the status it ended with, and the advice to check template and PDF access. It never shows `$Flow.FaultMessage`, which can name objects, fields and Apex classes; run the flow in debug to see it.

### Preview Height Fix

`mulesoft_idp:configEditorPreviewPlayer` uses `height: 100%` internally but collapses to ~150px because its host element has no explicit height set by the flow screen container.

**Why `querySelector` / `renderedCallback` does not work:** Lightning Web Security (LWS) blocks `shadowRoot` access across namespaces from LWC JavaScript. Attempting to reach into `mulesoft_idp-config-editor-preview-player` from another component's JS is silently denied.

**The fix — global CSS injection:** `rlmDocPreview` is an invisible companion LWC (`display: none`) placed on each preview screen in the flow. Its `connectedCallback` injects a `<style>` tag into `document.head` targeting `community_content-file-previewer .bodyContainer`:

```javascript
connectedCallback() {
    _instanceCount += 1;
    if (!document.getElementById(STYLE_ID)) {
        const style = document.createElement('style');
        style.id = STYLE_ID;
        style.textContent =
            `community_content-file-previewer .bodyContainer { height: ${PREVIEW_HEIGHT} !important; }`;   // PREVIEW_HEIGHT = '100%'
        document.head.appendChild(style);
    }
}
```

This works because `community_content-file-previewer` (the inner renderer used by the preview player) uses **LWC synthetic shadow**, not native shadow DOM. Global CSS rules applied to `document.head` penetrate synthetic shadow boundaries, so `.bodyContainer` inside that component receives the height override. The `STYLE_ID` guard ensures the tag is injected only once even when several instances are mounted. A module-level instance count removes the tag when the last instance disconnects, so it does not affect file previewers on other pages.

---

## Quick Reference

```bash
# Full docgen setup
cci flow run prepare_docgen --org beta

# Individual steps
cci task run create_docgen_library --org beta      # library + read access for runtime users
cci task run deploy_post_docgen --org beta
cci task run activate_docgen_templates --org beta
cci task run fix_document_template_binaries --org beta
cci task run apply_context_docgen --org beta

# Validate context definition only
cci task run manage_context_definition \
  -o plan_file datasets/context_plans/DocGen/manifest.json \
  -o validate_only true \
  --org beta

# Inspect a DGP payload without creating it
python scripts/docgen/docgen_template_generate.py \
  --record-id 0Q0XXXXXXXXXXXXAAA --template-id 2dtXXXXXXXXXXXXAAA \
  --org rlm-base__beta --dry-run
```

---

## Known Limitations

| Issue | Detail |
|---|---|
| Template files are read as the generating user | A user who is not a library member, directly (as the admin who created the library is) or through a group such as `RLM_DocGen_Template_Users`, cannot read the template files, and their generation fails (see [Template Library Access](#template-library-access)). |
| Template binary bug | Salesforce Metadata API batch deploy assigns the same ContentDocument binary to all templates. `fix_document_template_binaries` corrects this automatically. |
| Template versions accumulate | Each deploy creates a new DocumentTemplate version. `activateDocgenTemplates.apex` activates the highest version. Old versions remain as Archived but do not cause issues. |
| `enable_document_builder_toggle` | Uses Robot Framework; requires Robot deps. May fail if the Revenue Settings page is slow. Run `validate_setup` to check Robot deps. |
| Template logo is static | Logo image bytes are embedded inside the DOCX binary and cannot be updated via metadata deploy. A `PatchDocumentTemplateLogos` CCI task is planned to automate this (see `tasks/rlm_docgen.py`). |
| `SellerWebsite` blank for internal users | `$Organization.Website` is not a valid formula merge field. `RLM_Seller_Website__c` returns blank when the Quote Owner's Account has no Website set and there is no org-level fallback available. |
