---
page_id: actions_obj_unfreeze_sales_transaction.htm
title: Unfreeze Sales Transaction Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_unfreeze_sales_transaction.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Unfreeze Sales Transaction Action

Unfreeze a sales transaction to enable the modification of a line
item.

A line item can reach a milestone in the fulfillment
process, which is known as a point of no return, where the line item can’t accept
modifications. Get details about the point of no return for each line item of a
sales transaction.

This action is available in API version 64.0 and later.

## Special Access Rules

The Unfreeze Sales Transaction action is available in Enterprise, Unlimited, and
Developer Editions of Revenue Cloud. See the [required permissions](https://help.salesforce.com/s/articleView?id=ind.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&type=5&language=en_US) to access and call
this invocable action.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/unfreezeSalesTransaction`

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
| salesTransactionId | Type  id  Description  Required. ID of the sales transaction that's submitted to the Dynamic Revenue Orchestrator. |

## Outputs

| Output | Details |
| --- | --- |
| errorCode | Type  string  Description  Code indicating the type of error. |
| orchestrationPlanId | Type  id  Description  ID of the created orchestration plan. |
| planState | Type  string  Description  Status of the created orchestration plan. Valid values are:   - `FAILURE` - `NOTSTARTED` - `PENDING` - `COMPLETED` - `FROZEN` - `INPROGRESS` |
| requestId | Type  string  Description  ID of the request to get the point of no return details. |
| salesTransaction​Id | Type  string  Description  ID of the sales transaction that's submitted to the Dynamic Revenue Orchestrator. |

## Example

POST
:   This sample request is for the Unfreeze Sales Transaction action.

    ```
    {
      "inputs": [
        {
          "salesTransactionId": "801SG00000jQO1ZYAW"
        }
      ]
    }
    ```
:   This sample response is for the Unfreeze Sales Transaction action.

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
