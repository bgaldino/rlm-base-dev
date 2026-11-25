---
page_id: connect-responses-document-details-output
title: Document Details
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-document-details-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_document_details_output.htm
fetched_at: 2026-11-25
---

# Document Details

Output representation of the details of the generated document.

## JSON Example

```
{
  "details": {
    "documentEntityId": "1BBSM00000003KT4AY",
    "documentGenerationProcessId": "0nnSM00000009jFYAQ",
    "documentTitle": "DOC-000000197",
    "existingDocumentId": "069SM000002PYQLYA4",
    "recordId": "3ttSM0000000o58YAA",
    "documentTemplateId": "0694x000000XyzABC"
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `documentEntityId` | String | Identifier of the related object record that manages the relationship between the source record and the generated document. For example, InvoiceDocument for Invoice records. | Big, 66.0 | 66.0 |
| `documentGenerationProcessId` | String | Identifier of the document generation process record that’s created to track this document generation request. | Big, 66.0 | 66.0 |
| `documentTemplateId` | String | Identifier of the document template that’s used to generate the PDF. | Big, 66.0 | 66.0 |
| `documentTitle` | String | Document title or name of the generated document. | Big, 66.0 | 66.0 |
| `existingDocumentId` | String | Identifier of the existing content document if a document is already generated and is available to view. | Big, 66.0 | 66.0 |
| `recordId` | String | Identifier of the source record the document is generated for. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-document-details-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
