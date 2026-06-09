---
page_id: connect_responses_batch_invoice_scheduler_output.htm
title: Batch Invoice Scheduler
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_batch_invoice_scheduler_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Batch Invoice Scheduler

Output representation of the details of an invoice scheduler.

JSON example
:   ```
    {
        "billingBatchScheduler": {
            "id": "5BSxx0000004TwGGAU"
        }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `billing​Batch​Scheduler` | [Billing Batch Scheduler](./connect_responses_billing_batch_scheduler.htm.md "Output representation of the details of a created invoice or payment scheduler.")[] | Details of the created invoice scheduler. | Big, 62.0 | 62.0 |
