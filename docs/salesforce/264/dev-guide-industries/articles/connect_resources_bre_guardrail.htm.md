---
page_id: connect_resources_bre_guardrail.htm
title: Guardrails (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_guardrail.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Guardrails (GET)

Fetches guardrails from the Business Rules Engine (BRE) to manage rate limits for BRE
    components.

    
      
        
          

**Resource**

          
: 
            

```
/connect/business-rules/guardrails
```

          

        
        
          

**Example POST**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/business-rules/guardrails
```

          

        
        
          

**Available version**

          
: 63.0

        
        
          

**HTTP methods**

          
: GET

        
        
          

**Request parameters for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

- 
- 
- 
- 
- 

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `componentNames` | String | BRE component to fetch the guardrails. It contains a comma-separated list of predefined components. Valid component values are: `ExpressionSet` `DecisionTable` `DecisionMatrix` `Explainability` `DynamicRules` If no values are provided, guardrails for all components accessible to the user are returned. | Optional | 63.0 |
| `isNotification​Enabled` | Boolean | Indicates whether to return only the guardrails with enabled notifications (`true`) or not (`false`). | Optional | 63.0 |

          

        
        
          

**Response body for GET**

          
: [BRE Guardrails](./connect_responses_bre_guardrails.htm.md)
