---
page_id: apex_connectapi_input_payment_line_apply.htm
title: ConnectApi.PaymentLineApplyRequest
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_payment_line_apply.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.PaymentLineApplyRequest

Input representation of the payment line details. This representation covers details on
allocation of a payment to a specific invoice line. It also provides additional context through
optional fields, such as associated account and effective date.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `amount` | Double | Amount that's applied. The amount must be less than the invoice line and payment balance. | Required | 64.0 |
| `applied​ToId` | String | ID of the invoice line that this payment is applied to. Specify the IDs for these records.   - Invoice - Invoice Line | Required | 64.0 |
| `associated​AccountId` | String | ID of the associated account. | Optional | 64.0 |
| `comments` | String | Comments that you can add to the payment line application. | Optional | 64.0 |
| `effective​Date` | Datetime | Date from which the payment line application takes effect. | Optional | 64.0 |
