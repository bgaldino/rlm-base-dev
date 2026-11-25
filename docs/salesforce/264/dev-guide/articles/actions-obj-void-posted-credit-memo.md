---
page_id: actions-obj-void-posted-credit-memo
title: Void Posted Credit Memo Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-void-posted-credit-memo.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-invocable-actions-parent
legacy_page_id: actions_obj_void_posted_credit_memo.htm
fetched_at: 2026-11-25
---

# Void Posted Credit Memo Action

Invoke the Void Posted Credit Memo API by providing a credit memo ID.

This action is available in API version 66.0 and later.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/voidPostedCreditMemo`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `creditMemoId` | string | Required. ID of the credit memo record in posted status to be voided. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `debitMemoId` | string | ID of the created debit memo record. |
| `statusUrl` | string | URL to use to check the status of the request. |

## Example

**POST**

Here’s a sample request for the Void Posted Credit Memo action.

```
{
  "inputs": [
    {
      "creditMemoId": "50gSG0000001y5NYAQ"
    }
  ]
}
```

Here’s a sample response for the Void Posted Credit Memo action.

```
[
  {
    "actionName": "voidPostedCreditMemo",
    "errors": [],
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": {
      "debitMemoId": "4DmSG000001YcIP0A0",
      "statusUrl": "/services/data/v68.0/sobjects/AsyncOperationTracker/16PSG000001qlyL2AQ"
    },
    "sortOrder": -1,
    "version": 1
  }
]
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-void-posted-credit-memo.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
