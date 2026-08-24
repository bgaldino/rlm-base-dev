---
page_id: connect_requests_context_attribute_input.htm
title: Context Attribute Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_attribute_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_overview.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Attribute Input

Input representation for updating context attribute.

    
      
        
          

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
