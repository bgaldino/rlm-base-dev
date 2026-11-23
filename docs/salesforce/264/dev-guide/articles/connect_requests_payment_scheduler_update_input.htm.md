---
page_id: connect_requests_payment_scheduler_update_input.htm
title: Payment Scheduler Update Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_payment_scheduler_update_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-11-23
---

# Payment Scheduler Update Input

Input representation of the details of the request to update the status of a payment scheduler. This representation defines the status of a payment scheduler, which can be set to Active, Canceled, Draft, or Inactive.

## JSON Example

**JSON Example**

```
{
  "status": "Active"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `status` | String | Status that must be set to activate or deactivate a payment scheduler. | Required | 64.0 |

Valid values are:

- `Active`
- `Canceled`
- `Draft`
- `Inactive`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_payment_scheduler_update_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
