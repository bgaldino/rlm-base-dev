---
page_id: connect_resources_node_mapping.htm
title: Context Node Mapping (POST, PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_node_mapping.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_node_mapping_management.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Node Mapping (POST, PATCH)

Create and update context node mappings.

    
      
        
          

**Resource**

          
: 
            

```
/connect/context-mappings/${contextMappingId}/context-node-mappings
```

          

        
        
          

**Example for POST**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-mappings/${contextMappingId}/context-node-mappings
```

          

        
        
          

**Example for PATCH**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-mappings/${contextMappingId}/context-node-mappings
```

          

        
        
          

**Available version**

          
: 59.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: POST, PATCH

        
        
          

**Request body for POST**

          
: 
            
                
                    

**JSON example**

                    
: 
                        

```
{
    "contextNodeMappings": [
        {
            "contextNodeId": "11oxx000001G31BAAS",
            "sObjectName": "Order"
        },
        {
            "contextNodeId": "11oxx000001G31CAAS",
            "sObjectName": "OrderItem"
        }
    ]
}
```

                    

                
                
                    

**Properties**

                    
: 
                        

                                
                                
                                
                                
                                
                                
                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                

                                
                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                

                            
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `attributeMappings` | [Context Attribute Mappings Input](./connect_requests_context_attribute_mappings_input.htm.md)[] | List of context attribute mappings. | Required | 59.0 |
| `contextNodeId` | String | Reference to context node. | Optional | 59.0 |
| `contextNodeMappingId` | String | ID of this context node mapping. Required for update. | Required | 59.0 |
| `sObjectName` | String | SObject name. | Optional | 59.0 |

                    

                
            

          

        
        
          

**Response body for POST**

          
: [Context Node Mapping List Output](./connect_responses_context_node_mapping_list.htm.md)

        
        
          

**Request body for PATCH**

          
: 
            
              
                

**JSON example**

                
: 
                  

```
{
    "contextNodeMappings": [
        {
            "contextNodeMappingId": "11bxx000000YZipAAG",
            "sObjectName": "Quote"
        },
        {
            "contextNodeMappingId": "11bxx000000YZiqAAG",
            "sObjectName": "QuoteItem"
        }
    ]
}
```

                

              
            

          

        
        
          

**Response body for PATCH**

          
: [Context Node Mapping List Output](./connect_responses_context_node_mapping_list.htm.md)
