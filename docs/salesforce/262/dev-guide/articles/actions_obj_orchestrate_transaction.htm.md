---
page_id: actions_obj_orchestrate_transaction.htm
title: Orchestrate Transaction Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_orchestrate_transaction.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Orchestrate Transaction Action

Orchestrate a transaction for any
domain-specific object, such as a collection plan for Revenue billing, that requires the
composition and execution of a fulfillment plan.

Specify the ID of the transaction to orchestrate and the orchestration type. The
orchestration process includes:

- Composition of the orchestration plan
- Execution of the fulfillment plan

This action is available in API
version
66.0 and later.

## Special Access Rules

The Orchestrate Transaction action is available in Enterprise, Unlimited, and
Developer Editions of Revenue Cloud. See the [required
permissions](https://help.salesforce.com/s/articleView?id=sf.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&language=en_US "HTML (New Window)") to access and call this invocable action.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/orchestrateTransaction`

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
| transactionId | Type  string  Description  Required. ID of the business object or domain object to be orchestrated, such as a Collection Plan ID. |
| orchestration​Type | Type  string  Description  Required. Type of orchestration that’s used to orchestrate the transaction. Valid values are:  - `Generic` - `Fulfillment` - `Billing` |

## Outputs

| Output | Details |
| --- | --- |
| requestId | Type  string  Description  Request ID of the invocation. |
| errorCode | Type  string  Description  Code that corresponds to the type of encountered error. |
| fulfillment​PlanId | Type  string  Description  ID of the composed fulfillment plan. |
| submitStatus | Type  string  Description  Submission status of the transaction that’s orchestrated. Valid values are:   - `Success` - `Error` |

## Example

POST
:   This sample request is for the Orchestrate Transaction action.

    ```
    {
      "inputs": [
        {
          "transactionId": "801xx000003GYexAAG",
          "orchestrationType": "Fulfillment"
        }
      ]
    }
    ```
:   This sample response is for the Orchestrate Transaction action.

    ```
    [
      {
        "actionName": "orchestrateTransaction",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "requestId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
          "fulfillmentPlanId": "0000000s21to18g0009176412796953180a8259def914e1abbd863dde076b71f",
          "submitStatus": "SUCCESS"
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
