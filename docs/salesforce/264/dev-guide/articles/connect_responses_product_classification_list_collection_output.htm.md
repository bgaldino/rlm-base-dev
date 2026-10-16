---
page_id: connect_responses_product_classification_list_collection_output.htm
title: Product Classification List Collection
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_classification_list_collection_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Classification List Collection

Output representation that contains a collection of product classification records
    along with any processing errors.

    
      
        
          

**JSON example**

          
: 
            

```
{
  "success": true,
  "errors": [],
  "productClassifications": [
    {
      "id": "11BT10000004C9SMAU",
      "name": "Mobile Devices",
      "code": "MOB_DEV",
      "parentProductClassificationId": "11BDU0000004JXq2AM",
      "status": "Active"
    },
    {
      "id": "11BT10000004C9TMAU",
      "name": "Mobile Accessories",
      "code": "MOB_ACC",
      "status": "Active"
    }
  ]
}
```

          

        
      

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Product Catalog Management Error](./connect_responses_p_c_m_error_output.htm.md)[] | List of errors encountered during the processing of the API request. | Small, 67.0 | 67.0 |
| `productClassifications` | [Product Classification](./connect_responses_product_classification_output.htm.md)[] | List of product classification records that match the request query. | Small, 67.0 | 67.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or has failed (`false`). | Small, 67.0 | 67.0 |
