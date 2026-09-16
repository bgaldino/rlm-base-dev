---
page_id: connect_resources_get_index_settings.htm
title: Index Setting (GET, PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_index_settings.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Index Setting (GET, PATCH)

Fetch and update settings related to indexing and
    search.

    
      
        
          

**Resource**

          
: 
            

```
/connect/pcm/index/setting
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/index/setting
```

          

        
        
          

**Available version**

          
: 63.0

        
        
          

**HTTP methods**

          
: GET, PATCH

        
        
          

**Response body for GET**

          
: [Index Setting
              Results](./connect_responses_index_setting_output.htm.md)

        
        
          

**Request body for PATCH**

          
: 
            

**JSON example**

: 

```
{
    "setting" : {
        "supportedLanguages" : ["en_US","ja","es","nl_NL"],
        "defaultLanguage" : "en_US",
        "productsGrouping": "GROUPING_VARIATION"
   }
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `setting` | [Setting Input](./connect_requests_setting_input.htm.md)[] | Object containing the setting-related details. | Required | 63.0 |

          

        
        
          

**Request parameters for PATCH**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `settingId` | String | ID of the setting to update the details for. | Required | 63.0 |

          

        
        
          

**Response body for PATCH**

          
: [Index Setting
              Update](./connect_responses_index_setting_patch_output.htm.md)
