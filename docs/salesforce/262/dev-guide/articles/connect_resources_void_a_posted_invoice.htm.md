---
page_id: connect_resources_void_a_posted_invoice.htm
title: Void a Posted Invoice (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_void_a_posted_invoice.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Void a Posted Invoice (POST)

Void a posted invoice to rebill the customer, if
necessary.

This API request changes the invoice status from `Posted` to `Void In Progress`. The invoice
remains in the `Void In Progress` status until the credit
is applied and financial fields are recalculated on the invoice’s related billing period
items and billing schedule. The invoice status changes to `Voided` after all recalculations are completed.

Keep these considerations in mind when you use this API.

- The balance and total amount on the invoice must be equal. If these amounts aren’t equal
  due to payments or credits, the API request fails.
- You can’t call other APIs on an invoice with the `Void In
  Progress` status. You also can’t update the invoice fields.
- You can void only the most recently posted invoice on a billing schedule.
- To void an invoice that has payments or credits, use the [Credit Memo
  Unapply (POST)](https://developer.salesforce.com/docs/./connect_resources_credit_memo_invoice_application_unapply.htm.md "HTML (New Window)")  API.

Credit Memos
:   The void process creates a credit memo, which contains one credit memo line for each
    invoice line, including tax lines. For example, if the invoice line has a balance of
    US$20, the related credit memo line has a balance of $20. The credit memo’s balance is
    then allocated to the invoice header’s balance, reducing it to zero. A credit memo
    invoice application is created to record the details of the void process.

Negative Invoice Lines
:   If an invoice has negative invoice lines that aren’t converted to a credit memo, you
    can use this endpoint to void the posted invoice.

Special Access Rules
:   You need the Void a Posted Invoice API permission set to use this API.

Resource
:   ```
    /commerce/invoicing/invoices/invoiceId/actions/void
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/invoicing/invoices/3ttxx00000000XtAAI/actions/void
    ```

Available version
:   62.0

HTTP methods
:   POST

Path parameter for POST
:   Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `invoiceId` | String | ID of the posted invoice to be voided. | Required | 62.0 |

Response body for POST
:   [Revenue Async
    Response](./connect_responses_revenue_async_output.htm.md "Output representation of the result of the API request with the request identifier.")
