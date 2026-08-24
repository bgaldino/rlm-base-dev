---
page_id: connect_responses_error_output.htm
title: Error Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_error_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Error Details

Output representation of the top-level error detail when validation fails.

      
        
          

**JSON example**

          
: This example shows a sample error
            response.

```
{
  "errors": [
    {
      "errorCode": "VALIDATION_FAILED",
      "message": "Product validation completed with cross-entity errors",
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
  ]
}
```

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Standardized error code. For example, `VALIDATION_FAILED`. | Big, 66.0 | 66.0 |
| `message` | String | Human-readable error message that describes the overall validation failure. | Big, 66.0 | 66.0 |
| `products` | [Product Validation Result](./connect_responses_product_validation_result_output.htm.md)[] | List of product validation results. | Big, 66.0 | 66.0 |
