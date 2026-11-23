---
page_id: connect_responses_billing_schedule_recovery_output.htm
title: Billing Schedule Recovery
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_billing_schedule_recovery_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Billing Schedule Recovery

Output representation of the details of the recovered billing schedules.

## JSON Example

```
    "billingSchedules": [
        {
          "billingScheduleId": "44bDU00000000XX",
          "billingScheduleStatus": "ReadyForInvoicing"
        }
    ]
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `billing​Schedule​Id` | String | ID of the billing schedule. | Big, 62.0 | 62.0 |
| `billing​Schedule​Status` | String | Flag that indicates the billing schedule status. | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_billing_schedule_recovery_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
