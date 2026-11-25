---
page_id: connect-responses-batch-invoice-scheduler-output
title: Batch Invoice Scheduler
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-batch-invoice-scheduler-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_batch_invoice_scheduler_output.htm
fetched_at: 2026-11-25
---

# Batch Invoice Scheduler

Output representation of the details of an invoice scheduler.

## JSON Example

```
{
    "billingBatchScheduler": {
        "id": "5BSxx0000004TwGGAU"
    }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `billing​Batch​Scheduler` | [Billing Batch Scheduler](./connect-responses-billing-batch-scheduler.md)[] | Details of the created invoice scheduler. | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-batch-invoice-scheduler-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
