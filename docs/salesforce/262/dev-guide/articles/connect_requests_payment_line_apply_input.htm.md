---
page_id: connect_requests_payment_line_apply_input.htm
title: Payment Line Apply Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_payment_line_apply_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Payment Line Apply Input

Input representation of the payment line details. This representation
covers details on allocation of a payment to a specific invoice line. It also provides
additional context through optional fields such as associated account and effective
date.

JSON example
:   ```
    {
      "appliedToId": "3ttR000000001IkIAI",
      "amount": 10,
      "effectiveDate": "2020-08-11T07:53:15.000Z",
      "comments": "Apply payment",
      "associatedAccountId": "001R00000060AyuIAE"
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `amount` | Double | Amount that's applied. The amount must be less than the invoice line and payment balance. | Required | 64.0 |
    | `applied​ToId` | String | ID of the invoice line that this payment is applied to. Specify the IDs for these records.   - Invoice - Invoice Line | Required | 64.0 |
    | `associated​AccountId` | String | ID of the associated account. | Optional | 64.0 |
    | `comments` | String | Comments that you can add to the payment line application. | Optional | 64.0 |
    | `effective​Date` | String | Date from which the payment line application takes effect. | Optional | 64.0 |
