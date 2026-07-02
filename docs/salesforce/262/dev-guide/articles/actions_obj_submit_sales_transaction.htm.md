---
page_id: actions_obj_submit_sales_transaction.htm
title: Submit Sales Transaction Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_submit_sales_transaction.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Submit Sales Transaction Action

Initiate the fulfillment process of any sales transaction, such as a
quote, an order, or an order summary.

Specify the ID of the sales transaction to be fulfilled. The fulfillment process includes these
steps.

- Intake process
- Fulfillment orchestration

The intake process happens synchronously or asynchronously, which is specified
by using the intakeRequestType input parameter. You can also
specify the priority for the execution of the fulfillment process, which is
specified by using the fulfillmentPriority
parameter.

This action is available in API version 63.0 and
later.

## Special Access Rules

The Submit Sales Transaction action is available in Enterprise, Unlimited, and
Developer Editions of Revenue Cloud. See the [required permissions](https://help.salesforce.com/s/articleView?id=ind.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&type=5&language=en_US) to access and call
this invocable action.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/submitSalesTransaction`

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
| allowOverrideOfPointOfNoReturn | Type  boolean  Description  Indicates whether to override the point of no return setting for the fulfillment step (`true`) or not (`false`). The default value is `false`. Available in API version 64.0 and later. |
| fulfillmentAdapter | Type  string  Description  Type of fulfillment adapter. Valid values are:   - `StandardOrder` - `GenericAdapter`—Available in API   version 64.0 and later. |
| fulfillmentPriority | Type  string  Description  Priority to fulfill the sales transaction. Valid values are:   - `High` - `Bulk` - `Default` |
| hydratedContextId | Type  string  Description  ID of the hydrated context. |
| intakeRequestType | Type  string  Description  Type of request to process the intake. Valid values are:   - `Synchronous` - `Asynchronous` |
| priorityLimitAction | Type  string  Description  Type of action to perform when the priority limit is reached. Valid values are:   - `Reject` - `Downgrade`  This parameter is applicable only when you specify the fulfillmentPriority parameter. |
| salesTransactionId | Type  id  Description  Required. ID of the sales transaction to submit. |

## Outputs

| Output | Details |
| --- | --- |
| errorCode | Type  string  Description  Code indicating the type of error. |
| fulfillmentPlanId | Type  id  Description  ID of the composed fulfillment plan. |
| requestedFulfillmentPriority | Type  string  Description  Priority to fulfill the sales transaction. Valid values are:   - `High` - `Bulk` - `Default` |
| requestId | Type  string  Description  Request ID of the invocation. |
| resolvedFulfillmentPriority | Type  string  Description  Resolved priority to fulfill the sales transaction. |
| submitStatus | Type  string  Description  Submit status of the invocation. |
| usedContextId | Type  string  Description  ID of the used context that updates the decomposition process. |

## Example

POST
:   This sample request is for the Submit Sales Transaction action.

    ```
    {
      "inputs": [
        {
          "allowOverrideOfPointOfNoReturn": false,
          "salesTransactionId": "801DV000000CbIPYA0",
          "intakeRequestType": "Synchronous",
          "fulfillmentAdapter": "StandardOrder",
          "fulfillmentPriority": "Default",
          "priorityLimitAction": "Reject"
        }
      ]
    }
    ```
:   This sample response is for the Submit Sales Transaction action.

    ```
    [
      {
        "actionName": "submitSalesTransaction",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "submitStatus": "SUCCESS",
          "resolvedFulfillmentPriority": "Default",
          "requestedFulfillmentPriority": "Default",
          "usedContextId": "0abc8db32b30d09c5051e4561f0b39d938a3bd8db4ccb13e04d41019e427211d",
          "requestId": "927f72b7-85e0-4b5d-b92e-c265f41898f0",
          "fulfillmentPlanId": "13VDV00000008M92AI"
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
