---
page_id: connect_responses_product_variants_output.htm
title: Product Variants
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_variants_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Variants

Output representation of the variation products associated with the specified parent
    variant products.

    
      
        
          

**JSON example**

          
: 
            

```
{
  "correlationId": "9b6bc520-3c82-4d6c-a458-47590370681a",
  "count": 2,
  "details": {
    "01tT1000000F0afIAC": [
      "01tT1000000F0ahIAC",
      "01tT1000000F0aiIAC"
    ],
    "01tT1000000F0agIAC": [
      "01tT1000000F0ajIAC"
    ]
  },
  "inValidProductIds": [],
  "nonVariantParentIds": [],
  "status": {
    "code": "200",
    "errors": [],
    "message": "Successfully fetched the product variants."
  }
}
```

          

        
      

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique ID to track and associate related events or transactions. | Small, 67.0 | 67.0 |
| `count` | Integer | Number of parent variant products in the response that have at least one associated variation. | Small, 67.0 | 67.0 |
| `details` | Map<String, String[]> | Specifies a map where each key is a parent variant product ID and the value is a list of its associated variation product IDs. Only parent variants that have at least one variation are included in this map. | Small, 67.0 | 67.0 |
| `inValid​Product​Ids` | String[] | List of product IDs from the request that are blank, invalid, or not found in the org. The API excludes these IDs from processing but doesn’t fail the request. | Small, 67.0 | 67.0 |
| `non​Variant​Parent​Ids` | String[] | List of product IDs from the request that are valid products but don’t have the `VariationParent` product class. For example, simple products or bundle products passed in the request appear in this list. | Small, 67.0 | 67.0 |
| `status` | [Status](./connect_responses_status.htm.md) | Status of the request. | Small, 67.0 | 67.0 |
