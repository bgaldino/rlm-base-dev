---
page_id: connect_resources_query_context_interface_by_name.htm
title: Query Context Definition Interface By Name (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_query_context_interface_by_name.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Query Context Definition Interface By Name (GET)

Get the details of a context definition interface by using the context definition
    interface name.

    
      
        
          

**Resource**

          
: 
            

```
/connect/context-definition-interfaces/contextDefinitionInterfaceName
```

          

        
        
          
: The contextDefinitionInterfaceName path parameter is the API name
            of the context definition interface.

        
        
          

**Resource example**

          
: 

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/context-definition-interfaces/exampleDefinitionInterface
```

        
        
          

**Available version**

          
: 62.0

        
        
          

**HTTP methods**

          
: GET

        
        
          

**Response body for GET**

          
: [Context Definition
              Interface](./connect_responses_context_definition_interface.htm.md)
