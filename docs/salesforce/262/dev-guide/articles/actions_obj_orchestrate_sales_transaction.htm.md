---
page_id: actions_obj_orchestrate_sales_transaction.htm
title: Orchestrate Sales Transaction Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_orchestrate_sales_transaction.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Orchestrate Sales Transaction Action

Initiate the orchestration process for a sales
transaction. This action executes only the plan composition and orchestration
phases, without performing decomposition.

Specify the ID of the sales transaction to orchestrate. The decomposition process
includes these steps.

- Intake process
- Fulfillment orchestration

The intake process occurs synchronously or asynchronously, as specified with the
intakeRequestType input parameter. You can also specify the
orchestration priority using the fulfillmentPriority
parameter.

Use this action when the sales transaction is decomposed either by a previous
decomposition action or by custom logic before orchestrating the fulfillment
plan.

This action is available in API version 67.0 and later.

## Special Access Rules

The Orchestrate Sales Transaction action is available in Enterprise, Unlimited, and
Developer Editions of Revenue Cloud. See the [required permissions](https://help.salesforce.com/s/articleView?id=sf.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&language=en_US) to access and call
this invocable action.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/orchestrateSalesTransaction`

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
| allowOverride​OfPointOfNoReturn | Type  boolean  Description  Indicates whether to override the point-of-no-return setting for the fulfillment step (`true`) or not (`false`). The default value is `false`. |
| fulfillmentAdapter | Type  string  Description  Required. Type of fulfillment adapter. Valid values are:   - `StandardOrder` - `GenericAdapter` |
| fulfillmentPriority | Type  string  Description  Priority to fulfill the sales transaction. Valid values are:   - `High` - `Bulk` - `Default` |
| hydratedContextId | Type  string  Description  ID of the hydrated context. |
| intakeRequestType | Type  string  Description  Type of request to process the intake. Valid values are:   - `Synchronous` - `Asynchronous` |
| priorityLimit​Action | Type  string  Description  Type of action to perform when the priority limit is reached. Valid values are:   - `Reject` - `Downgrade`  This parameter is applicable only when you specify the fulfillmentPriority parameter. |
| salesTransactionId | Type  id  Description  Required. ID of the sales transaction to submit. |

## Outputs

| Output | Details |
| --- | --- |
| errorCode | Type  string  Description  Code indicating the type of error. |
| fulfillmentPlanId | Type  id  Description  ID of the composed fulfillment plan. |
| requested​FulfillmentPriority | Type  string  Description  Priority to fulfill the sales transaction. Valid values are:   - `High` - `Bulk` - `Default` |
| requestId | Type  string  Description  Request ID of the invocation. |
| resolved​FulfillmentPriority | Type  string  Description  Resolved priority to fulfill the sales transaction. Valid values are:   - `High` - `Bulk` - `Default` |
| submitStatus | Type  string  Description  Submission status of the sales transaction for orchestration. Valid values are:  - `SUCCESS` - `ERROR` - `SUBMITTED` - `REJECTED` |
| usedContextId | Type  string  Description  ID of the context that updates the orchestration process. |

## Example

POST
:   This sample request is for the Orchestrate Sales Transaction action.

    ```
    {
        "inputs": [
            {
                "fulfillmentAdapter": "StandardOrder",
                "intakeRequestType": "Synchronous",
                "salesTransactionId": "801xx000003GYgZAAW"
            }
        ]
    }
    ```
:   This sample response is for the Orchestrate Sales Transaction action.

    ```
    [
      {
        "actionName": "orchestrateSalesTransaction",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "usedContextId": "0000000s21to18g00091764134566956e2100424de0d4af8869669df515e24cb",
          "requestId": "ac2a9d18-c702-43ee-bc08-1c03061b549c",
          "fulfillmentPlanId": "13Vxx0000004CFUEA2",
          "submitStatus": "SUCCESS",
          "resolvedFulfillmentPriority": "Default",
          "requestedFulfillmentPriority": "Default"
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
