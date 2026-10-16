---
page_id: connect_resources_configure_relationship_node.htm
title: Context Node Relationship (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_configure_relationship_node.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_node_mapping_management.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Node Relationship (POST)

Configure a relationship node by adding child context nodes to a specific context
    node.

    
      
        
          

**Resource**

          
: 
            

```
/connect/context-nodes/contextNodeId/configurerelationship
```

          

          
: The contextNodeId specifies the ID of the context node to which you
            want to add the context nodes from the request body as child nodes.

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/context-nodes/11oxx000001G3dtAAC/configurerelationship
```

          

        
        
          

**Available version**

          
: 61.0

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Request body for POST**

          
: 
            
        
          

**JSON example**

          
: 
            

```
{
  "contextNodeIds": [
    "11oxx000001G3dtAAC",
    "11oxx000001G3duAAC"
  ]
}
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextNodeIds` | String | List of context node IDs to create the relationship nodes by adding them as child nodes to the context node that’s specified in the endpoint. | Required | 61.0 |

          

        
      

          

        
        
          

**Response body for POST**

          
: [Context Node List](./connect_responses_context_node_list.htm.md)
