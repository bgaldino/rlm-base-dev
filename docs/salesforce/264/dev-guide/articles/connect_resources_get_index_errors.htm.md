---
page_id: connect_resources_get_index_errors.htm
title: Snapshot Index Error (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_index_errors.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Snapshot Index Error (GET)

Get the count and details of the errors that occurred during the
      indexing process.

    
      
        
          

**Resource**

          
: 
            

```
/connect/pcm/index/error
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/index/error
```

          

        
        
          

**Available version**

          
: 63.0

        
        
          

**HTTP methods**

          
: GET

        
        
          

**Request parameters for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `indexId` | String | ID of the index. | Required | 63.0 |
| `snapshot​IndexId` | String | ID of the snapshot index. | Required | 63.0 |

          

        
        
          

**Response body for GET**

          
: [Snapshot Index
              Error](./connect_responses_snapshot_index_error_output.htm.md)
