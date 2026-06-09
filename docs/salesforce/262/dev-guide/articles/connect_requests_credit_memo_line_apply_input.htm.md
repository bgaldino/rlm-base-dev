---
page_id: connect_requests_credit_memo_line_apply_input.htm
title: Credit Memo Line Apply Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_credit_memo_line_apply_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Credit Memo Line Apply Input

Input representation of the details of the request to apply a credit memo line to an
invoice line.

JSON example
:   ```
    {
     "applyCreditDetails": [
     {
     "invoiceLineId": "5TVSG0000002ZJR4A2",
     "appliedAmount": 5,
     "description": "Apply to invoice line 1",
     "effectiveDate": "2024-07-01"
     },
     {
     "invoiceLineId": "5TVSG0000002ZJS4A2",
     "appliedAmount": 10,
     "description": "Apply to invoice line 2",
     "effectiveDate": "2024-07-01"
     }
     ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `applyCredit​Details` | [Credit Memo Line Application Input](./connect_requests_credit_memo_line_application_input.htm.md "Input representation of the request to specify one or more applications to apply a credit memo line for, with each application representing an invoice line.")[] | List of one or more applications to apply the credit memo line for. Each application represents an invoice line that’s credited by using the balance of the specified credit memo line. | Required | 62.0 |
