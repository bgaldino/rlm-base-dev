---
page_id: connect_resources_update_payment_scheduler.htm
title: Payment Scheduler Update (PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_update_payment_scheduler.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-11-23
---

# Payment Scheduler Update (PATCH)

Activate or deactivate a payment scheduler. You can set the status of a payment scheduler to `Active`, `Canceled`, `Draft`, or `Inactive`.

## Special Access Rules

You need the Payment Ops permission set to use this API.

## Resource

```
/commerce/payments/payment-schedulers/billingBatchSchedulerId
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/payments/payment-schedulers/5BSxx0000004TwGGAU
```

## Available Version

64.0

## HTTP Methods

PATCH

## Path Parameter for POST

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billingBatch​SchedulerId` | String | ID of the payment scheduler record. | Required | 64.0 |

## Request Body for PATCH

**JSON Example**

**JSON Example**

```
{
  "status": "Active"
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `status` | String | Status that must be set to activate or deactivate a payment scheduler. | Required | 64.0 |

Valid values are:

- `Active`
- `Canceled`
- `Draft`
- `Inactive`

## Response Body for PATCH

[Payments Scheduler Update](./connect_responses_payment_scheduler_update_output.htm.md "Output representation of the details of the updated payment scheduler. This representation covers the updated status value of the specified payment scheduler.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_update_payment_scheduler.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
