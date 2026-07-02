---
page_id: connect_requests_credit_memo_unapply_input.htm
title: Credit Memo Unapply Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_credit_memo_unapply_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Credit Memo Unapply Input

Input representation of the request to unapply a credit memo from an invoice.

JSON example
:   ```
        {
          "description": "Unapply credit memo from invoice to revert an error",
          "effectiveDate": "2024-07-01"
        }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `description` | String | Explanation or reason for unapplying the credit memo. | Optional | 62.0 |
    | `effectiveDate` | String | Effective date for the credit memo. | Optional | 62.0 |
