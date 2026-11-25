---
page_id: actions-obj-decompose-sales-transaction
title: Decompose Sales Transaction Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-decompose-sales-transaction.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-invocable-actions-parent
legacy_page_id: actions_obj_decompose_sales_transaction.htm
fetched_at: 2026-11-25
---

# Decompose Sales Transaction Action

Decompose a sales transaction, such as a quote, order, or order summary.

Specify the ID of the sales transaction to decompose. The decomposition process includes these steps.

- Intake process

- Sales transaction decomposition

The intake process occurs synchronously or asynchronously, as specified with the `intakeRequestType` input parameter. You can also specify the decomposition priority using the `fulfillmentPriority` parameter.

This action executes only the decomposition process and stops before orchestration. You can execute custom logic in between the decomposition and orchestration processes.

This action is available in API version 68.0 and later.

## Special Access Rules

The Decompose Sales Transaction action is available in Enterprise, Unlimited, and Developer Editions of Revenue Management. See the [required permissions](https://help.salesforce.com/s/articleView?id=sf.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&language=en_US) to access and call this invocable action.

## Supported REST HTTP Methods

**URI:** `/services/data/v66.0/actions/standard/decomposeSalesTransaction`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `allowOverride​OfPointOfNoReturn` | boolean | Indicates whether to override the point of no return setting for the fulfillment step ( `true` ) or not ( `false` ). The default value is `false`. |
| `fulfillmentAdapter` | string | Required. Type of fulfillment adapter. Valid values are `StandardOrder` or `GenericAdapter`. |
| `fulfillmentPriority` | string | Priority to fulfill the sales transaction. Valid values are `High`, `Bulk`, or `Default`. |
| `hydratedContextId` | string | ID of the hydrated context. |
| `intakeRequestType` | string | Type of request to process the intake. Valid values are `Synchronous` or `Asynchronous`. |
| `priorityLimit​Action` | string | Type of action to perform when the priority limit is reached. Valid values are `Reject` or `Downgrade`. This parameter is applicable only when you specify the `fulfillmentPriority` parameter. |
| `sales​TransactionId` | id | Required. ID of the sales transaction to submit. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `errorCode` | string | Code that corresponds to the type of error encountered. |
| `requested​FulfillmentPriority` | string | Priority to fulfill the sales transaction. Valid values are `High`, `Bulk`, or `Default`. |
| `requestId` | string | Request ID of the invocation. |
| `resolved​FulfillmentPriority` | string | Resolved priority to fulfill the sales transaction. Valid values are `High`, `Bulk`, or `Default`. |
| `submitStatus` | string | Submission status of the sales transaction for decomposition. Valid values are `Success`, `Error`, `Submitted`, or `Rejected`. |
| `usedContextId` | string | ID of the used context that updates the decomposition process. |

## Example

**POST**

This sample request is for the Decompose Sales Transaction action.

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

This sample response is for the Decompose Sales Transaction action.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-decompose-sales-transaction.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
