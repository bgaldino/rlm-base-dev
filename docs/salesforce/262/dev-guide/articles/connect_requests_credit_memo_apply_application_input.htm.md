---
page_id: connect_requests_credit_memo_apply_application_input.htm
title: Credit Memo Apply Application Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_credit_memo_apply_application_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Credit Memo Apply Application Input

Input representation of the request to specify one or more applications to apply a credit
memo for, with each application representing an invoice.

JSON example
:   ```
      "applications": [
        {
          "appliedToId": "3ttxx000000003FAAQ",
          "amount": 10,
          "description": "Apply to invoice for refund",
          "effectiveDate": "2024-07-01"
        },
        {
          "appliedToId": "3ttxx0000000001AAA",
          "amount": 100
        }
      ]
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `amount` | Double | Credit amount to be applied to the invoice. | Required | 62.0 |
    | `appliedToId` | String | ID of the invoice record to apply the credit for. | Required | 62.0 |
    | `description` | String | Explanation or reason for applying the credit memo. | Optional | 62.0 |
    | `effectiveDate` | String | Effective date for the credit memo. | Optional | 62.0 |
