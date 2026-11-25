---
page_id: connect-requests-pricing-waterfall-input
title: Pricing Waterfall Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-pricing-waterfall-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-requests
legacy_page_id: connect_requests_pricing_waterfall_input.htm
fetched_at: 2026-11-25
---

# Pricing Waterfall Input

Input representation of the pricing waterfall details.

## JSON Example

```
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
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `fieldTo​TagName​Mapping` | Map<String, String> | Mappings of field to tag names. | Optional | 60.0 |
| `input​Parameters` | Map<String, Object> | Input parameters of the pricing element. | Optional | 60.0 |
| `output​Parameters` | Map<String, Object> | Output parameters of the pricing element. | Optional | 60.0 |
| `pricing​Element` | [Adjustment Details Input](./connect-requests-adjustment-details-input.md) | Details of the pricing element. | Optional | 60.0 |
| `sequence` | Integer | Sequence of the pricing element execution. | Optional | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-pricing-waterfall-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
