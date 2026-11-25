---
page_id: connect-requests-billing-schedule-recovery-input
title: Billing Schedule Recovery Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-billing-schedule-recovery-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_billing_schedule_recovery_input.htm
fetched_at: 2026-11-25
---

# Billing Schedule Recovery Input

Input representation of the details of the billing schedules to recover the associated invoice.

## JSON Example

```
  {
    "billingScheduleIds": ["44bDU00000000XXYAY"]
  }
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billing​Schedule​Ids` | String[] | IDs of the billing schedules to recover the invoice for. You can recover one billing schedule per API request. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-billing-schedule-recovery-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
