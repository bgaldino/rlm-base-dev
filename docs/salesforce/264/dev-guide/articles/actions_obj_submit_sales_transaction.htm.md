---
page_id: actions_obj_submit_sales_transaction.htm
title: Submit Sales Transaction Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_submit_sales_transaction.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_invocable_actions_parent.htm
fetched_at: 2026-11-23
---

# Submit Sales Transaction Action

Initiate the fulfillment process of any sales transaction, such as a quote, an order, or an order summary.

Specify the ID of the sales transaction to be fulfilled. The fulfillment process includes these steps.

- Intake process
- Fulfillment orchestration

The intake process happens synchronously or asynchronously, which is specified by using the intakeRequestType input parameter. You can also specify the priority for the execution of the fulfillment process, which is specified by using the fulfillmentPriority parameter.

This action is available in API version 63.0 and later.

## Special Access Rules

The Submit Sales Transaction action is available in Enterprise, Unlimited, and Developer Editions of Revenue Management. See the [required permissions](https://help.salesforce.com/s/articleView?id=ind.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&type=5&language=en_US) to access and call this invocable action.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/submitSalesTransaction`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer token`

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| allowOverrideOfPointOfNoReturn | boolean | Indicates whether to override the point of no return setting for the fulfillment step ( `true` ) or not ( `false` ). The default value is `false`. Available in API version 64.0 and later. |
| fulfillmentAdapter | string | Type of fulfillment adapter. Valid values are `StandardOrder`; or `GenericAdapter`—Available in API version 64.0 and later. |
| fulfillmentPriority | string | Priority to fulfill the sales transaction. Valid values are `High`, `Bulk`, or `Default`. |
| hydratedContextId | string | ID of the hydrated context. |
| intakeRequestType | string | Type of request to process the intake. Valid values are `Synchronous` or `Asynchronous`. |
| priorityLimitAction | string | Type of action to perform when the priority limit is reached. Valid values are `Reject` or `Downgrade`. This parameter is applicable only when you specify the fulfillmentPriority parameter. |
| salesTransactionId | id | Required. ID of the sales transaction to submit. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| errorCode | string | Code indicating the type of error. |
| fulfillmentPlanId | id | ID of the composed fulfillment plan. |
| requestedFulfillmentPriority | string | Priority to fulfill the sales transaction. Valid values are `High`, `Bulk`, or `Default`. |
| requestId | string | Request ID of the invocation. |
| resolvedFulfillmentPriority | string | Resolved priority to fulfill the sales transaction. |
| submitStatus | string | Submit status of the invocation. |
| usedContextId | string | ID of the used context that updates the decomposition process. |

## Example

**POST**

This sample request is for the Submit Sales Transaction action.

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

This sample response is for the Submit Sales Transaction action.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_submit_sales_transaction.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
