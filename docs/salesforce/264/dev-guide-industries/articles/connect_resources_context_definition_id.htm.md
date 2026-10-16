---
page_id: connect_resources_context_definition_id.htm
title: Context Definition Id (GET, PATCH, DELETE)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_definition_id.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_context_definition_management.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Definition Id (GET, PATCH, DELETE)

Query, update, and delete a context definition using an ID.

    
      
        
          

**Resource**

          
: 
            

```
/connect/context-definitions/${contextDefinitionId}
```

          

        
        
          

**Example for GET**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}
```

          

        
        
          

**Example for PATCH **

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}
```

          

        
        
          

**Example for DELETE **

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}
```

          

        
        
          

**Available version**

          
: 59.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: GET, PATCH, DELETE

        
        
          

**Response body for GET**

          
: [Context Definition Output](./connect_responses_context_definition.htm.md)

        
        
          

**Request body for PATCH**

          
: 

              
                

**JSON example**

                
: 
                  

```
{
"definition": "Example Defintion patch",
"description": "Example Description patch"
}
```

                

              
            

        
        
          

**Response body for PATCH**

          
: [Context Definition Information](./connect_responses_context_definition_info.htm.md)
