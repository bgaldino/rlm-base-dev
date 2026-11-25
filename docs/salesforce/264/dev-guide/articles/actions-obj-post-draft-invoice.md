---
page_id: actions-obj-post-draft-invoice
title: Post Draft Invoice Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-post-draft-invoice.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-invocable-actions-parent
legacy_page_id: actions_obj_post_draft_invoice.htm
fetched_at: 2026-11-25
---

# Post Draft Invoice Action

Update the status of an invoice from `Draft` to `Posted` for a credit memo application.

This action uses the ID of the draft invoice and triggers an asynchronous process to post the invoice. This action is available in API version 62.0 and later.

## Special Access Rules

The Post Draft Invoice action is available in Enterprise, Unlimited, and Developer Editions where Billing is enabled. To use this action, you need the Billing Operations User permission set.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/postDraftInvoice`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `correlationId` | string | Splunk correlation ID to track the messages that are related to the request and are logged in Splunk by the different services involved in the request. If the ID isn’t specified, the service creates a random Universally Unique Identifier (UUID). |
| `invoiceId` | string | Required. ID of the `Draft` invoice to be posted. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `requestIdentifier` | string | UUID that’s used to track the status of the asynchronous action. |
| `statusUrl` | string | URL that’s used to check the status of the API request. |

## Example

**POST**

This example shows a sample request for the Post Draft Invoice action.

```
{
  "inputs": [
    {
      "invoiceId": "3ttDU00000000iZYAQ"
    }
  ]
}
```

This example shows a sample response for the Post Draft Invoice action.

```
{
  "actionName": "postDraftInvoice",
  "errors": null,
  "isSuccess": true,
  "outputValues": {
    "requestIdentifier": "4sFDU00000000652AA",
    "statusUrl": "/services/data/v62.0/sobjects/AsyncOperationTracker/16Pxx0000004NhAEAU"
  }
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-post-draft-invoice.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
