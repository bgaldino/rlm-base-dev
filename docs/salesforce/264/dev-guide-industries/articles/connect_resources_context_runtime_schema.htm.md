---
page_id: connect_resources_context_runtime_schema.htm
title: Context Runtime Schema (DELETE)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_runtime_schema.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Runtime Schema (DELETE)

Clear runtime schema cache for context definitions and their associated mappings. 

    
      
        
          

**Resource**

          
: 
            

```
/connect/context-runtime-schema/clear
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/context-runtime-schema/clear?contextDefinitionDevlName=CustomerProfile&contextMappingNames=StandardMapping,CustomMapping
```

          

        
        
          

**Available version**

          
: 65.0

        
        
          

**HTTP methods**

          
: DELETE

        
        
          

**Request parameters for DELETE**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionDevlName` | String | Developer name of the context definition whose runtime schema is to be cleared. | Required | 65.0 |
| `contextMappingNames` | String[] | Comma-separated list of mapping names to clear. If not provided, the default mapping for the definition is cleared. | Optional | 65.0 |

          

        
        
          

**Response body for DELETE**

          
: 
            

This resource uses query parameters only and returns HTTP 204 No Content on
              success.
