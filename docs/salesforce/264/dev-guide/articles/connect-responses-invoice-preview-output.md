---
page_id: connect-responses-invoice-preview-output
title: Invoice Preview Result
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-invoice-preview-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_invoice_preview_output.htm
fetched_at: 2026-11-25
---

# Invoice Preview Result

Output representation of the list of preview invoices that are generated for the billing transaction.

## JSON Example

```
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
| `invoice​Detail​List` | [Invoice Preview](./connect-responses-prev-inv-output.md)[] | Details of the invoices that are generated for the billing transaction. | Big, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-invoice-preview-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
