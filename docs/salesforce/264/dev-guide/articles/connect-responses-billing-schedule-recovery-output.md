---
page_id: connect-responses-billing-schedule-recovery-output
title: Billing Schedule Recovery
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-billing-schedule-recovery-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_billing_schedule_recovery_output.htm
fetched_at: 2026-11-25
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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-billing-schedule-recovery-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
