---
page_id: connect_responses_context_definition_interface_attribute_tag.htm
title: Context Definition Interface Attribute Tag
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_interface_attribute_tag.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Definition Interface Attribute Tag

Output representation of the attribute tags associated with the context definition
    interface.

        
          

**JSON example**

          
: 
            

```
{
  "attributeTags": [
    {
      "dataType": "REFERENCE",
      "isMappingRequired": false,
      "isNodeTag": false,
      "domainName": "Account",
      "tagName": "AccountRef_attr_tag"
    }
  ]
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `dataType` | String | Data type of the attribute associated with the context definition interface. | Small, 62.0 | 62.0 |
| `domainName` | String | Domain name of the attribute associated with the context definition interface. | Small, 62.0 | 62.0 |
| `isMappingRequired` | Boolean | Indicates whether the attribute tag must be mapped in the context definition (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `isNodeTag` | Boolean | Indicates whether the attribute tag is a node tag (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `isOptional` | Boolean | Indicates whether validation must be done for the attribute tag (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `isSuccess` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `tagName` | String | Name of the attribute tag. | Small, 62.0 | 62.0 |
