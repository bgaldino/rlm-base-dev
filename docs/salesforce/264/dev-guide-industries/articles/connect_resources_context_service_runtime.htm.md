---
page_id: connect_resources_context_service_runtime.htm
title: Context Service (DELETE, GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_service_runtime.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Service (DELETE, GET)

Retrieve the context details using a context ID. Delete a context record using a
    context ID.

    
      
        
          

**Resource**

          
: 
            

```
/connect/contexts/${contextId}
```

          

        
        
          

**Example **

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/contexts/c4c69a9a-3841-4fc3-a10d-a52779ade3d8
```

          

        
        
          

**Available version**

          
: 59.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: DELETE, GET

        
        
          

**Response body for GET**

          
: [Context Info](./connect_responses_context_info.htm.md)

        
        
          

**Response body for DELETE**

          
: None.
