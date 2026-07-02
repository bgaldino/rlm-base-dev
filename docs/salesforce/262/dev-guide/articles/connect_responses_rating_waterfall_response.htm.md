---
page_id: connect_responses_rating_waterfall_response.htm
title: Rating Waterfall Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_rating_waterfall_response.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Rating Waterfall Response

Output representation of a rating waterfall request.

JSON example
:   ```
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
| `fieldTo​TagName​Mapping` | Map<String, String> | Mappings of field to tag names. | Small, 62.0 | 62.0 |
| `input​Parameters` | Map<String, Object> | Parameters of rating element input. | Small, 62.0 | 62.0 |
| `output​Parameters` | Map<String, Object> | Parameters of rating element output. | Small, 62.0 | 62.0 |
| `pricing​Element` | [Adjustment Details](./connect_responses_rate_adjustment_detail.htm.md "Output representation of a rate adjustment request.") | Details of the rate adjustment of a rating element. | Small, 62.0 | 62.0 |
| `sequence` | Integer | Sequence of rating element execution. | Small, 62.0 | 62.0 |
