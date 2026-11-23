---
page_id: actions_obj_freeze_sales_transaction.htm
title: Freeze Sales Transaction Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_freeze_sales_transaction.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_invocable_actions_parent.htm
fetched_at: 2026-11-23
---

# Freeze Sales Transaction Action

Freeze a sales transaction to disable the modification of a line item.

A line item can reach a milestone in the fulfillment process, which is known as a point of no return, where the line item can’t accept modifications. Get details about the point of no return for each line item of a sales transaction.

This action is available in API version 64.0 and later.

## Special Access Rules

The Freeze Sales Transaction action is available in Enterprise, Unlimited, and Developer Editions of Revenue Cloud. See the [required permissions](https://help.salesforce.com/s/articleView?id=ind.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&type=5&language=en_US) to access and call this invocable action.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/freezeSalesTransaction`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer token`

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| salesTransactionId | id | Required. ID of the sales transaction that's submitted to the Dynamic Revenue Orchestrator. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| errorCode | string | Code indicating the type of error. |
| orchestration​PlanId | id | ID of the created orchestration plan. |
| planState | string | Status of the created orchestration plan. Valid values are `FAILURE`, `NOTSTARTED`, `PENDING`, `COMPLETED`, `FROZEN`, or `INPROGRESS`. |
| pointOf​NoReturn​DetailFor​LineItems​List | string | Collection of sales transaction line items, where each item includes a boolean value indicating whether it has reached the point of no return. |
| requestId | string | ID of the request to get the point of no return details. |
| salesTransaction​Id | string | ID of the sales transaction that's submitted to the Dynamic Revenue Orchestrator. |

## Example

**POST**

This sample request is for the Freeze Sales Transaction action.

```
{
    "inputs": [
        {
            "salesTransactionId": "801SG00000jQO1ZYAW"
        }
    ]
}
```

This sample response is for the Freeze Sales Transaction action.

```
[
  {
    "actionName": "freezeSalesTransaction",
    "errors": null,
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": {
      "salesTransactionId": "801SG00000jQO1ZYAW",
      "orchestrationPlanId": "13VSG00000229Z72AI",
      "requestId": "452789a6-f2ab-4079-8aca-a11dbfef6a45",
      "pointOfNoReturnDetailForLineItemsList": "802SG000007D0B4YAK\": {\namendAllowed: false,\nanyChangesAllowed: true,\ncancelAllowed: false\n}, \n802SG000007D0B3YAK\": {\namendAllowed: false,\nanyChangesAllowed: true,\ncancelAllowed: false\n}",
      "planState": "Frozen"
    },
    "sortOrder": -1,
    "version": 1
  }
]
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_freeze_sales_transaction.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
