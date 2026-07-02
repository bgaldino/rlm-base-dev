---
page_id: connect_requests_credit_memo_apply_input.htm
title: Credit Memo Apply Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_credit_memo_apply_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Credit Memo Apply Input

Input representation of the request to apply a credit memo to an invoice.

JSON example
:   ```
    {
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
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `applications` | [Credit Memo Apply Application Input](./connect_requests_credit_memo_apply_application_input.htm.md "Input representation of the request to specify one or more applications to apply a credit memo for, with each application representing an invoice.")[] | List of one or more applications to apply the credit memo for. Each application represents an invoice that’s credited by using the balance of the specified credit memo. | Required | 62.0 |
