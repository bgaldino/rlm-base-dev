---
page_id: actions-obj-orchestrate-sales-transaction
title: Orchestrate Sales Transaction Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-orchestrate-sales-transaction.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-invocable-actions-parent
legacy_page_id: actions_obj_orchestrate_sales_transaction.htm
fetched_at: 2026-11-25
---

# Orchestrate Sales Transaction Action

Initiate the orchestration process for a sales transaction. This action executes only the plan composition and orchestration phases, without performing decomposition.

Specify the ID of the sales transaction to orchestrate. The decomposition process includes these steps.

- Intake process

- Fulfillment orchestration

The intake process occurs synchronously or asynchronously, as specified with the `intakeRequestType` input parameter. You can also specify the orchestration priority using the `fulfillmentPriority` parameter.

Use this action when the sales transaction is decomposed either by a previous decomposition action or by custom logic before orchestrating the fulfillment plan.

This action is available in API version 68.0 and later.

## Special Access Rules

The Orchestrate Sales Transaction action is available in Enterprise, Unlimited, and Developer Editions of Revenue Management. See the [required permissions](https://help.salesforce.com/s/articleView?id=sf.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&language=en_US) to access and call this invocable action.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/orchestrateSalesTransaction`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `allowOverride​OfPointOfNoReturn` | boolean | Indicates whether to override the point-of-no-return setting for the fulfillment step ( `true` ) or not ( `false` ). The default value is `false`. |
| `fulfillmentAdapter` | string | Required. Type of fulfillment adapter. Valid values are `StandardOrder` or `GenericAdapter`. |
| `fulfillmentPriority` | string | Priority to fulfill the sales transaction. Valid values are `High`, `Bulk`, or `Default`. |
| `hydratedContextId` | string | ID of the hydrated context. |
| `intakeRequestType` | string | Type of request to process the intake. Valid values are `Synchronous` or `Asynchronous`. |
| `priorityLimit​Action` | string | Type of action to perform when the priority limit is reached. Valid values are `Reject` or `Downgrade`. This parameter is applicable only when you specify the `fulfillmentPriority` parameter. |
| `salesTransactionId` | id | Required. ID of the sales transaction to submit. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `errorCode` | string | Code indicating the type of error. |
| `fulfillmentPlanId` | id | ID of the composed fulfillment plan. |
| `requested​FulfillmentPriority` | string | Priority to fulfill the sales transaction. Valid values are `High`, `Bulk`, or `Default`. |
| `requestId` | string | Request ID of the invocation. |
| `resolved​FulfillmentPriority` | string | Resolved priority to fulfill the sales transaction. Valid values are `High`, `Bulk`, or `Default`. |
| `submitStatus` | string | Submission status of the sales transaction for orchestration. Valid values are `SUCCESS`, `ERROR`, `SUBMITTED`, or `REJECTED`. |
| `usedContextId` | string | ID of the context that updates the orchestration process. |

## Example

**POST**

This sample request is for the Orchestrate Sales Transaction action.

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

This sample response is for the Orchestrate Sales Transaction action.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-orchestrate-sales-transaction.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
