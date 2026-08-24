---
page_id: connect_responses_pricing_water_fall_response.htm
title: Pricing Waterfall Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_water_fall_response.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Pricing Waterfall Response

Output representation of a pricing waterfall request.

      
        
          

**JSON example**

          
: 
            

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
| `pricing​Element` | [Adjustment Details](./connect_responses_adjustment_detail.htm.md) | Details of the price adjustment of a pricing element. | Small, 60.0 | 60.0 |
| `sequence` | Integer | Sequence of pricing element execution. | Small, 60.0 | 60.0 |
