---
page_id: connect_requests_integration_procedure_cache_input_data.htm
title: Integration Procedure Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_integration_procedure_cache_input_data.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Integration Procedure Details

Input representation of the details of the integration procedures to clear the cache
    for.

    
      
        
          

**JSON example**

          
: 
            

```
{
  "inputs": [
    {
      "ipkey": "Account_GetAccountDetails",
      "inputData": "{\"Name\": \"Get Account Details\"}",
      "blockName": "Cache"
    }
  ]
}
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `blockName` | String | Block name of the integration procedure. | Optional | 64.0 |
| `iPKey` | String | Unique key that's associated with the integration procedure. The format of the value for this property is `Type_SubType`. | Required | 64.0 |
| `inputData` | String | Additional data to clear the cache. | Optional | 64.0 |
