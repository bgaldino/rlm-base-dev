---
page_id: connect_resources_create_and_apply_a_credit_memo.htm
title: Create and Apply Credit Memo (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_and_apply_a_credit_memo.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Create and Apply Credit Memo (POST)

Create a credit memo and apply it to an invoice. The credit memo can
fully or partially credit the invoice.

Use this API to adjust an outstanding invoice balance or rectify errors in an
invoice. In the API request, pass a list of invoice lines to credit. Keep these
considerations in mind when you use this API.

- The request must contain at least one invoice line. Each invoice line must have the
  invoice line’s ID, the amount to credit, and any optional tax details. The invoice lines
  must be a part of the invoice passed in the resource.
- The amount to credit must not exceed the charge or adjustment amount of an individual
  invoice line.
- The request body's credit amount inclusive of taxes must not exceed the target invoice
  line's amount inclusive of taxes, except for taxes calculated through an external tax
  service.
- The request body's total credit amount inclusive of taxes calculated through an external
  tax service must not exceed the outstanding invoice balance, which is also inclusive of
  taxes.

This API creates and posts a credit memo. The credit memo has one credit memo line for each
invoice line passed in the API request. The invoice balance reduces by a value equal to the
credit memo’s balance. This API modifies the balance of a posted invoice or invoice line
based on the specified credit application level for your org. See [Apply Credits to Posted Invoices or
Invoice Lines](https://help.salesforce.com/s/articleView?id=sf.billing_setup_credit_application_level.htm&language=en_US "HTML (New Window)").

Special Access Rules
:   You need the Credit Memo Operations User permission set to use this API.

Resource
:   ```
    /commerce/invoicing/invoices/invoiceId/actions/credit
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/invoicing/invoices/3ttR000000008NEIAY/actions/credit
    ```

Available version
:   62.0

HTTP methods
:   POST

Path parameter for POST
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `invoice​Id` | String | ID of the invoice to be credited partially or fully. The status of the invoice must be `Posted`. | Required | 62.0 |

Request body for POST
:   JSON example
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

Response body for POST
:   [Revenue Async Line
    Level](./connect_responses_revenue_async_line_level.htm.md "Output representation of the result of the API request for the async line level operations.")
