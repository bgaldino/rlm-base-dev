---
page_id: connect-responses-billing-schedule-recovery-list-output
title: Billing Schedule Recovery List
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-billing-schedule-recovery-list-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_billing_schedule_recovery_list_output.htm
fetched_at: 2026-11-25
---

# Billing Schedule Recovery List

Output representation of the recovered details of the billing schedules and associated invoice.

## JSON Example

```
{
  "recoveryResults": [
    {
      "billingSchedules": [
        {
          "billingScheduleId": "44bDU00000000XX",
          "billingScheduleStatus": "ReadyForInvoicing"
        }
      ],
      "invoiceErrors": [],
      "invoiceId": null,
      "success": true
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `recovery​Results` | [Invoice Recovery](./connect-responses-invoice-recovery-output.md)[] | Details of the recovered invoice and billing schedules. | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-billing-schedule-recovery-list-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
