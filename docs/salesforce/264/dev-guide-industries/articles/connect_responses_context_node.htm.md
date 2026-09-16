---
page_id: connect_responses_context_node.htm
title: Context Node
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_node.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Node

Output representation of the details of context nodes.

      
        
          

**JSON Example**

          
: 
            

```
{
  "contextNodes": [
    {
      "attributes": [],
      "baseReference": "11oxx000001G1DTPP88",
      "canonicalNodeId": "11oxx000001G1CGAA0",
      "childNodes": [],
      "contextDefinitionVersionId": "11pxx0000004UvYAAU",
      "contextNodeId": "11oxx000001G3xEAAS",
      "displayName": "Mobile_Contact_AccountSibRef",
      "isSuccess": true,
      "isTransposable": false,
      "name": "Mobile_Contact_AccountSibRef",
      "parentNodeId": "11oxx000001G1AeAAK",
      "tags": []
    }
  ]
}
```

          

        
      

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attributes` | [Context Attribute List](./connect_responses_context_attribute_list.htm.md)[] | List of attributes. | Small, 59.0 | 59.0 |
| `baseReference` | String | Identifies the context node ID of the parent context definition that this context node is inherited from. | Small, 60.0 | 60.0 |
| `canonicalNodeId` | String | ID of the canonical node that’s used as a reference to create this context node. | Small, 61.0 | 61.0 |
| `childNodes` | [Context Node Output](#)[] | List of child context nodes. | Small, 59.0 | 59.0 |
| `contextDefinition​VersionID` | String | ID of context definition version. | Small, 59.0 | 59.0 |
| `contextNodeID` | String | ID of this context node. | Small, 59.0 | 59.0 |
| `displayName` | String | Name of the context node that appears on the UI. | Small, 61.0 | 61.0 |
| `isSuccess` | Boolean | Specifies if the operation is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isTransposable` | Boolean | Specifies if the context node is used for the transposable feature (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `name` | String | Name of the context node. | Small, 59.0 | 59.0 |
| `parentNodeId` | String | ID of (parent) context node. | Small, 59.0 | 59.0 |
| `tags` | [Context Attribute Tag Output](./connect_responses_context_attribute_tag.htm.md)[] | List of tags. | Small, 59.0 | 59.0 |
