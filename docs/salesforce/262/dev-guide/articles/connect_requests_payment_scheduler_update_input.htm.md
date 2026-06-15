---
page_id: connect_requests_payment_scheduler_update_input.htm
title: Payment Scheduler Update Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_payment_scheduler_update_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Payment Scheduler Update Input

Input representation of the details of the request to update the status of a payment
scheduler. This representation defines the status of a payment scheduler, which can be set to
Active, Canceled, Draft, or Inactive.

JSON example
:   JSON example
    :   ```
        {
          "status": "Active"
        }
        ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `status` | String | Status that must be set to activate or deactivate a payment scheduler. Valid values are:   - `Active` - `Canceled` - `Draft` - `Inactive` | Required | 64.0 |
