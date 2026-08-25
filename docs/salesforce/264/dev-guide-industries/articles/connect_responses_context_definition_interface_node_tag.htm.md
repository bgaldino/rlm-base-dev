---
page_id: connect_responses_context_definition_interface_node_tag.htm
title: Context Definition Interface Node Tag
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_interface_node_tag.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Definition Interface Node Tag

Output representation of the tags associated with the context definition
    interface.

        
          

**JSON example**

          
: 
            

```
{
  "contextDefinitionInterfaceNodeTagList": [
    {
      "attributeTags": [
        {
          "dataType": "STRING",
          "isMappingRequired": true,
          "isNodeTag": false,
          "tagName": "id_attr_tag"
        }
      ],
      "childNodeTags": [
        {
          "attributeTags": [
            {
              "dataType": "STRING",
              "isMappingRequired": false,
              "isNodeTag": false,
              "tagName": "contactId_attr_tag"
            },
            {
              "dataType": "STRING",
              "isMappingRequired": true,
              "isNodeTag": false,
              "tagName": "contactName_attr_tag"
            }
          ],
          "childNodeTags": [],
          "isMappingRequired": false,
          "isNodeTag": true,
          "tagName": "Contact_node_tag"
        }
      ],
      "isMappingRequired": true,
      "isNodeTag": true,
      "tagName": "Account_node_tag"
    }
  ]
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attributeTags` | [Context Definition Interface Attribute Tag](./connect_responses_context_definition_interface_attribute_tag.htm.md)[] | List of attribute tags associated with the context definition interface. | Small, 62.0 | 62.0 |
| `childNodeTags` | [Context Definition Interface Node Tag](#)[] | List of child node tags associated with the context definition interface. | Small, 62.0 | 62.0 |
| `isMappingRequired` | Boolean | Indicates whether the context tags must be mapped in the context definition (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `isNodeTag` | Boolean | Indicates whether the context tag is a node tag (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `isOptional` | Boolean | Indicates whether validation must be done for the context tag (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `tagName` | String | Name of the context tag. | Small, 62.0 | 62.0 |
