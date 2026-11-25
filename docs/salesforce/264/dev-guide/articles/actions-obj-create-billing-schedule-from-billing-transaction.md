---
page_id: actions-obj-create-billing-schedule-from-billing-transaction
title: Create Billing Schedules From Billing Transaction Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-create-billing-schedule-from-billing-transaction.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-invocable-actions-parent
legacy_page_id: actions_obj_create_billing_schedule_from_billing_transaction.htm
fetched_at: 2026-11-25
---

# Create Billing Schedules From Billing Transaction Action

Create one or more billing schedules for a specified billing transaction ID.

This action calls the [Create Billing Schedules for Orders (POST) API](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_billing_schedules.htm) to retrieve the billing transaction items associated with the billing transaction ID. The API generates the corresponding billing schedules for each of the billing transaction items for operations such as transaction modifications, renewals, cancellations, and new sales.

This action is available in API version 62.0 and later.

## Special Access Rules

The Create Billing Schedules From Billing Transaction action is available in Enterprise, Unlimited, and Developer Editions where Billing is enabled. To use this action, you need the Create Billing Schedules From Billing Transactions API permission set.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/createBillingSchedulesFromBillingTransaction`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `billingTransactionId` | string | Required. ID of the billing transaction record to create one or more billing schedules for. This action supports only one billing transaction ID in the input. |

**Note:**

When a flow, such as the Order To Billing Schedule flow, is triggered for multiple orders at the same time, Salesforce Flow bulkifies the action calls into a single invocation. Because this action accepts only one billing transaction ID per request, the call fails. To avoid this error, invoke this action separately for each order or billing transaction ID. For example, use a Loop element to iterate over the records before calling this action.

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `requestId` | string | Universally Unique Identifier (UUID) that’s used to track the status of the asynchronous action. |
| `statusUrl` | string | URL that’s used to check the status of the API request. |

## Example

**POST**

This example shows a sample request for the Create Billing Schedules From Billing Transaction action.

```
{
  "inputs": [
    {
      "billingTransactionId": "801xx000003JztvAAC"
    }
  ]
}
```

This example shows a sample response for the Create Billing Schedules From Billing Transaction action.

```
{
  "actionName": "createBillingSchedulesFromBillingTransaction",
  "errors": null,
  "isSuccess": true,
  "outputValues": {
    "requestId": "4sFDU00000000652AA",
    "statusUrl": "/services/data/v62.0/sobjects/AsyncOperationTracker/16Pxx0000004NhAEAU"
  },
  "sortOrder": -1,
  "version": 1
}
```

**See Also**

- [*Revenue Cloud Developer Guide*: Context-Aware Billing Schedule API](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_billing_schedules.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-create-billing-schedule-from-billing-transaction.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
