---
page_id: connect_resources_integration_procedure.htm
title: Integration Procedure Execution (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_integration_procedure.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Integration Procedure Execution (POST)

Execute an integration procedure by using the name or ID of the integration
    procedure.

    
      

#### Note

When using the Integration Procedure (IP) Connect API, HTTP
        callouts cannot be executed in the same transaction. This is because these APIs perform an
        implicit DML operation through the underlying Connect API framework. If a callout is
        required, it must be executed in a separate transaction, for example by using an
        asynchronous mechanism such as @future.

      
        
          

**Resource**

          
: 
            

```
/connect/omni-global/integration-procedure/execute/id
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/omni-global/integration-procedure/execute/0jNxx000000005rFCC
```

          

        
        
          

**Available version**

          
: 64.0

        
        
          

**HTTP methods**

          
: POST

        
      

      
        
          

**Path parameter for POST**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | Name or ID of the integration procedure. | Required | 64.0 |

          

        
      

      
        
          

**Request body for POST**

          
: 
            
        
          

**JSON example**

          
: 
            

```
{
  "input": {
    "inputs": [
      "{\"Name\": \"Get Account Details\"}"
    ]
  },
  "options": {
    "ignoreCache": false
  }
}
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `input` | [Integration Procedure Service Run Input](./connect_requests_integration_procedure_service_run_input_list.htm.md) | Details to execute the integration procedure. | Required | 64.0 |
| `options` | [Integration Procedure Service Run Options](./connect_requests_integration_procedure_service_run_options.htm.md) | Optional parameters to refine the execution of the integration procedure. | Optional | 64.0 |

          

        
      

       

        
        
          

**Response body for POST**

          
: [Integration Procedure
              Execution Details](./connect_responses_integration_procedure_service_run_output.htm.md)
