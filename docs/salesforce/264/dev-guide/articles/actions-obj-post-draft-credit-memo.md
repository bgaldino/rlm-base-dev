---
page_id: actions-obj-post-draft-credit-memo
title: Post Draft Credit Memo Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-post-draft-credit-memo.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-invocable-actions-parent
legacy_page_id: actions_obj_post_draft_credit_memo.htm
fetched_at: 2026-11-25
---

# Post Draft Credit Memo Action

Post a draft credit memo to a credit memo record for review and approval.

This action is available in API version 65.0 and later.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/postDraftCreditMemo`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `correlationId` | string | Splunk correlation ID to use to track messages that are related to the request and logged in Splunk by the different services involved in the request. If not specified, the service creates a random Universally Unique Identifier (UUID). |
| `creditMemoId` | string | Required. ID of the credit memo record in `Draft` status to be posted. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `requestIdentifier` | string | The UUID that’s used to track the status of the asynchronous action. |
| `statusUrl` | string | The URL to use to check the status of the request. |

## Example

**POST**

This example shows a sample request that contains the ID of the credit memo to be posted.

```
{
  "inputs": [
    {
      "creditMemoId": "50gDU00000001MdYAI"
    }
  ]
}
```

This example shows a sample successful response.

```
[
  {
    "actionName": "postDraftCreditMemo",
    "errors": [],
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": {
      "statusUrl": "/services/data/v68.0/sobjects/AsyncOperationTracker/16PDU000000A4nw2AC",
      "requestIdentifier": "d3a9d9ce-2a83-4a08-bcf3-df0348a0008c"
    },
    "sortOrder": -1,
    "version": 1
  }
]
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-post-draft-credit-memo.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
