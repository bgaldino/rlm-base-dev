---
page_id: connect_requests_integration_procedure_cache_keys_list.htm
title: Integration Procedure Cache Keys
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_integration_procedure_cache_keys_list.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Integration Procedure Cache Keys

Input representation of the cache keys to clear the execution cache.

    
      
        
          

**JSON example**

          
: 
            

```
{
    "cacheKeys": [
      "IP06535636"
    ]
}
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `cacheKeys` | String[] | List of cache keys to clear the cache for. | Optional | 64.0 |
