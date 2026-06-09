---
page_id: connect_requests_credit_invoice_line_input.htm
title: Credit Invoice Line Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_credit_invoice_line_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Credit Invoice Line Input

Input representation of the details of the invoice lines to be credited.

JSON example
:   ```
      "invoiceLines": [
        {
          "invoiceLineId": "5TVR00000004SiqOBE",
          "amountToCredit": 100,
          "taxStrategy": "ManualOverride",
          "taxEffectiveDate": "2021-08-01T21:22:41.000Z",
          "taxes": [
            {
              "taxAmount": 15,
              "taxName": "abc",
              "taxCode": "taxCode",
              "taxRate": 7
            }
          ],
          "addresses": {
            "billingAddress": {
              "street": "1 Market St #300",
              "city": "San Francisco",
              "state": "CA",
              "country": "US",
              "postalCode": "94105",
              "latitude": "37.789901",
              "longitude": "-122.396923"
            },
            "shippingAddress": {
              "street": "415 Mission St",
              "city": "San Francisco",
              "state": "CA",
              "country": "US",
              "postalCode": "94105",
              "latitude": "37.789901",
              "longitude": "-122.396923"
            }
          }
        },
        {
          "invoiceLineId": "5TVR00000004SiqOAE",
          "amountToCredit": 200,
          "taxStrategy": "CopyFromInvoiceLine"
        }
      ]
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `addresses` | [Credit Memo Addresses Input](./connect_requests_credit_memo_addresses_input.htm.md "Input representation of the details of the billing and shipping addresses.")[] | Addresses to be created manually for this invoice line and the overridden tax lines. These addresses are only applicable if this invoice line is using the `ManualOverride` tax strategy. | Optional | 62.0 |
    | `amountTo​Credit` | Double | Amount to be credited from this invoice line. | Required | 62.0 |
    | `invoice​LineId` | String | ID of the invoice line record to be credited. The invoice line ID must be related to the invoice ID specified in the API request. | Required | 62.0 |
    | `isTaxOnly​Credit` | Boolean | Indicates whether the applicable tax amount is credited for the charge or adjustment amount (`true`), or the applicable tax amount is credited along with the charge or adjustment amount (`false`). The default value is `false`. | Optional | 62.0 |
    | `taxEffective​Date` | String | Date when the tax takes effect and the invoice line is credited. | Optional | 62.0 |
    | `tax​Strategy` | String | Tax strategy for crediting the invoice line. This tax strategy takes precedence over the `taxStrategy` property value specified in the [Credit Invoice Input](./connect_requests_credit_invoice_input.htm.md "Input representation of the details of the request to create a credit memo."). Valid values are:   - `Ignore`—Specifies that the   creation of tax lines must be ignored. - `ManualOverride`—Specifies that the provided tax values must be   considered for taxes. - `CopyFromInvoiceLine`—Specifies   that tax values must be copied from the invoice line. - `Calculate`—Specifies that tax   must be calculated by using the API. | Optional | 62.0 |
    | `taxes` | [Credit Invoice Line Tax Input](./connect_requests_credit_invoice_line_tax_input.htm.md "Input representation of the details of the tax lines to be created manually for the invoice line.")[] | List of tax lines to be created manually for this invoice line. | Required if the `taxStrategy` property value is `ManualOverride`. | 62.0 |
