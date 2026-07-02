---
page_id: connect_responses_prev_inv_line_output.htm
title: Invoice Line Preview
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_prev_inv_line_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Invoice Line Preview

Output representation of the invoice line preview result.

JSON example
:   ```
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
          ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `billing​Frequency` | String | The frequency at which the invoice line is created for the billing transaction. | Big, 63.0 | 63.0 |
| `endDate` | String | The end date of the billing for the service for invoice lines made from a time-based service. | Big, 63.0 | 63.0 |
| `line​Amount` | String | The amount of the invoice line. | Big, 63.0 | 63.0 |
| `product​Name` | String | The name of the product that was charged or ordered to create the invoice line. | Big, 63.0 | 63.0 |
| `quantity` | String | The number of units of the order product that created the invoice line. | Big, 63.0 | 63.0 |
| `startDate` | String | The first date of the billing for the service for invoice lines made from a time-based service. | Big, 63.0 | 63.0 |
| `taxAmount` | String | The tax amount for the invoice line. | Big, 63.0 | 63.0 |
| `unitPrice` | String | The price for one unit of the item on the invoice line. | Big, 63.0 | 63.0 |
