---
page_id: connect_requests_context_mappings_input.htm
title: Context Mappings Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_mappings_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Mappings Input

Input representation of context mapping.

                    

**JSON example**

                    
: 
                        

```
{
  "contextMappings": [
    {
      "name": "ExampleMapping",
      "description": "Example Mapping Description",
      "isDefault": true,
      "intents": [
        "ASSOCIATION",
        "HYDRATION",
        "PERSISTENCE",
        "TRANSLATION"
      ]
    }
  ],
  "generateInputMappings": false,
  "generateSObjectMappings": false
}
```

                    

                
                    

**Properties**

                    
: 
                        

                                
                                
                                
                                
                                
                                
                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                

                                
                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                    
                                        

                                        

                                        

- 
- 
- 
- 

                                        

                                        

                                    

                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                

                            
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextMappingId` | String | ID of this context mapping. Required for update. | Required | 59.0 |
| `contextNodeMappings` | Context Node Mappings Input[] | List of context node mappings. | Optional | 59.0 |
| `description` | String | Description of context mapping. | Optional | 59.0 |
| `isDefault` | Boolean | Indicates whether to make a default mapping for the context definition (`true`) or not (`false`). | Optional | 59.0 |
| `intents` | List<String> | Purpose that's used to identify the type of required context mapping.Valid values are: `HYDRATION`—To load cache from a data source. `PERSISTENCE`—To load the sink objects from cache. Sink objects are the final destinations for the processed data. `ASSOCIATION`—To create a mapping without validating database relationships, attaching context structure nodes and their attributes with data source nodes and their attributes. `TRANSLATION`—To transform the data loaded in the cache to another representation defined by the mapping. | Optional | 61.0 |
| `name` | String | Name of the context mapping. | Required | 59.0 |
