---
page_id: connect_responses_invoice_preview_output.htm
title: Invoice Preview Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_invoice_preview_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Invoice Preview Result

Output representation of the list of preview invoices that are generated for the billing transaction.

JSON example
:   ```
    {
      "invoiceDetailList": [
        {
          "accountId": "001Z6000005aQj8",
          "currencyIsoCode": "USD",
          "dueDate": "2025-01-03",
          "invoiceDate": "2024-12-04",
          "invoiceLineDetailList": [
            {
              "billingFrequency": "OneTime",
              "chargeAmount": "1990.00",
              "endDate": "2024-07-18",
              "lineAmount": "2189.00",
              "productName": "Laptop",
              "quantity": "10.0",
              "startDate": "2024-07-18",
              "taxAmount": "199.0",
              "unitPrice": "199.0"
            }
          ],
          "totalAmount": "1990.00",
          "totalAmountWithTax": "2189.00",
          "totalTaxAmount": "199.0"
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `invoice​Detail​List` | [Invoice Preview](./connect_responses_prev_inv_output.htm.md "Output representation of the invoice preview result.")[] | Details of the invoices that are generated for the billing transaction. | Big, 63.0 | 63.0 |
