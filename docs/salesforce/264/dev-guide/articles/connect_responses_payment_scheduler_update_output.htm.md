---
page_id: connect_responses_payment_scheduler_update_output.htm
title: Payment Scheduler Update
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_payment_scheduler_update_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Payment Scheduler Update

Output representation of the details of the updated payment scheduler. This representation covers the updated status value of the specified payment scheduler.

## JSON Example

```
{
  "status": "Active"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `status` | String | Updated status value of the specified payment scheduler. | Big, 64.0 | 64.0 |

Valid values are:

- `Active`
- `Canceled`
- `Draft`
- `Inactive`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_payment_scheduler_update_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
