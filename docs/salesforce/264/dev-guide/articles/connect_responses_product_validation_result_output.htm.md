---
page_id: connect_responses_product_validation_result_output.htm
title: Product Validation Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_validation_result_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Validation Result

Output representation of the validation result for a specific product.

      
        
          

**JSON example**

          
: This example shows the product validation result.

```
{
  "products": [
    {
      "productId": "01txx0000006i2gAAA",
      "validationResult": {
        "validationErrors": [],
        "validationWarnings": []
      }
    }
  ]
}
```

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `productId` | String | Unique product ID that's being validated. | Big, 67.0 | 67.0 |
| `validationResult` | [Validation Result](./connect_responses_validation_result_output.htm.md) | Validation results grouped by rule name. | Big, 67.0 | 67.0 |
