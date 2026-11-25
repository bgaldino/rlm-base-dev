---
page_id: actions-obj-orchestrate-transaction
title: Orchestrate Transaction Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-orchestrate-transaction.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-invocable-actions-parent
legacy_page_id: actions_obj_orchestrate_transaction.htm
fetched_at: 2026-11-25
---

# Orchestrate Transaction Action

Orchestrate a transaction for any domain-specific object, such as a collection plan for Revenue billing, that requires the composition and execution of a fulfillment plan.

Specify the ID of the transaction to orchestrate and the orchestration type. The orchestration process includes:

- Composition of the orchestration plan

- Execution of the fulfillment plan

This action is available in API version 66.0 and later.

## Special Access Rules

The Orchestrate Transaction action is available in Enterprise, Unlimited, and Developer Editions of Revenue Management. See the [required permissions](https://help.salesforce.com/s/articleView?id=sf.dro_permission_sets_in_dynamic_revenue_orchestrator.htm) to access and call this invocable action.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/orchestrateTransaction`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `transactionId` | string | Required. ID of the business object or domain object to be orchestrated, such as a Collection Plan ID. |
| `orchestration​Type` | string | Required. Type of orchestration that’s used to orchestrate the transaction. Valid values are `Generic`, `Fulfillment`, or `Billing`. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `requestId` | string | Request ID of the invocation. |
| `errorCode` | string | Code that corresponds to the type of encountered error. |
| `fulfillment​PlanId` | string | ID of the composed fulfillment plan. |
| `submitStatus` | string | Submission status of the transaction that’s orchestrated. Valid values are `Success` or `Error`. |

## Example

**POST**

This sample request is for the Orchestrate Transaction action.

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

This sample response is for the Orchestrate Transaction action.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-orchestrate-transaction.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
