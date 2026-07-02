---
page_id: connect_resources_calculate_taxes.htm
title: Tax Calculation (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_calculate_taxes.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Tax Calculation (POST)

Calculate tax for a transaction.

Special Access Rules
:   To use this API, you need the CalculateTaxes API permission set.

Resource
:   ```
    /commerce/taxes/actions/calculate
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/taxes/actions/calculate
    ```

Available version
:   62.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   This example shows a tax request for a specified invoice as the reference
        entity.

        ```
        {
          "addresses": {
            "billTo": {
              "street": "123 Main Street",
              "city": "Bainbridge Island",
              "state": "WA",
              "postalCode": "98110",
              "country": "US"
            },
            "soldTo": {
              "street": "123 Main Street",
              "city": "Bainbridge Island",
              "state": "WA",
              "postalCode": "98110",
              "country": "US"
            },
            "shipFrom": {
              "street": "123 Alaskan Way",
              "city": "Seattle",
              "state": "WA",
              "country": "US",
              "postalCode": "98101"
            },
            "shipTo": {
              "street": "123 Main street",
              "city": "Bainbridge Island",
              "state": "WA",
              "postalCode": "98110",
              "country": "US"
            }
          },
          "currencyIsoCode": "USD",
          "customerDetails": {
            "accountId": "001xx000003HYD5AAO"
          },
          "description": "Monthly invoice for account 001xx000003HYEhAAO",
          "documentCode": "3ttxx0000000C7d_Debit-4wAxx00000000ODEAY",
          "effectiveDate": "2022-03-09T10:30:41.000Z",
          "isCommit": true,
          "lineItems": [
            {
              "quantity": 1,
              "amount": 100,
              "taxCode": "TX0001",
              "productCode": "Y0001",
              "productSKU": "PRES-RX-12896745",
              "description": "New Product",
              "effectiveDate": "2022-03-09T10:30:41.000Z",
              "lineNumber": "5TVxx0000004C92GAE",
              "addresses": {
                "shipFrom": {
                  "street": "123 Alaskan Way",
                  "city": "Seattle",
                  "state": "WA",
                  "country": "US",
                  "postalCode": "98101",
                  "latitude": 45.12,
                  "longitude": 45.12
                },
                "shipTo": {
                  "street": "123 Auburn Blvd",
                  "city": "Sacramento",
                  "state": "CA",
                  "country": "US",
                  "postalCode": "95841",
                  "latitude": 45.12,
                  "longitude": 45.12
                },
                "soldTo": {
                  "street": "123 Auburn Blvd",
                  "city": "Sacramento",
                  "state": "CA",
                  "country": "US",
                  "postalCode": "95841",
                  "latitude": 45.12,
                  "longitude": 45.12
                },
                "billTo": {
                  "street": "123 Auburn Blvd",
                  "city": "Sacramento",
                  "state": "CA",
                  "country": "US",
                  "postalCode": "95841",
                  "latitude": 45.12,
                  "longitude": 45.12
                }
              }
            }
          ],
          "referenceDocumentCode" = null,
          "referenceEntityId": "3ttxx0000000C7d",
          "shouldVoidTax": false,
          "taxEngineId": "4wAxx0000000g8v",
          "taxType": "Actual",
          "taxTransactionType": "Debit",
          "transactionDate": "2022-03-09T10:30:41.000Z"
        }
        ```
    :   This example shows a tax request for a specified credit memo as the reference
        entity.

        ```
        {
          "addresses": {
            "billTo": {
              "street": "123 Main Street",
              "city": "Bainbridge Island",
              "state": "WA",
              "postalCode": "98110",
              "country": "US"
            },
            "soldTo": {
              "street": "123 Main Street",
              "city": "Bainbridge Island",
              "state": "WA",
              "postalCode": "98110",
              "country": "US"
            },
            "shipFrom": {
              "street": "123 Alaskan Way",
              "city": "Seattle",
              "state": "WA",
              "country": "US",
              "postalCode": "98101"
            },
            "shipTo": {
              "street": "123 Main street",
              "city": "Bainbridge Island",
              "state": "WA",
              "postalCode": "98110",
              "country": "US"
            }
          },
          "currencyIsoCode": "USD",
          "customerDetails": {
            "accountId": "001xx000003HYD5AAO"
          },
          "description": "Monthly credit memo for account 001xx000003HYEhAAO",
          "documentCode": "50gxx000000g27KAAQ-4wAxx00000000ODEAY",
          "effectiveDate": "2022-03-09T10:30:41.000Z",
          "isCommit": true,
          "lineItems": [
            {
              "quantity": 1,
              "amount": 100,
              "taxCode": "TX0001",
              "productCode": "Y0001",
              "productSKU": "PRES-RX-12896745",
              "description": "New Product",
              "effectiveDate": "2022-03-09T10:30:41.000Z",
              "lineNumber": "5TVxx0000004C92GAE",
              "addresses": {
                "shipFrom": {
                  "street": "123 Alaskan Way",
                  "city": "Seattle",
                  "state": "WA",
                  "country": "US",
                  "postalCode": "98101",
                  "latitude": 45.12,
                  "longitude": 45.12
                },
                "shipTo": {
                  "street": "123 Auburn Blvd",
                  "city": "Sacramento",
                  "state": "CA",
                  "country": "US",
                  "postalCode": "95841",
                  "latitude": 45.12,
                  "longitude": 45.12
                },
                "soldTo": {
                  "street": "123 Auburn Blvd",
                  "city": "Sacramento",
                  "state": "CA",
                  "country": "US",
                  "postalCode": "95841",
                  "latitude": 45.12,
                  "longitude": 45.12
                },
                "billTo": {
                  "street": "123 Auburn Blvd",
                  "city": "Sacramento",
                  "state": "CA",
                  "country": "US",
                  "postalCode": "95841",
                  "latitude": 45.12,
                  "longitude": 45.12
                }
              }
            }
          ],
          "referenceDocumentCode" = null,
          "referenceEntityId": "50gxx000000g27K",
          "shouldVoidTax": false,
          "taxEngineId": "4wAxx0000000g8v",
          "taxType": "Actual",
          "taxTransactionType": "Debit",
          "transactionDate": "2022-03-09T10:30:41.000Z"
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `addresses` | [Addresses](./connect_requests_addresses_input.htm.md "Input representation of the details of the addresses for calculating tax.") | Address details for tax calculation. | Optional | 62.0 |
        | `currencyIsoCode` | String | Currency ISO code that’s used for tax calculation. | Optional | 62.0 |
        | `customerDetails` | [Customer Details](./connect_requests_customer_details_input.htm.md "Input representation of the customer details for tax calculation.") | Customer details for determining the applicable tax. | Optional | 62.0 |
        | `description` | String | Description of the tax transaction. | Optional | 62.0 |
        | `documentCode` | String | Unique identifier for the tax document. If the `documentCode` property isn't specified, the tax engine auto-generates it. | Optional | 62.0 |
        | `effectiveDate` | String | Date when the tax rules are applied. If a tax rate changes on a specific date, the `effectiveDate` property ensures the correct rate is applied based on the transaction's timing.  For credit-based tax callouts, specify the original invoice date. | Optional | 62.0 |
        | `isCommit` | Boolean | Indicates whether to submit the transaction to the tax engine for reporting (`true`) or not (`false`). This property value is `true` for invoices and credit memos with the `Posted` status. | Optional | 62.0 |
        | `lineItems` | [Line Item Input](./connect_requests_line_item_input.htm.md "Input representation of the details of the line item for tax calculation.") [] | Details of the line items for calculating the applicable tax. | Required | 62.0 |
        | `reference​DocumentCode` | String | Reference document code. For subsequent transactions such as a credit tax, this property value specifies the original document code.  For credit-based tax callouts, specify the original invoice ID. | Optional | 62.0 |
        | `reference​EntityId` | String | ID of the related quote, invoice, and other transaction documents. | Optional | 62.0 |
        | `sellerDetails` | [Seller Details Input](./connect_requests_seller_details_input.htm.md "Input representation of the seller details for tax calculation.") | Seller details for tax calculation. | Optional | 62.0 |
        | `shouldVoidTax` | Boolean | Indicates whether to void the tax transaction associated with a document that's mentioned as the `referenceDocumentCode` property value with `taxType` property value as `Actual` and `isCommit` property value set to `true`.  Keep these considerations in mind when you use this property.   - If the `shouldVoidTax` property value   is set to `true`, then the operation   returns a response with `documentCode`   property value updated to `referenceDocumentCode` property value that was originally sent   in the request payload. The response also includes the `taxTransactionType` property value as   `Void`. This indicates that the   document specified in the `referenceDocumentCode` property value is voided. - If document is locked or you can't void the tax transaction for any   reason, then you can use the Tax Calculation request to perform another   transaction such as a Credit Tax request. In this scenario, the response   includes the `documentCode` property   value that was sent in the request payload. - If the document that's mentioned in the `referenceDocumentCode` property value isn't available in the   tax engine, then an error response occurs with [ResultCode](./apex_enum_commercetax_ResultCode.htm.md "Code that represents the results of a tax request made to the tax engine.") value as `ReferenceDocumentCodeMissing`. | Optional | 65.0 |
        | `taxEngineId` | String | ID of the tax engine that’s used to calculate tax. | Required | 62.0 |
        | `tax​TransactionType` | String | Type of the tax transaction. Valid values are:  - `Debit`—Increases tax   liability for the seller, requiring the seller to pay tax on the   transaction. - `Credit`—Decreases tax   liability for the seller, resulting in a tax refund for the seller. - `Void`—Reserved for internal   use.   The default value is `Debit`. | Optional | 62.0 |
        | `taxType` | String | Type of the tax. Valid values are:  - `Actual`—Exact tax amount   that’s calculated based on actual sales. - `Estimated`— Estimated tax   amount, which is adjusted later to match actual tax calculations.   For draft invoices and quote records, the tax type is marked as `Estimated`. After draft invoices are posted and the status changes to `Posted`, the tax type is updated to `Actual`. Similarly, when a quote record is finalized and converted into an actual order, the tax type is also updated to `Actual`. | Required | 62.0 |
        | `transactionDate` | String | Date of the transaction that appears on the invoice, order, and other transaction documents. | Required | 62.0 |

Response body for POST
:   [Tax Calculation](./connect_responses_calculate_tax_output.htm.md "Output representation of the details of the calculated tax.")
