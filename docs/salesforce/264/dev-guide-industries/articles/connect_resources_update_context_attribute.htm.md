---
page_id: connect_resources_update_context_attribute.htm
title: Context Attribute (PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_update_context_attribute.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Attribute (PATCH)

Update attributes of a context record.

    
      
        
          

**Resource**

          
: 
            

```
/connect/contexts/attributes
```

          

        
        
          

**Example for PATCH**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/contexts/attributes
```

          

        
        
          

**Available version**

          
: 59.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: PATCH

        
        
        
          

**Request body for PATCH**

          
: 
            
        
          

**JSON example**

          
: 
            

```
{
    "contextId": "3729ed60-d16d-41b8-8951-9ad4f6407ad2",
    "nodePathAndAttributes": [
        {
            "nodePath": {
                "dataPath": [
                    "TestOrder123"
                ]
            },
            "attributes": [
                {
                    "attributeName": "Status",
                    "attributeValue": "DISPATCHED"
                }
            ]
        }
    ]
}
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `updateContextAttributesInput` | Object | Input object for updating context attributes. | Required | 59.0 |

          

        
      

          

          
: 
            

#### Note

 When a context definition is mapped to Account and a field is mapped to `Account.RecordType.Name`, updating the RecordType's ID
              does not update the mapped field. This is because updating the RecordType ID does not
              cause updates to other fields of the RecordType record.

          

        
        
          

**Response body for PATCH**

          
: [Context
            Output](./connect_responses_context_output.htm.md)
