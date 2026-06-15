---
page_id: connect_responses_payment_scheduler_update_output.htm
title: Payment Scheduler Update
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_payment_scheduler_update_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Payment Scheduler Update

Output representation of the details of the updated payment scheduler. This
representation covers the updated status value of the specified payment scheduler.

JSON example
:   ```
    {
      "status": "Active"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `status` | String | Updated status value of the specified payment scheduler. Valid values are:   - `Active` - `Canceled` - `Draft` - `Inactive` | Big, 64.0 | 64.0 |
