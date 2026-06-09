---
page_id: connect_responses_place_sales_transaction_async_error_output.htm
title: Sales Transaction Async Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_place_sales_transaction_async_error_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Sales Transaction Async Error

Output representation of the details of errors encountered during the async processing of
the Place Sales Transaction API request.

JSON example
:   ```
    {
      "errors": [
        {
          "errorCode": "FIELD_CUSTOM_VALIDATION_EXCEPTION",
          "message": "Quantity cannot exceed 10",
          "referenceId": "refQuoteLineItem2"
        }
      ],
      "jobStatus": "Completed",
      "retryablePayload": {
        "pricingPref": "System",
        "configurationPref": {
          "configurationMethod": "System",
          "configurationOptions": {
            "validateProductCatalog": true,
            "validateAmendRenewCancel": true,
            "executeConfigurationRules": true,
            "addDefaultConfiguration": true
          }
        },
        "graph": {
          "graphId": "1",
          "records": [
            {
              "referenceId": "refQuoteLineItem2",
              "record": {
                "attributes": {
                  "type": "QuoteLineItem",
                  "method": "POST"
                },
                "QuoteId": "000xx0000004CNYCA2",
                "PricebookEntryId": "01uxx0000009CL2",
                "Product2Id": "01txx0000006uu2",
                "Quantity": 15,
                "UnitPrice": 100
              }
            },
            {
              "referenceId": "refQuoteLineItem3",
              "record": {
                "attributes": {
                  "type": "QuoteLineItem",
                  "method": "POST"
                },
                "QuoteId": "000xx0000004CNYCA2",
                "PricebookEntryId": "01uxx0000009CL3",
                "Product2Id": "01txx0000006uu3",
                "Quantity": 20,
                "UnitPrice": 100
              }
            },
            {
              "referenceId": "refQuoteLinePriceAdjustment1",
              "record": {
                "attributes": {
                  "type": "QuoteLinePriceAdjustment",
                  "method": "POST"
                },
                "QuoteLineItemId": "@{refQuoteLineItem3.id}",
                "Name": "Some Promo",
                "Amount": -25
              }
            }
          ]
        }
      },
      "rolledBackReferenceIds": [
        "refQuoteLineItem3",
        "refQuoteLinePriceAdjustment1"
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Place Sales Transaction Error](./connect_responses_place_sales_transaction_error_response.htm.md "Output representation of the error details associated with the API request.")[] | List of async errors from Place Sales Transaction API. The details include a reference ID for the failed subrequest, an error code, and a detailed message. | Small, 66.0 | 66.0 |
| `jobStatus` | String | Status of the async tracker ID. Error results are returned after the job is in a `Completed` status. | Small, 66.0 | 66.0 |
| `retryablePayload` | [Sales Transaction Input](./connect_requests_place_sales_transaction_input.htm.md "Input representation of the details of the request to place a sales transaction, such as a quote or an order.") | Subset of the original Place Sales Transaction API payload errors that can be used for retry attempts. Reference IDs that are saved are replaced by their corresponding record IDs.This property is included in the response only when the `includeRetryablePayload` query parameter is set to `true`. | Small, 66.0 | 66.0 |
| `rolledBack​ReferenceIds` | String[] | List of rolled-back reference IDs for subrequests due to failure of a subrequest in the same transaction. | Small, 66.0 | 66.0 |
