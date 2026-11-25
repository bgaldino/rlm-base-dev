---
page_id: actions-obj-unfreeze-sales-transaction
title: Unfreeze Sales Transaction Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-unfreeze-sales-transaction.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-invocable-actions-parent
legacy_page_id: actions_obj_unfreeze_sales_transaction.htm
fetched_at: 2026-11-25
---

# Unfreeze Sales Transaction Action

Unfreeze a sales transaction to enable the modification of a line item.

A line item can reach a milestone in the fulfillment process, which is known as a point of no return, where the line item can’t accept modifications. Get details about the point of no return for each line item of a sales transaction.

This action is available in API version 64.0 and later.

## Special Access Rules

The Unfreeze Sales Transaction action is available in Enterprise, Unlimited, and Developer Editions of Revenue Management. See the [required permissions](https://help.salesforce.com/s/articleView?id=ind.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&type=5) to access and call this invocable action.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/unfreezeSalesTransaction`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `salesTransactionId` | id | Required. ID of the sales transaction that’s submitted to the Dynamic Revenue Orchestrator. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `errorCode` | string | Code indicating the type of error. |
| `orchestrationPlanId` | id | ID of the created orchestration plan. |
| `planState` | string | Status of the created orchestration plan. Valid values are `FAILURE`, `NOTSTARTED`, `PENDING`, `COMPLETED`, `FROZEN`, or `INPROGRESS`. |
| `requestId` | string | ID of the request to get the point of no return details. |
| `salesTransaction​Id` | string | ID of the sales transaction that’s submitted to the Dynamic Revenue Orchestrator. |

## Example

**POST**

This sample request is for the Unfreeze Sales Transaction action.

```
{
  "inputs": [
    {
      "salesTransactionId": "801SG00000jQO1ZYAW"
    }
  ]
}
```

This sample response is for the Unfreeze Sales Transaction action.

```
[
  {
    "actionName": "unfreezeSalesTransaction",
    "errors": null,
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": {
      "orchestrationPlanId": "13VSG00000229Z72AI",
      "salesTransactionId": "801SG00000jQO1ZYAW",
      "planState": "InProgress",
      "requestId": "e9f2d961-b218-4911-8fee-8de31937850d"
    },
    "sortOrder": -1,
    "version": 1
  }
]
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-unfreeze-sales-transaction.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
