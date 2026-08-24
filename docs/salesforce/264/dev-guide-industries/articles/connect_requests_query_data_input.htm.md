---
page_id: connect_requests_query_data_input.htm
title: Query Record Status Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_query_data_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Query Record Status Input

Input representation of status and related error messages of query data
    records.

    
      
        
          

**JSON example**

          
: 
            

```
{
    "queryRecordStatusInput": {
        "contextId": "3729ed60-d16d-41b8-8951-9ad4f6407ad2",
        "queryPaths": [
            {
                "dataPath": [
                    "TestOrder123"
                ]
            }
        ]
    }
}

```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `queryRecordStatusInput` | Object | Input representation for context ID and the list of paths for querying the status. | Required | 59.0 |
