---
page_id: connect_resources_context_attribute_mapping_id.htm
title: Context Attribute Mapping ID (GET, DELETE)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_attribute_mapping_id.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_mapping_management.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Attribute Mapping ID (GET, DELETE)

Query and delete a context attribute mapping using an ID.

    
      
        
          

**Resource**

          
: 
            

```
/connect/context-node-mappings/${contextNodeMappingId}/context-attribute-mappings/${contextAttributeMappingId}
```

          

        
        
          

**Example for GET **

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-node-mappings/${contextNodeMappingId}/context-attribute-mappings/${contextAttributeMappingId}
```

          

        
        
          

**Example for DELETE **

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-node-mappings/${{contextNodeMappingId}/context-attribute-mappings/${contextAttributeMappingId}
```

          

        
        
          

**Available version**

          
: 59.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: GET, DELETE

        
        
          

**Response body for GET**

          
: [Context Attribute Mapping Output](./connect_responses_context_attribute_mapping.htm.md)
