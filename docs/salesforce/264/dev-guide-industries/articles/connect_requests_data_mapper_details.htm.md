---
page_id: connect_requests_data_mapper_details.htm
title: Data Mapper Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_data_mapper_details.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_data_mapper_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Data Mapper Details

Input representation of the data mapper details to clear the cache for.

    
      
        
          

**JSON example**

          
: 
            

```
{
  "dataMappers": [
    {
      "dataMapperName": "DRWithLoad",
      "input": {
        "Name": "Get Account Details"
      }
    }
  ]
}
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `dataMapperName` | String | Name of the data mapper to clear the cache for. The execution cache is cleared for the storage that's specified in the `cacheStorageType` property. | Required | 64.0 |
| `input` | String | Custom JSON data to clear the cache. | Optional | 64.0 |
