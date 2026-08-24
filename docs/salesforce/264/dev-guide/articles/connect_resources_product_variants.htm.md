---
page_id: connect_resources_product_variants.htm
title: Product Variants (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_product_variants.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Variants (POST)

Retrieve the variation product associated with one or more parent
      variant products.

    
      

A parent variant product is a non-purchasable product that groups related variations. Use
        this API to retrieve the mapping between parent variant product IDs and their associated
        variation product IDs.

    

    
      
        
          

**Resource**

          
: 
            

```
/connect/pcm/products/variants
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/products/variants
```

          

        
        
          

**Available version**

          
: 67.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: POST

#### Note

POST methods typically create an item, but for this resource POST is used to
              retrieve information.

        
        
          

**Request body for POST**

          
: 
            
        
          

**JSON example**

          
: 
            

```
{
  "correlationId": "9b6bc520-3c82-4d6c-a458-47590370681a",
  "parentVariantsIds": [
    "01tT1000000F0afIAC",
    "01tT1000000F0agIAC"
  ]
}
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique ID to track and associate related events or transactions. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 67.0 |
| `parent​Variants​Ids` | String[] | List of product IDs for parent variant products whose variations you want to retrieve. If any product ID is blank, invalid, or not found, the API skips that ID and processes the remaining valid IDs. The skipped IDs appear in the `inValidProductIds` response property. If a product ID is valid but isn't a parent variant product, the API includes it in the `nonVariantParentIds` response property. | Required | 67.0 |

          

        
      

          

        
        
          

**Response body for POST**

          
: [Product
              Variants](./connect_responses_product_variants_output.htm.md)
