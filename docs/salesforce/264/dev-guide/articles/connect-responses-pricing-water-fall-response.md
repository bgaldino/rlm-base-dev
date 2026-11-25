---
page_id: connect-responses-pricing-water-fall-response
title: Pricing Waterfall Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-pricing-water-fall-response.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-responses
legacy_page_id: connect_responses_pricing_water_fall_response.htm
fetched_at: 2026-11-25
---

# Pricing Waterfall Response

Output representation of a pricing waterfall request.

## JSON Example

```
{
  "inputParameters": {
    "productId": "01txx0000006i2SAAQ",
    "pricebookId": "01sxx0000005ptpAAA",
    "pricingModelType": "OneTime"
  },
  "fieldToTagNameMapping": {
    "Product2Id": "ItemProduct",
    "Subtotal": "Subtotal",
    "Pricebook2Id": "Pricebook",
    "Quantity": "ItemQuantity",
    "LineItemId": "SalesTransactionSource",
    "ListPrice": "ItemListPrice"
  },
  "sequence": 0,
  "outputParameters": {
    "listPrice": "10"
  },
  "pricingElement": {
    "adjustments": [
      {
        "adjustmentType": null,
        "adjustmentValue": null
      }
    ],
    "name": "List Price"
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `fieldTo​TagName​Mapping` | Map<String, String> | Mappings of field to tag names. | Small, 60.0 | 60.0 |
| `input​Parameters` | Map<String, Object> | Parameters of pricing element input. | Small, 60.0 | 60.0 |
| `output​Parameters` | Map<String, Object> | Parameters of pricing element output. | Small, 60.0 | 60.0 |
| `pricing​Element` | [Adjustment Details](./connect-responses-adjustment-detail.md) | Details of the price adjustment of a pricing element. | Small, 60.0 | 60.0 |
| `sequence` | Integer | Sequence of pricing element execution. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-pricing-water-fall-response.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
