# Save the generated proposal PDF as a "Quote PDF" (QuoteDocument)

**Status:** Design / not yet implemented
**Target org for verification:** `rlm-base__july15_margin` (CCI alias `july15_margin`)
**Release:** 262 (API v67.0)

## Goal

Update the server-side document-generation work so the generated proposal PDF is attached as
a **"Quote PDF"** record (the standard `QuoteDocument` object — the "Quote PDFs" related list
on a Quote) **instead of** landing only in the general Files / Notes & Attachments list.

Keep the existing **server-side** generation path (the `DocumentGenerationProcess` pipeline).
This is not about the client-side spike in `unpackaged/spike_docgen_client/`.

---

## Background: what "Quote PDF" actually is (data model)

The UI "**Quote PDFs**" related list on a Quote is the standard **`QuoteDocument`** object:

| Property | Value |
|----------|-------|
| Key prefix | `0QD` |
| Label | "Quote PDF" |
| Module | `quotes-api` (`javaPackageRoot = sales.quote.document`) |
| Access delegate | `cudAccessDelegate = "Quote"` (Quote CRUD gates QuoteDocument CRUD) |
| License | Revenue Cloud Advanced / Document Builder |

Createable fields that matter:

| Field | Type | Notes |
|-------|------|-------|
| `QuoteId` | reference → Quote | **Required**, not updateable |
| `Document` | base64 blob | Write-only ("so that we can save PDFs in SFX") |
| `Status` | picklist | None / In Progress / Queued / Generating / Completed / Failed |
| `ContentVersionDocumentId` | FK → ContentVersion | **Platform-populated — not settable on insert** |
| `DocumentTemplate` | String | **Not settable on insert** |

### The write contract (live-verified on `july15_margin`, 2026-07-23)

> **Insert a `QuoteDocument` with `QuoteId` + `Document` (PDF bytes) + `Status = 'Completed'`.**

The platform then:

- auto-creates a `ContentVersion` and populates `ContentVersionDocumentId`
  (verified: a `068…` Id came back populated);
- auto-names the file **`<QuoteName>_V<N>.pdf`** (verified: `New Quote For Infinitech_V1.pdf`);
- rolls up `GrandTotal` from the Quote;
- links the file so it appears in the **Quote PDFs** related list.

**Proven failure modes (do NOT do these):**

- Setting `ContentVersionDocumentId` on insert → `UNKNOWN_EXCEPTION, unexpected metadata: []`
  (you cannot point a QuoteDocument at an existing ContentVersion).
- `QuoteId` only, no `Document` → `ApexPagesHandledException` (bytes are required).
- Setting `DocumentTemplate` on insert → `unexpected metadata: []`.

---

## Why we can't just call a standard action to generate into a QuoteDocument

Investigated the "populate via a Service Document template / non-OmniStudio path" lead to
ground; it does not work on this org:

- The standard **`createServiceDocument`** invocable action **does** exist (describe at both
  v63 and v67: inputs `recordId` (req, ID), `templateId` (req, ID), `documentType` (STRING),
  plus `title`, `locale`, `pdfReportId`). This is the Field-Service Document Builder action.
- **But** its `documentType` is validated against a Field-Service "ServiceDocument"
  property-file section, and on `july15_margin` it **rejects every value tried** —
  `QuoteDocument`, `SfsQuoteDocument`, `WorkOrder`, `ServiceReport`, and empty — all return
  `INVALID_API_INPUT … val InvalidDocumentType not found in section ServiceDocument`.
  The quote document types are not provisioned on this org's action.
- The standard "**Generate PDF Document**" (Document Builder) button that normally populates
  Quote PDFs is served by **core Java** (`sales.quote.document`, Perforce, not indexed in
  codesearch). There is **no Apex trigger** on the standard object and **no public Connect
  REST generate endpoint for quotes** (unlike Billing's
  `POST /revenue/billing/document/actions/generate` → `InvoiceDocument`).

**Conclusion:** there is no supported server API we can call to "generate straight into a
QuoteDocument" on this org. The reliable, supported route is to let the existing server-side
DGP pipeline produce the PDF `ContentVersion` (as it does today), then **insert a
`QuoteDocument` from those bytes** using the verified write contract above.

---

## Current pipeline (what exists today)

Flow **`RLM_Quote_Doc_Gen_wAttachments`**
(`unpackaged/post_docgen/flows/RLM_Quote_Doc_Gen_wAttachments.flow-meta.xml`), launched by
quick action `Quote.RLM_Create_Proposal` ("Create Proposal"). Apex lives in
`unpackaged/post_docgen/classes/` (all `apiVersion 67.0`); there are **no dedicated Apex
tests** for the three existing classes. Deployed via `cci task run deploy_post_docgen`
(path `unpackaged/post_docgen`).

Spine:

1. **`Create_PDF_File`** → `RLM_DocumentGenerationCreate` inserts a
   `DocumentGenerationProcess` (`GenerateAndConvert`) → returns DGP Id (`varT_DocGenProcessId`).
2. Poll (`Status_Check_Single`) → **`Get_New_PDF_Content_Version_ID`** (DGP lookup) →
   **`Get_the_PDF_Document_Id`** (`RLM_ReturnPDFDocument`) → sets
   `varT_SingleDocContentVersionId` / `varT_SingleDocContentDocId` (the proposal PDF).
3. **Decision `File_Attachments`:**
   - **No attachments** (`varN_FileCount == 0`) → **`View_Output_Document`** previews
     `varT_SingleDocContentDocId`. *(final doc = the single proposal PDF)*
   - **Attachments** → `Add_Quote_Doc_to_Attachment_List` → **`Merge_PDF_Documents`**
     (`RLM_DocumentGenerationMerge`, `MergePDF`) → **`Get_New_Merge_PDF_Content_Version_ID`**
     (merged CV Id in `.ResponseText`) → **`Get_Multi_Doc_Content_Id`**
     (`varT_MultiDocContentDocId`) → **`Delete_Proposal_Doc`** (housekeeps the pre-merge single
     doc) → **`View_Multi_Documents`** previews `varT_MultiDocContentDocId`. *(final doc = merged PDF)*

Today, in **both** terminal branches the final PDF lives only as a **File** (ContentDocument)
on the Quote — never as a QuoteDocument.

---

## Recommended change — "replace" (one copy, as a Quote PDF)

Add a small invocable that turns the **final** PDF ContentVersion into a QuoteDocument, wire
it into **both** terminal branches, repoint the preview at the QuoteDocument's own file, and
delete the original plain File so the PDF lands **only** in Quote PDFs (honoring "instead of
the general notes/attachments").

### 1. New Apex: `unpackaged/post_docgen/classes/RLM_SaveQuoteDocument.cls` (+ `-meta.xml`, apiVersion 67.0)

`@InvocableMethod SaveAsQuotePdf` — input list of:

- `QuoteId` (Id, required)
- `ContentVersionId` (Id, required) — the final proposal/merged PDF ContentVersion
- `DocumentTitle` (String, optional — informational; the platform auto-names the file anyway)

Body (bulk-safe — no SOQL/DML in loops):

1. Query the input `ContentVersion`s (`VersionData`, `Title`) in one SOQL.
2. Build + `insert` one `QuoteDocument` per request: `QuoteId`, `Document = VersionData`,
   `Status = 'Completed'`.
3. Re-query the inserted QuoteDocuments for `ContentVersionDocumentId`; query those CVs'
   `ContentDocumentId` in one SOQL.
4. Return per request: `QuoteDocumentId`, `NewContentDocumentId`, `NewContentVersionId`.

Follow `.cursor/rules/apex-classes.mdc` — validate Ids with a try/cast (as
`RLM_ReturnPDFDocument` already does), and use `USER_MODE` / `as user` on the DML unless the
`cudAccessDelegate="Quote"` coverage is confirmed sufficient (see **Verify**, step 2).

### 2. Flow edits: `RLM_Quote_Doc_Gen_wAttachments.flow-meta.xml`

- **Merged branch:** after `Get_New_Merge_PDF_Content_Version_ID`, add an action call
  `Save_Merged_As_QuotePdf` → `RLM_SaveQuoteDocument` with
  `QuoteId = recordId`, `ContentVersionId = Get_New_Merge_PDF_Content_Version_ID.ResponseText`.
  Assign the returned `NewContentDocumentId` → `varT_MultiDocContentDocId` (so
  `View_Multi_Documents` previews the Quote PDF). Extend `Delete_Proposal_Doc` (or add a
  sibling delete) to also delete the **original merged** ContentDocument, leaving only the
  QuoteDocument's copy.
- **No-attachments branch:** on the `No_Attachments` route, before `View_Output_Document`, add
  `Save_Single_As_QuotePdf` → `RLM_SaveQuoteDocument` with
  `ContentVersionId = varT_SingleDocContentVersionId`. Assign the returned
  `NewContentDocumentId` → `varT_SingleDocContentDocId` (preview shows the Quote PDF); add a
  delete of the original single ContentDocument.
- Keep `apiVersion 67.0`, `status Active`.

### Simpler fallback (if you prefer "in addition" rather than "replace")

Skip the repoint + deletes: just call `RLM_SaveQuoteDocument` in both branches and leave the
existing File in place. Result: the PDF appears in **both** Files and Quote PDFs. One class,
two action-call nodes, no assignment/delete changes. Lower risk; does not fully satisfy the
"instead of the general notes/attachments" wording, but is trivially reversible.

---

## Files to add / modify

| File | Change |
|------|--------|
| `unpackaged/post_docgen/classes/RLM_SaveQuoteDocument.cls` (+ `.cls-meta.xml`) | **New** invocable |
| `unpackaged/post_docgen/classes/RLM_SaveQuoteDocumentTest.cls` (+ meta) | **New** minimal test (repo convention for new Apex; needed for prod-like deploys) |
| `unpackaged/post_docgen/flows/RLM_Quote_Doc_Gen_wAttachments.flow-meta.xml` | 2 action calls + assignments + delete edits (replace variant) |
| `docs/guides/docgen-setup.md` | Note the new "saved as Quote PDF" behavior (doc-consistency) |

No `cumulusci.yml` change — the new class lands under the existing `deploy_post_docgen` path.

---

## Verification (on `rlm-base__july15_margin`, Quote `0Q0dh000002MUO5CAO`)

1. Deploy: `cci task run deploy_post_docgen --org july15_margin`
   (or `sf project deploy start --source-dir unpackaged/post_docgen --target-org rlm-base__july15_margin`).
2. **Permissions:** confirm the launching persona can **create QuoteDocument**. Because
   `QuoteDocument.cudAccessDelegate="Quote"`, Quote-edit users should qualify — but verify the
   RLM sales permission set actually allows it and that the Revenue Cloud Advanced / Document
   Builder license is present (it is on this org; the live insert succeeded as admin).
3. Run the **Create Proposal** quick action on the Quote **twice**: once with **no**
   attachments and once **with** an attachment (exercises both terminal branches).
4. Assert:
   `SELECT Id, Name, QuoteId, Status, ContentVersionDocumentId FROM QuoteDocument WHERE QuoteId = '0Q0dh000002MUO5CAO'`
   returns one `0QD` per run, `Status = 'Completed'`, name `New Quote For Infinitech_V<N>.pdf`,
   and it appears in the **Quote PDFs** related list.
5. Replace variant only: assert the original merged/single ContentDocument is gone from the
   Quote's **Files** (only the Quote PDF copy remains) and the preview screen still renders.
6. **Idempotency:** run again → auto-versioning yields `_V2`, no errors, no orphaned Files.

> Per repo policy, a behavioral Flow change is **not** verified by `--dryrun`; it must run
> against a live scratch org before the PR merges.

---

## Notes / risks

- **Two-copy footprint.** Inserting `Document` bytes always creates a fresh ContentVersion; the
  replace variant's deletes are what keep it to a single copy. Get the delete ordering right so
  the preview (which reads the file) points at the surviving QuoteDocument copy, not a
  just-deleted one.
- **Governor safety.** A large merged PDF's `VersionData` goes through Apex heap — fine for the
  single-record screen-flow invocation; the invocable is written bulk-safe regardless.
- **No standard-action dependency.** Deliberately avoids `createServiceDocument` (proven
  unprovisioned for quotes here) and any unindexed core path.
- **Template versioning caveat.** If the proposal `DocumentTemplate` is redeployed, generate
  against the highest-version active `2dt…` Id — see the docgen redeploy-versioning note in
  `docs/guides/docgen-setup.md` / project memory.
