---
page_id: actions_obj_get_point_of_no_return.htm
title: Get Point Of No Return Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_get_point_of_no_return.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_invocable_actions_parent.htm
fetched_at: 2026-11-23
---

# Get Point Of No Return Action

Get details about the point of no return milestone for each line item in a sales transaction.

A line item can reach a milestone in the fulfillment process, which is known as a point of
no return, where the line item can’t accept modifications. Get details about the point of no
return for each line item of a sales transaction.

This action is available in API version 64.0 and later.

## Special Access Rules

The Get Point Of No Return action is available in Enterprise, Unlimited, and Developer Editions of Revenue Management. See the [required permissions](https://help.salesforce.com/s/articleView?id=ind.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&type=5&language=en_US) to access and call this invocable action.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/getPointOfNoReturnDetails`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer token`

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| salesTransactionId | id | Required. ID of the sales transaction to get the point of no return details for. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| errorCode | string | Code indicating the type of error. |
| lineItems​PointOf​NoReturn​Info | string | Line items with the point of no return details. |
| planId | id | ID of the composed fulfillment plan. |
| planState | string | State of the fulfillment plan. |
| requestId | string | Request ID of the invocation. |
| salesTransaction​Id | string | ID of the submitted sales transaction. |

## Example

**POST**

This sample request is for the Get Point Of No Return action.

```
{
  "inputs": [
    {
      "salesTransactionId": "801SG00000jQO1ZYAW"
    }
  ]
}
```

This sample response is for the Get Point Of No Return action.

```
[
  {
    "actionName": "getPointOfNoReturnDetails",
    "errors": null,
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": {
      "planId": "13VSG00000229Z72AI",
      "requestId": "35c9388b-d30d-4d68-aae5-c109c8bff7ef",
      "lineItemsPointOfNoReturnInfo": "802SG000007D0B4YAK\": {\namendAllowed: false,\nanyChangesAllowed: true,\ncancelAllowed: false\n}, \n802SG000007D0B3YAK\": {\namendAllowed: false,\nanyChangesAllowed: true,\ncancelAllowed: false\n}",
      "salesTransactionId": "801SG00000jQO1ZYAW",
      "planState": "InProgress"
    },
    "sortOrder": -1,
    "version": 1
  }
]
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_get_point_of_no_return.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
