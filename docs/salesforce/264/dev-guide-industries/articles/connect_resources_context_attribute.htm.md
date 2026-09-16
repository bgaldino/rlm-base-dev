---
page_id: connect_resources_context_attribute.htm
title: Context Attribute (POST, PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_attribute.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_attribute_management.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Attribute (POST, PATCH)

Create a list of context attributes.

    
      
        
          

**Resource**

          
: 
            

```
/connect/context-nodes/${contextNodeId}/context-attributes
```

          

        
        
          

**Example for POST**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-nodes/${contextNodeId}/context-attributes
```

          

        
        
          

**Example for PATCH**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-nodes/${contextNodeId}/context-attributes
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
    "contextAttributes": [
        {
            "dataType": "STRING",
            "fieldType": "INPUT",
            "name": "Attribute_5",
            "tags": {
                "contextTags": [
                    {
                        "name": "Attribute_5_Tag"
                    }
                ]
            }
        },
        {
            "dataType": "NUMBER",
            "fieldType": "OUTPUT",
            "name": "Attribute_6"
        }
    ]
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextAttributeId` | String | ID of the attribute. | Required | 59.0 |
| `dataType` | String | Data type of the attribute. | Required | 59.0 |
| `domainSet` | String | Comma separated node names referenced by this attribute. | Optional | 59.0 |
| `fieldType` | String | Field type of the attribute. | Required | 59.0 |
| `isKey` | Boolean | Specifies if it used for transposable feature (`true`) or not (`false`). | Optional | 59.0 |
| `isValue` | Boolean | Specifies if it used for transposable feature (`true`) or not (`false`). | Optional | 59.0 |
| `name` | String | Name of the attribute. | Required | 59.0 |
| `tags` | [Context Tag Input](./connect_requests_context_tag_input.htm.md)[] | List of tags for the attribute. | Optional | 59.0 |

          

        
        
          

**Response body for POST**

          
: 
[Context Attribute List](./connect_responses_context_attribute_list.htm.md)
          

        
        
          

**Request body for PATCH**

          
: 

              
                

**JSON example**

                
: 
                  

```
{
    "contextAttributes": [
        {
            "name": "Attribute_5_Updated",
            "contextAttributeId": "11nxx000001hOvRAAU"
        },
        {
            "name": "Attribute_6_Updated",
            "contextAttributeId": "11nxx000001hOvSAAU"
        }
    ]
}
```

                

              
            

        
        
          

**Response body for PATCH**

          
: 
[Context Attribute List](./connect_responses_context_attribute_list.htm.md)
