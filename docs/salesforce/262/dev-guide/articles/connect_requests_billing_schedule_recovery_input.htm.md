---
page_id: connect_requests_billing_schedule_recovery_input.htm
title: Billing Schedule Recovery Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_schedule_recovery_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Billing Schedule Recovery Input

Input representation of the details of the billing schedules to recover the associated
invoice.

JSON example
:   ```
      {
        "billingScheduleIds": ["44bDU00000000XXYAY"]
      }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `billing​Schedule​Ids` | String[] | IDs of the billing schedules to recover the invoice for. You can recover one billing schedule per API request. | Required | 62.0 |
