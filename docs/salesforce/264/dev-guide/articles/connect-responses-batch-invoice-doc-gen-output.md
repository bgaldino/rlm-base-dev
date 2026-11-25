---
page_id: connect-responses-batch-invoice-doc-gen-output
title: Batch Invoice Document Generation
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-batch-invoice-doc-gen-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_batch_invoice_doc_gen_output.htm
fetched_at: 2026-11-25
---

# Batch Invoice Document Generation

Output representation of the request to generate or regenerate the PDF documents for the invoices that are in the `Draft` or `Posted` status.

## JSON Example

```
{
  "errors": [
    {
      "errorCode": "API_DISABLED_FOR_ORG",
      "errorMessage": "Document Generation is not enabled for this org!"
    },
    {
      "errorCode": "INVALID_API_INPUT",
      "errorMessage": "Invalid Invoice Batch Run Id"
    }
  ],
  "requestIdentifier": "5IRDU000000009i4AA",
  "success": false
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Batch Invoice Document Generation Error []](./connect-responses-batch-invoice-doc-gen-error.md) | Details of the error if the operation fails. | Big, 63.0 | 63.0 |
| `requestIdentifier` | String | Unique ID that’s associated with the specific error, and is used for tracking and referencing the request. | Big, 63.0 | 63.0 |
| `success` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Big, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-batch-invoice-doc-gen-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
