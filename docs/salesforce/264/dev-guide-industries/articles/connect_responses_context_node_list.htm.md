---
page_id: connect_responses_context_node_list.htm
title: Context Node List
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_node_list.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Node List

Output representation of the list of context nodes.

    
      
        
          

**JSON Example**

          
: 
            

```
{
  "contextNodeListId": "ebaf2554-88f2-4cb2-8418-cd3c250a9535",
  "contextNodes": [
    {
      "attributes": [
        {
          "attributeTags": [],
          "contextAttributeId": "11nxx000001hJm5AAE",
          "dataType": "REFERENCE",
          "domainSet": "Contact_AccountSibRef",
          "fieldType": "INPUT",
          "isKey": false,
          "isValue": false,
          "name": "ParentReference",
          "parentNodeId": "11oxx000001G3xEAAS"
        }
      ],
      "canonicalNodeId": "11oxx000001G1CGAA0",
      "childNodes": [],
      "contextDefinitionVersionId": "11pxx0000004UvYAAU",
      "contextNodeId": "11oxx000001G3xEAAS",
      "displayName": "Mobile_Contact_AccountSibRef",
      "isTransposable": false,
      "name": "Mobile_Contact_AccountSibRef",
      "parentNodeId": "11oxx000001G1AeAAK",
      "tags": []
    }
  ],
  "isSuccess": true
}
```

          

        
      

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextNode​ListId` | String | Unique ID of the context node list, which is required for Salesforce Lightning Design System (LDS). | Small, 59.0 | 59.0 |
| `contextNodes` | [Context Node []](./connect_responses_context_node.htm.md) | List of context nodes. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
