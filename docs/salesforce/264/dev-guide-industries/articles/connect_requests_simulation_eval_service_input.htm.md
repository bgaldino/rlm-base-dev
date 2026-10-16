---
page_id: connect_requests_simulation_eval_service_input.htm
title: Simulation Evaluation Service Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_simulation_eval_service_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Simulation Evaluation Service Input

Input representation to run simulation on an expression
      set.

         

#### Note

This API has been deprecated as of API version 55.0.
        In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

            
               

**Root XML tag**

               
: `SimulationEvalServiceInput`

            
            
               

**JSON example**

               
: 
                  

```
{
   "input":{
      "variables":[
         {
            "name":"artEstimatedValue",
            "value":"301",
            "datatype":"number"
         },
         {
            "name":"quantity",
            "value":"301",
            "datatype":"number"
         }
      ]
   },
   "contextInput":{
      "name":"PensionFunds",
      "value":{
         "PolicyDetails":[
            {
               "PolicyName":"Policy1",
               "TotalMember":"100",
               "PrincipalAmout":"500",
               "Status":"Active",
               "TotalPremium":"0"
            },
            {
               "PolicyName":"Policy2",
               "TotalMember":"200",
               "PrincipalAmout":"100",
               "Status":"Inactive",
               "TotalPremium":"0"
            },
            {
               "PolicyName":"Policy3",
               "TotalMember":"300",
               "PrincipalAmout":"400",
               "Status":"Active",
               "TotalPremium":"0"
            }
         ]
      }
   },
   "config":{
      "versionInfo":{
         "configurationVersionId":"a1o5w000002EJPPAA4",
         "effectiveDate":"2019-02-13 00:00:00"
      }
   }
}
```

               

            
            
               

**Properties**

               
: 
                  

                        
                        
                        
                        
                        
                        
                           
                              

                              

                              

                              

                              

                           

                        

                        
                           
                              

                              

                              

                              

                              

                           

                           
                              

                              

                              

                              

                              

                           

                           
                              

                              

                              

                              

                              

                           

                        

                     
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `config` | [Simulation Config Input](./connect_requests_simulation_config_input.htm.md) | Configuration details for the simulation. | Required | 53.0 |
| `contextInput` | [Simulation Context Input](./connect_requests_simulation_context_input.htm.md) | Context details for the simulation. | Required | 58.0 |
| `input` | [Simulation Variable Input[]](./connect_requests_simulation_variable_input.htm.md) | List of input variables to run the simulation. | Required | 53.0 |
