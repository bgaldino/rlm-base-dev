---
page_id: connect_resources_context_query_lean_tag.htm
title: Context Query Tags Leaner (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_query_lean_tag.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Query Tags Leaner (POST)

Query tags and return a memory-optimized (leaner) result suitable for Apex and low-heap
    clients. Eliminate redundant metadata to reduce heap usage and payload size.

    
      
        
          

**Resource**

          
: 
            

```
/connect/contexts/query-tags-leaner
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/contexts/query-tags-leaner
```

          

        
        
          

**Available version**

          
: 67.0

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Request body for POST**

          
: 
            
        
          

**Root XML tag**

          
: `<LeanerQueryTagsInputRepresentation>`

        
        
          

**JSON example**

          
: 
            

```
{
  "contextId": "0000000s07fm061002917633740427233ff03037a8fe48048696667781ec824c",
  "tags": [
    "Contact_FirstName",
    "Contact_Email"
  ]
}
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | ID of the context to query. | Required | 66.0 |
| `tags` | String[] | List of tag names to query from the context. Tags can include both attribute-level and node-level. | Required | 66.0 |

          

        
      

          

        
        
          

**Response body for POST**

          
: [Leaner Query Tags Result](./connect_responses_leaner_query_tags_result.htm.md)
