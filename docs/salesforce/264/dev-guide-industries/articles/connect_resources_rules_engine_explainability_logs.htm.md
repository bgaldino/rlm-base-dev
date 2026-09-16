---
page_id: connect_resources_rules_engine_explainability_logs.htm
title: Explainability Logs (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_rules_engine_explainability_logs.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_explainer_bre_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Explainability Logs (GET)

Retrieves explainability logs for expression step elements for which
      explanation messages are configured.

    
      
        
          

**Resource**

          
: 
            

```
/connect/business-rules/explainability/logs
```

          

        
        
          

**Resource Example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect
/business-rules/explainability/logs?actionContextCode=001x0000005DmI3AAK
```

          

        
        
          

**Available version**

          
: 56.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: GET

        
        
          

**Request parameters for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `action​Context​Code` | String | The record ID within the context of the associated application's action that’s used to retrieve action logs. | Optional | 56.0 |
| `application​SubType` | String | The subtype of the associated application for which the explainability log is generated. This matches one of the valid values in the ExplainabilityActionDef . `ApplicationSubtype` field. | Optional | 56.0 |
| `application​Type` | String | The name of the application for which the explainability service is run. This matches one of the valid values in the ExplainabilityActionDef .`ApplicationType` field. | Optional | 56.0 |
| `createdAfter` | String | A valid date time after which the explainability log records are returned. | Optional | 56.0 |
| `createdBefore` | String | A valid date time before which the explainability log records are returned. | Optional | 56.0 |
| `pageSize` | Integer | The number of explainability log records to return. The value can range from 200 to 500. | Optional | 56.0 |
| `processType` | String | The process type of the associated application for which the explainability action log is generated. This matches one of the valid values in the ExplainabilityActionDef `ProcessType` field. | Optional | 56.0 |
| `queryMore` | String | A string returned from the previous request, which you must pass to the next request to get the next page. | Optional | 56.0 |

          

        
        
          

**Response body for GET**

          
: [Explainability Logs](./connect_responses_explainability_logs.htm.md)
