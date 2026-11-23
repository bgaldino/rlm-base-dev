---
page_id: connect_responses_payment_line_apply_output.htm
title: Payment Line Apply
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_payment_line_apply_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Payment Line Apply

Output representation of the details of the applied payment line. The details include the ID of the payment record and date when the payment line was applied.

## JSON Example

```
{
  "appliedDate": "2020-08-11T08:09:01.000Z",
  "id": "1PLR000000000dDOAQ"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `applied​Date` | String | Date when the payment line was applied. | Big, 64.0 | 64.0 |
| `id` | String | ID of the payment line record. | Big, 64.0 | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_payment_line_apply_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
