---
page_id: connect_requests_write_off_posted_invoice_list_input.htm
title: Posted Invoice List Write-Off Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_write_off_posted_invoice_list_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Posted Invoice List Write-Off Input

Input representation of the request to write off a list of posted invoices. This
representation includes the details of invoices that you want to write off.

JSON example
:   ```
    {
      "invoices": [
        {
          "invoiceId": "3ttxx00000000cjAAA",
          "reasonCode": "Bad Debt",
          "description": "Bad Debt"
        },
        {
          "invoiceId": "3ttxx00000000cjAAA",
          "reasonCode": "Concession",
          "description": "Concession"
        }
      ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `invoices` | [Posted Invoice Write-Off Input](./connect_requests_write_off_posted_invoice_input.htm.md "Input representation of the details of the request to write off a posted invoice. This representation includes invoice details such as invoice ID and reason for writing off invoices.")[] | Details of the invoices that you want to write off. | Required | 64.0 |
