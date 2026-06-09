---
page_id: connect_requests_credit_invoice_input.htm
title: Credit Invoice Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_credit_invoice_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Credit Invoice Input

Input representation of the details of the request to create a credit memo.

JSON example
:   This example shows a sample request with the `Calculate` tax
    strategy.

    ```
    {
      "type": "POSTED",
      "taxStrategy": "Calculate",
      "taxEffectiveDate": "2024-07-20",
      "effectiveDate": "2024-07-20",
      "description": "Credit Invoice",
      "invoiceLines": [
        {
          "invoiceLineId": "5TVR00000004SiqOBE",
          "amountToCredit": 5
        }
      ]
    }
    ```
:   This example shows a sample request with the `CopyFromInvoiceLine` tax
    strategy.

    ```
    {
      "type": "POSTED",
      "taxStrategy": "CopyFromInvoiceLine",
      "effectiveDate": "2020-05-22",
      "description": "Credit Invoice",
      "invoiceLines": [
        {
          "invoiceLineId": "5TVR00000004SiqOBE",
          "amountToCredit": "5",
          "taxStrategy": "CopyFromInvoiceLine"
        }
      ]
    }
    ```
:   This example shows a sample request with the `ManualOverride` and `CopyFromInvoiceLine`
    tax strategies.

    ```
    {
      "type": "POSTED",
      "taxStrategy": "ManualOverride",
      "taxEffectiveDate": "2021-08-01",
      "effectiveDate": "2021-08-01",
      "description": "Credit issued because product was malfunctioning.",
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
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `description` | String | Description for the credit memo to be created. | Optional | 62.0 |
    | `effective​Date` | String | Date when the credit memo takes effect. | Optional | 62.0 |
    | `invoice​Lines` | [Credit Invoice Line Input](./connect_requests_credit_invoice_line_input.htm.md "Input representation of the details of the invoice lines to be credited.")[] | List of the invoice lines to be credited. The invoice line IDs must be related to the invoice ID specified in the API request. If invoice lines aren’t specified, the API request results in an error. | Required | 62.0 |
    | `taxEffective​Date` | String | Date when the tax takes effect to recalculate the taxes. | Optional | 62.0 |
    | `tax​Strategy` | String | Tax strategy to be applied across invoice lines. You can override the tax strategy at the individual invoice line level or at the tax line level. Valid values are:   - `Ignore`—Specifies that the   creation of tax lines must be ignored. - `ManualOverride`—Specifies that the provided tax values must be   considered for taxes. - `CopyFromInvoiceLine`—Specifies   that tax values must be copied from the invoice line. - `Calculate`—Specifies that tax   must be calculated by using the API. | Required | 62.0 |
    | `type` | String | Type of credit memo to be created. Valid values are `Posted` and `Draft`. Specify `Draft` as a value in your request to create draft credit memos. | Optional | 62.0 |
