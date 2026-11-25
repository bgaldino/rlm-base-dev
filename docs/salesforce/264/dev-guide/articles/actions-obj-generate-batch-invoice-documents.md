---
page_id: actions-obj-generate-batch-invoice-documents
title: Generate Invoice Documents Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-generate-batch-invoice-documents.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-invocable-actions-parent
legacy_page_id: actions_obj_generate_batch_invoice_documents.htm
fetched_at: 2026-11-25
---

# Generate Invoice Documents Action

Asynchronously generate PDF documents for the invoices associated with an invoice batch run record that are in the `Draft` or `Posted` status.

This action uses the ID of the invoice batch run record to find the draft or posted invoices from the batch and to generate the PDF documents for its invoices that are in the `Draft` or `Posted` status. This action creates a DocGenerationBatchProcess record that contains the Document Generation Process and Invoice Document records for each of the invoices. This action is available in API version 63.0 and later with Revenue Cloud Billing.

## Special Access Rules

The Generate Invoice Documents action is available in Enterprise, Unlimited, and Developer Editions where Revenue Cloud Billing is enabled. The org must have Billing Docgen enabled and an active Invoice Document Template to generate PDF documents. To use this action, you need either the Billing Operations User or the Billing Admin permission set, along with the Docgen Designer and Docgen Designer Standard User permission sets.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/generateInvoiceDocuments`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `invoiceBatchRunId` | string | Required. ID of the invoice batch run record that created the draft or posted invoices. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `requestId` | string | An alphanumeric string to track the status of the document generation request. |
| `requestStatus` | boolean | Indicates whether the operation is successful (`true`) or not (`false`). |

## Example

**POST**

This example shows a sample request for the Generate Invoice Documents action.

```
{
  "inputs": [
    {
      "invoiceBatchRunId": "5IRSG000001Az014AC"
    }
  ]
}
```

This example shows a sample response for the Generate Invoice Documents action.

```
{
  "actionName": "generateInvoiceDocuments",
  "errors": null,
  "isSuccess": true,
  "outputValues": {
    "requestId": "4sFDU00000000652AA",
    "requestStatus": true
  }
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-generate-batch-invoice-documents.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
