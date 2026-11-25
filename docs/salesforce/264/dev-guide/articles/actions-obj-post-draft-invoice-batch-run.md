---
page_id: actions-obj-post-draft-invoice-batch-run
title: Post Draft Invoice Batch Run Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-post-draft-invoice-batch-run.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-invocable-actions-parent
legacy_page_id: actions_obj_post_draft_invoice_batch_run.htm
fetched_at: 2026-11-25
---

# Post Draft Invoice Batch Run Action

Update the status of a batch of invoices from `Draft` to `Posted` for a credit memo application.

This action uses the ID of the invoice batch run record to find draft invoices from the batch and to post the draft invoices to an invoice record. This action is available in API version 62.0 and later.

## Special Access Rules

The Post Draft Invoice Batch Run action is available in Enterprise, Unlimited, and Developer Editions where Billing is enabled. To use this action, you need the Billing Operations User permission set.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/postDraftInvoiceBatchRun`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `invoiceBatchRunId` | string | Required. ID of the invoice batch run record that created the draft invoices. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `invBatchDraftToPostedRunId` | string | ID of the record that’s created to track the batch process of posting draft invoices. These draft invoices are associated with the parent invoice batch run record. |

## Example

**POST**

This example shows a sample request for the Post Draft Invoice Batch Run action.

```
{
  "inputs": [
    {
      "invoiceBatchRunId": "5IRSG000001Az014AC"
    }
  ]
}
```

This example shows a sample response for the Post Draft Invoice Batch Run action.

```
{
  "actionName": "postDraftInvoiceBatchRun",
  "errors": null,
  "isSuccess": true,
  "outputValues": {
    "invBatchDraftToPostedRunId": "4sFDU00000000652AA"
  }
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-post-draft-invoice-batch-run.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
