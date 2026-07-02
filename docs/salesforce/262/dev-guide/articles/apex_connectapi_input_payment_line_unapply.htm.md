---
page_id: apex_connectapi_input_payment_line_unapply.htm
title: ConnectApi.PaymentLineUnapplyRequest
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_payment_line_unapply.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.PaymentLineUnapplyRequest

Input representation of the payment line details. This representation covers fields that
you can specify to revert a payment line application.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `comments` | String | Comments that you can add when you revert a payment line application. | Optional | 64.0 |
| `effective​Date` | Datetime | Date from when the reversal of the payment line application is in effect. | Optional | 64.0 |
