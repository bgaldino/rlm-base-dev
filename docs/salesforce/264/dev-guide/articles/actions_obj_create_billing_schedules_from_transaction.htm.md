---
page_id: actions_obj_create_billing_schedules_from_transaction.htm
title: Create Standalone Billing Schedules Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_create_billing_schedules_from_transaction.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-11-23
---

# Create Standalone Billing Schedules Action

Creates billing schedules for internal or external transaction records by calling the Create Standalone Billing Schedules API.

This action is available in API version 64.0 and later.

See [Create Standalone Billing Schedules (POST) API](./connect_resources_create_billing_schedules_from_any_transaction.htm.md "HTML (New Window)") to know more about the mandatory and optional tags, sample transaction details, and sample payloads for various types of transactions.

## Special Access Rules

This action is available in Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. To use this action, you need the Billing Operations permission set.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/createBillingSchedulesFromTrxn`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer token`

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| contextDefinitionName | string | Required. Name of the context definition that contains the mappings for the transaction record and billing schedules. |
| executeAsync | boolean | Optional. Indicates whether to process the request asynchronously (`true`). The default value is `false` (synchronous). Available in API version 68.0 and later. |
| readContextMappingName | string | Required. Name of the context mapping with the mapping for the transaction. |
| saveContextMappingName | string | Required. Name of the context mapping with the mapping for the billing schedule and billing schedule group. The save context mapping is used to save the billing schedule. |
| transactionDetails | string | Required. A JSON string containing the ID of the transaction record that the billing schedule is created for and other additional transaction details. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| requestId | string | Unique request identifier that you can use to poll the asynchronous request. |
| statusUrl | string | Status URL that’s used to track the operation. |

## Example

**POST**

Here's a sample request for the Create Billing Schedules From Transaction action.

```
{
  "inputs": [
    {
      "transactionDetails": "{\"Transaction\":[{\"id\":\"sampleA1\",\"ParentTransactionId\":\"sample\",\"TransactionId\":\"sampleA1\",\"RelatedTransactionId\":\"ter1\",\"StartDate\":\"2025-04-01\",\"UnitPrice\":10,\"Quantity\":1,\"TotalPrice\":90,\"BillingActionType\":\"Amend\"},{\"id\":\"sampleA2\",\"ParentTransactionId\":\"sample\",\"TransactionId\":\"sampleA2\",\"RelatedTransactionId\":\"ter1\",\"StartDate\":\"2025-03-01\",\"UnitPrice\":10,\"Quantity\":-2,\"TotalPrice\":-200,\"BillingActionType\":\"Amend\"},{\"id\":\"sampleA3\",\"ParentTransactionId\":\"sample\",\"TransactionId\":\"sampleA3\",\"RelatedTransactionId\":\"ter1\",\"StartDate\":\"2025-03-01\",\"UnitPrice\":10,\"Quantity\":-1,\"TotalPrice\":-100,\"BillingActionType\":\"Amend\"}]}",
      "contextDefinitionName": "StandaloneBillingContext__stdctx",
      "readContextMappingName": "TransactionMapping",
      "saveContextMappingName": "BSGEntitiesMapping"
    }
  ]
}
```

Here's a sample response for the Create Billing Schedules From Transaction action.

```
{
  "actionName": "createBillingSchedulesFromTrxn",
  "errors": null,
  "isSuccess": true,
  "outputValues": {
    "requestId": "16PZ6000000CnKRMA0",
    "statusUrl": "/services/data/v64.0/sobjects/AsyncOperationTracker/16PZ6000000CnKRMA0"
  },
  "sortOrder": -1,
  "version": 1
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_create_billing_schedules_from_transaction.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
