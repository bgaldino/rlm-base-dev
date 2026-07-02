---
page_id: actions_obj_freeze_sales_transaction.htm
title: Freeze Sales Transaction Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_freeze_sales_transaction.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Freeze Sales Transaction Action

Freeze a sales transaction to disable the modification of a line
item.

A line item can reach a milestone in the fulfillment
process, which is known as a point of no return, where the line item can’t accept
modifications. Get details about the point of no return for each line item of a
sales transaction.

This action is available in API version 64.0 and later.

## Special Access Rules

The Freeze Sales Transaction action is available in Enterprise, Unlimited, and Developer Editions
of Revenue Cloud. See the [required permissions](https://help.salesforce.com/s/articleView?id=ind.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&type=5&language=en_US) to access and call
this invocable action.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/freezeSalesTransaction`

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
| orchestration​PlanId | Type  id  Description  ID of the created orchestration plan. |
| planState | Type  string  Description  Status of the created orchestration plan. Valid values are:   - `FAILURE` - `NOTSTARTED` - `PENDING` - `COMPLETED` - `FROZEN` - `INPROGRESS` |
| pointOf​NoReturn​DetailFor​LineItems​List | Type  string  Description  Collection of sales transaction line items, where each item includes a boolean value indicating whether it has reached the point of no return. |
| requestId | Type  string  Description  ID of the request to get the point of no return details. |
| salesTransaction​Id | Type  string  Description  ID of the sales transaction that's submitted to the Dynamic Revenue Orchestrator. |

## Example

POST
:   This sample request is for the Freeze Sales Transaction action.

    ```
    {
        "inputs": [
            {
                "salesTransactionId": "801SG00000jQO1ZYAW"
            }
        ]
    }
    ```
:   This sample response is for the Freeze Sales Transaction action.

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
