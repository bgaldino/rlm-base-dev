---
page_id: connect_resources_context_tag.htm
title: Context Tag (GET, POST, PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_tag.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_tag_managament.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Tag (GET, POST, PATCH)

Query, create, and update context tag.

    
      
        
          

**Resource**

          
: 
            

```
/connect/context-definitions/${contextDefinitionId}/context-tags
```

          

        
        
          

**Example for GET **

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}/context-tags
```

          

        
        
          

**Example for POST **

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}/context-tags
```

          

        
        
          

**Example for PATCH **

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}/context-tags
```

          

        
        
          

**Available version**

          
: 59.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: GET, POST, PATCH 

        
        
          

**Response body for GET**

          
: 
[Context Tag List Output](./connect_responses_context_tag_list.htm.md)

#### Note

              

When the `includeReferencedDefinitionTag` query
                parameter is set to `true` in a GET request, the
                response will include the name of the context tag in the format `ContextDeveloperName.tagName`.

            

        
        
          

**Request body for POST**

          
: 
            
        
          

**JSON example**

          
: 
            

```
{
    "contextTags": [
        {
            "name": "Attribute_Tag",
            "contextAttributeId": "11nxx000001hOozAAE"
        },
        {
            "name": "Node_Tag",
            "contextNodeId": "11oxx000001G9D2AAK"
        }
    ]
}
```

          

        

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextAttributeId` | String | ID of the (parent) context attribute. | Required | 59.0 |
| `contextNodeId` | String | ID of the (parent) context node. | Required | 59.0 |
| `contextTagId` | String | ID of this Context tag. Required only for update. | Optional | 59.0 |
| `name` | String | Name of the context tag. | Required | 59.0 |

          

        
        
          

**Response body for POST**

          
: [Context Tag List Output](./connect_responses_context_tag_list.htm.md)

        
        
          

**Request body for PATCH**

          
: 
            
              
                

**JSON example**

                
: 
                  

```
{
    "contextTags": [
        {
            "name": "Updated_ATag",
            "contextTagId": "11kxx00000ZzcDpAAJ"
        }
    ]
}
```

                

              
            

          

        
        
          

**Response body for PATCH**

          
: [Context Tag List Output](./connect_responses_context_tag_list.htm.md)
