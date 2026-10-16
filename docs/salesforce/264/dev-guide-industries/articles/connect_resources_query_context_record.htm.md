---
page_id: connect_resources_query_context_record.htm
title: Query Context Record (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_query_context_record.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Query Context Record (POST)

Query a context record, with the option to retrieve child records.

    
      
        
          

**Resource**

          
: 
            

```
/connect/contexts/query-record
```

          

        
        
          

**Examples**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/contexts/query-record
```

          

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/contexts/query-record?children=false
```

          

        
        
          

**Available version**

          
: 59.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Request parameters for POST**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `children` | Boolean | Indicates whether to retrieve child records `true` or not `false`. | Optional | 59.0 |

          

        
        
          

**Request body for POST**

          
: 
            

**JSON example**

: 

```
{
  "contextId": "7bc695bc-f38b-4a94-8a95-0caa50f3da53"
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `attributes` | String[] | List of attributes to be retrieved. | Optional | 58.0 |
| `businessObjectTypeFilter` | String | Filter based on a business object type. | Optional | 58.0 |
| `contextId` | String | The ID of the context to be queried. | Required | 58.0 |
| `queryPath` | String[] | Path to the parent node. | Optional | 58.0 |

          

        
        
          

**Response body for POST**

          
: [Query
              Context Record Result](./connect_responses_query_context_record_result.htm.md)
