---
page_id: connect_requests_integration_procedure_service_run_input.htm
title: Integration Procedure Service Run
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_integration_procedure_service_run_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Integration Procedure Service Run

Input representation of the details to execute an integration procedure from
    Apex.

        
          

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
