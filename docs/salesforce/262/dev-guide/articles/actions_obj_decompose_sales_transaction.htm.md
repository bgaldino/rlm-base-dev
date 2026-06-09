---
page_id: actions_obj_decompose_sales_transaction.htm
title: Decompose Sales Transaction Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_decompose_sales_transaction.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Decompose Sales Transaction Action

Decompose a sales transaction, such as a quote, order, or
order summary.

Specify the ID of the sales transaction to decompose. The decomposition process
includes these steps.

- Intake process
- Sales transaction decomposition

The intake process occurs synchronously or asynchronously, as specified with the
intakeRequestType input parameter. You can also specify the
decomposition priority using the fulfillmentPriority
parameter.

This action executes only the decomposition process and stops before orchestration.
You can execute custom logic in between the decomposition and orchestration
processes.

This action is available in API version 67.0 and later.

## Special Access Rules

The Decompose Sales Transaction action is available in Enterprise, Unlimited, and
Developer Editions of Revenue Cloud. See the [required permissions](https://help.salesforce.com/s/articleView?id=sf.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&language=en_US) to access and call
this invocable action.

## Supported REST HTTP Methods

URI
:   `/services/data/v66.0/actions/standard/decomposeSalesTransaction`

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
| allowOverride​OfPointOfNoReturn | Type  boolean  Description  Indicates whether to override the point of no return setting for the fulfillment step (`true`) or not (`false`). The default value is `false`. |
| fulfillmentAdapter | Type  string  Description  Required. Type of fulfillment adapter. Valid values are:   - `StandardOrder` - `GenericAdapter` |
| fulfillmentPriority | Type  string  Description  Priority to fulfill the sales transaction. Valid values are:   - `High` - `Bulk` - `Default` |
| hydratedContextId | Type  string  Description  ID of the hydrated context. |
| intakeRequestType | Type  string  Description  Type of request to process the intake. Valid values are:   - `Synchronous` - `Asynchronous` |
| priorityLimit​Action | Type  string  Description  Type of action to perform when the priority limit is reached. Valid values are:   - `Reject` - `Downgrade`  This parameter is applicable only when you specify the fulfillmentPriority parameter. |
| sales​TransactionId | Type  id  Description  Required. ID of the sales transaction to submit. |

## Outputs

| Output | Details |
| --- | --- |
| errorCode | Type  string  Description  Code that corresponds to the type of error encountered. |
| requested​FulfillmentPriority | Type  string  Description  Priority to fulfill the sales transaction. Valid values are:   - `High` - `Bulk` - `Default` |
| requestId | Type  string  Description  Request ID of the invocation. |
| resolved​FulfillmentPriority | Type  string  Description  Resolved priority to fulfill the sales transaction. Valid values are:   - `High` - `Bulk` - `Default` |
| submitStatus | Type  string  Description  Submission status of the sales transaction for decomposition. Valid values are:  - `Success` - `Error` - `Submitted` - `Rejected` |
| usedContextId | Type  string  Description  ID of the used context that updates the decomposition process. |

## Example

POST
:   This sample request is for the Decompose Sales Transaction action.

    ```
    {
      "inputs": [
        {
          "fulfillmentAdapter": "StandardOrder",
          "intakeRequestType": "Synchronous",
          "salesTransactionId": "801xx000003GYexAAG"
        }
      ]
    }
    ```
:   This sample response is for the Decompose Sales Transaction action.

    ```
    [
      {
        "actionName": "decomposeSalesTransaction",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "requestId": "ee3ded2e-fe43-401b-a54d-9124d48a0b72",
          "requestedFulfillmentPriority": "Default",
          "submitStatus": "SUCCESS",
          "usedContextId": "0000000s21to18g0009176412796953180a8259def914e1abbd863dde076b71f",
          "resolvedFulfillmentPriority": "Default"
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
