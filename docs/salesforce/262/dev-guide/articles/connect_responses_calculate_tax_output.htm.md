---
page_id: connect_responses_calculate_tax_output.htm
title: Tax Calculation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_calculate_tax_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Tax Calculation

Output representation of the details of the calculated tax.

JSON example
:   ```
    {
        "referenceEntityId": "001xx000003HYEhAAO",
        "status": "Committed",
        "taxEngineLogs": [
            {
                "createdDate": "2022-03-09T10:55:38.000Z",
                "id": "3l1xx00000000PpAAI",
                "resultCode": "Success"
            }
        ],
        "taxTransactionType": "Debit",
        "taxType": "Actual",
        "transactionDate": "2022-03-09T10:30:41.000Z",
        "addresses": {
            "shipFrom": {
                "locationCode": "67890"
            },
            "shipTo": {
                "locationCode": "23456"
            },
            "soldTo": {
                "locationCode": "23456"
            }
        },
        "amountDetails": {
            "exemptAmount": 0.0,
            "taxAmount": 12.5,
            "totalAmount": 100.0,
            "totalAmountWithTax": 112.5
        },
        "currencyIsoCode": "USD",
        "description": "Monthly invoice for account 001xx000003HYEhAAO",
        "documentCode": "INV-003",
        "effectiveDate": "2022-03-09T10:55:38.410Z",
        "lineItems": [
            {
                "addresses": {
                    "shipFrom": {
                        "locationCode": "67890"
                    },
                    "shipTo": {
                        "locationCode": "12345"
                    },
                    "soldTo": {
                        "locationCode": "12345"
                    }
                },
                "amountDetails": {
                    "exemptAmount": 0.0,
                    "taxAmount": 12.5,
                    "totalAmount": 100.0,
                    "totalAmountWithTax": 112.5
                },
                "effectiveDate": "2022-03-09T10:55:38.416Z",
                "lineNumber": "001xx000003HYEiAAO",
                "productCode": "Y0001",
                "quantity": 1.0,
                "taxCode": "TX0001",
                "taxes": [
                    {
                        "exemptAmount": 0.0,
                        "exemptReason": "NoExemption",
                        "imposition": {
                            "type": "General"
                        },
                        "jurisdiction": {
                            "country": "US",
                            "id": "63000",
                            "level": "CIT",
                            "name": "SEATTLE",
                            "region": "WA",
                            "stateAssignedNo": "1726"
                        },
                        "rate": 12.5,
                        "tax": 12.5,
                        "taxId": "11000378132466",
                        "taxableAmount": 100.0
                    }
                ]
            }
        ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `adapterError` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/connect_responses_error_response.htm) | Details of the adapter error. | Big, 62.0 | 62.0 |
| `addresses` | [Addresses](./connect_responses_addresses_output.htm.md "Output representation of the details of the addresses that are used for calculating tax.") | Addresses that are used for calculating tax. | Big, 62.0 | 62.0 |
| `amountDetails` | [Tax Amount Details](./connect_responses_tax_amount_details_output.htm.md "Output representation of the details of the tax amount.") | Details of the transaction amount and taxes. | Big, 62.0 | 62.0 |
| `currencyIsoCode` | String | Currency ISO code that’s used for tax calculation. | Big, 62.0 | 62.0 |
| `description` | String | Description of the transaction status. | Big, 62.0 | 62.0 |
| `documentCode` | String | Unique identifier for the tax document. If the `documentCode` property isn't specified, the tax engine auto-generates it. | Big, 62.0 | 62.0 |
| `effectiveDate` | String | Date when the tax rules are applied. | Big, 62.0 | 62.0 |
| `lineItems` | [Line Item](./connect_responses_line_item_output.htm.md "Output representation of the details of the line item.") [] | Line items that the taxes are calculated for. | Big, 62.0 | 62.0 |
| `reference​DocumentCode` | String | Reference document code. For subsequent transactions such as a credit tax, the `referenceDocumentCode` property value refers to the original document code. | Big, 62.0 | 62.0 |
| `reference​EntityId` | String | ID of the related quote, invoice, or other transaction documents. | Big, 62.0 | 62.0 |
| `status` | String | Commit status of the tax transaction. Valid values are:  - `Committed`—Committed transaction,   which is marked for tax reporting. - `Uncommitted`— Uncommitted transaction,   which isn’t marked for tax reporting. | Big, 62.0 | 62.0 |
| `taxEngineLogs` | [Tax Engine Log](./connect_responses_tax_engine_log_output.htm.md "Output representation of the logs that the tax engine generates.") [] | Records that the tax engine generates while calculating taxes for the transaction. | Big, 62.0 | 62.0 |
| `tax​TransactionId` | String | Unique ID for the tax transaction. | Big, 62.0 | 62.0 |
| `transactionDate` | String | Date of the transaction that appears on the invoice, order, and other transaction documents. | Big, 62.0 | 62.0 |
| `taxTransaction​Type` | String | Tax transaction type. Valid values are:  - `Debit`—Increases tax liability for   the user, requiring the user to pay tax on the transaction. - `Credit`—Decreases tax liability for   the user, resulting in a tax refund for the user. - `Void`—Specifies that the tax engine   has voided the document that's mentioned as the `referenceDocumentCode` property value. | Big, 62.0 | 62.0 |
| `taxType` | String | Type of calculated tax. Valid values are:  - `Actual`—Exact tax amount that’s   calculated based on the actual sales. - `Estimated`— Estimated tax amount,   which is adjusted later to match the actual tax calculations. | Big, 62.0 | 62.0 |
