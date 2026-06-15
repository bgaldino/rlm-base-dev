---
page_id: actions_obj_get_point_of_no_return.htm
title: Get Point Of No Return Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_get_point_of_no_return.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Get Point Of No Return Action

Get details about the point of no return milestone for each line
item in a sales transaction.

A line item can reach a milestone in the fulfillment
process, which is known as a point of no return, where the line item can’t accept
modifications. Get details about the point of no return for each line item of a
sales transaction.

This action is available in API version 64.0 and later.

## Special Access Rules

The Get Point Of No Return action is available in Enterprise, Unlimited, and
Developer Editions of Revenue Cloud. See the [required permissions](https://help.salesforce.com/s/articleView?id=ind.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&type=5&language=en_US) to access and call
this invocable action.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/getPointOfNoReturn`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization:
    Bearertoken`

## Inputs

| Input | Details |
| --- | --- |
| salesTransactionId | Type  id  Description  Required. ID of the sales transaction to get the point of no return details for. |

## Outputs

| Output | Details |
| --- | --- |
| errorCode | Type  string  Description  Code indicating the type of error. |
| lineItems​PointOf​NoReturn​Info | Type  string  Description  Line items with the point of no return details. |
| planId | Type  id  Description  ID of the composed fulfillment plan. |
| planState | Type  string  Description  State of the fulfillment plan. |
| requestId | Type  string  Description  Request ID of the invocation. |
| salesTransaction​Id | Type  string  Description  ID of the submitted sales transaction. |

## Example

POST
:   This sample request is for the Get Point Of No Return action.

    ```
    {
      "inputs": [
        {
          "salesTransactionId": "801SG00000jQO1ZYAW"
        }
      ]
    }
    ```
:   This sample response is for the Get Point Of No Return action.

    ```
    [
      {
        "actionName": "getPointOfNoReturn",
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
