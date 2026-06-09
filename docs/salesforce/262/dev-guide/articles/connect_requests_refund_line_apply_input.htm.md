---
page_id: connect_requests_refund_line_apply_input.htm
title: Refund Line Apply Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_refund_line_apply_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Refund Line Apply Input

Input representation of the details of a transaction refund request. This representation
outlines the properties of a refund, including the refund amount and ID of the payment or credit
memo record that the refund is applied to.

JSON example
:   ```
    {
      "appliedToId": "0aQR00000004ZkKMAU",
      "amount": 10,
      "effectiveDate": "2020-08-11T07:53:15.000Z",
      "comments": "Payment application."
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `amount` | Double | Amount to refund. | Required | 64.0 |
    | `appliedToId` | String | ID of a payment or credit memo record. The refund is applied to this object. | Required | 64.0 |
    | `comments` | String | Additional details of the refund request. | Optional | 64.0 |
    | `effectiveDate` | String | Date from when the refund is in effect. | Optional | 64.0 |
