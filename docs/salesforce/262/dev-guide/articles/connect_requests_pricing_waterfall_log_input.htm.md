---
page_id: connect_requests_pricing_waterfall_log_input.htm
title: Pricing Waterfall Log Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_pricing_waterfall_log_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_requests.htm
fetched_at: 2026-06-09
---

# Pricing Waterfall Log Input

Input representation of the request to create an explainability action log.

JSON example
:   ```
    {
          "currencyCode": "USD",
          "executionEndTimestamp": "2023-07-31T20:11:29.625Z",
          "executionId": "executionId1",
          "executionStartTimestamp": null,
          "lineItemId": "item1",
          "output": {
              "Subtotal": 38.25,
              "ListPrice": 10,
              "NetUnitPrice": 7.65
      },
          "waterfall": [{
            "fieldToTagNameMapping": {
                "Product2Id": "ItemProduct",
                "Subtotal": "Subtotal",
                "Pricebook2Id": "Pricebook",
                "Quantity": "ItemQuantity",
                "LineItemId": "SalesTransactionSource",
                "ListPrice": "ItemListPrice"
      },
          "inputParameters": {
              "Product2Id": "01txx0000006i44AAA",
              "Pricebook2Id": "01sxx0000005q9xAAA",
              "Quantity": 5,
              "LineItemId": "item1"
        },
          "outputParameters": {
              "Subtotal": 50,
              "ListPrice": 10
          },
          "pricingElement": {
              "adjustments": [{
                  "AdjustmentValue": "95.00",
                  "AdjustmentType": "Amount"
               }],
              "description": null,
              "elementType": "ListPrice",
              "name": "List Price"
          },
              "sequence": 1
        },
        {
            "fieldToTagNameMapping": {
                "PriceAdjustmentScheduleId": "ItemDescription",
                "NetUnitPrice": "ItemNetUnitPrice",
                "Product2Id": "ItemProduct",
                "LowerBound": "ItemQuantity",
                "UpperBound": "ItemQuantity",
                "Subtotal": "Subtotal",
                "Quantity": "ItemQuantity",
                "LineItemId": "SalesTransactionSource",
                "InputUnitPrice": "ItemListPrice"
          },
            "inputParameters": {
                "PriceAdjustmentScheduleId": "84Xxx0000004CGSEA2",
                "Product2Id": "01txx0000006i44AAA",
                "LowerBound": 5,
                "UpperBound": 5,
                "Quantity": 5,
                "LineItemId": "item1",
                "InputUnitPrice": 10
           },
            "outputParameters": {
                  "NetUnitPrice": 8.5,
                  "Subtotal": 42.5
      },
            "pricingElement": {
                  "adjustments": [{
                  "AdjustmentValue": "15.00",
                  "AdjustmentType": "Percentage"
      }],
          "description": null,
          "elementType": "VolumeDiscount",
          "name": "Volume Discount"
        },
          "sequence": 2
          }
      ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `context​Definition​VersionId` | String | Context definition version ID of the pricing procedure. | Optional | 60.0 |
    | `context​MappingId` | String | Context mapping ID of the pricing procedure. | Optional | 60.0 |
    | `currency​Code` | String | Currency code such as, USD or INR. | Optional | 60.0 |
    | `executionEnd​Timestamp` | String | End timestamp of procedure execution. | Optional | 60.0 |
    | `execution​Id` | String | Execution ID for a particular execution of a pricing procedure. | Required | 60.0 |
    | `execution​Start​Timestamp` | String | Start timestamp of procedure execution. | Optional | 60.0 |
    | `lineItem​Id` | String | Line item ID for which the price is being calculated. | Required | 60.0 |
    | `output` | Map<String, Object> | Output of the pricing procedure. | Optional | 60.0 |
    | `waterfall` | [Pricing Waterfall Input](./connect_requests_pricing_waterfall_input.htm.md "Input representation of the pricing waterfall details.")[] | Details of the pricing waterfall. | Required | 60.0 |
