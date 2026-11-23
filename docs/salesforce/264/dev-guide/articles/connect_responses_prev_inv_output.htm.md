---
page_id: connect_responses_prev_inv_output.htm
title: Invoice Preview
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_prev_inv_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Invoice Preview

Output representation of the invoice preview result.

## JSON Example

```
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
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `accountId` | String | The account ID of the billing transaction. | Big, 63.0 | 63.0 |
| `currency​Code` | String | The currency code for the amount fields. | Big, 63.0 | 63.0 |
| `dueDate` | String | The date by when the customer must pay an invoice that’s generated for the billing transaction. | Big, 63.0 | 63.0 |
| `invoiceDate` | String | The date when an invoice that’s generated for the billing transaction is posted. | Big, 63.0 | 63.0 |
| `invoiceLines` | [Invoice Line Preview](./connect_responses_prev_inv_line_output.htm.md "Output representation of the invoice line preview result.")[] | The details of the invoice lines related to the invoices that are generated for the billing transaction. | Big, 63.0 | 63.0 |
| `totalAmount` | String | The sum of the total amount on the invoice lines of an invoice that’s generated for the billing transaction. | Big, 63.0 | 63.0 |
| `total​Amount​WithTax` | String | The sum of the total amount including tax on the invoice lines of an invoice that’s generated for the billing transaction. | Big, 63.0 | 63.0 |
| `totalTax​Amount` | String | The sum of the tax amount on the invoice lines of an invoice that’s generated for the billing transaction. | Big, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_prev_inv_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
