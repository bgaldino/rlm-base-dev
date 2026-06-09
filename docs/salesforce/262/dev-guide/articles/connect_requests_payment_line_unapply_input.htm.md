---
page_id: connect_requests_payment_line_unapply_input.htm
title: Payment Line Unapply Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_payment_line_unapply_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Payment Line Unapply Input

Input representation of the payment line details. This representation covers fields that
you can specify to revert a payment line application to their preapplication state.

JSON example
:   ```
    {
      "effectiveDate": "2025-05-22T11:30:25.000Z",
      "comments": "Unapply payment"
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `comments` | String | Comments that you can add when you revert a payment line application. | Optional | 64.0 |
    | `effective​Date` | String | Date from when the reversal of the payment line application is in effect. | Optional | 64.0 |
