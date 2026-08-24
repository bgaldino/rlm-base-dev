---
page_id: connect_resources_get_pricing_simulation_data_with_variables.htm
title: Pricing Simulation Input Variables With Data (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_pricing_simulation_data_with_variables.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Pricing Simulation Input Variables With Data (GET)

Get details of the pricing simulation input variables along with
      associated data.

    
      
        
          

**Resource**

          
: 
            

```
/connect/core-pricing/simulationInputVariablesWithData
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/simulationInputVariablesWithData?expressionSetVersionId=9QMxx0000004CDsGAM&entityId=0Q0xx0000004C92CAE&contextDefinitionId=SalesTransactionContext__stdctx&contextMappingId=QuoteEntitiesMapping
```

          

        
        
          

**Available version**

          
: 64.0

        
        
          

**HTTP methods**

          
: GET

        
        
          

**Request parameters for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `context​DefinitionId` | String | ID or developer name of the context definition. | Required | 64.0 |
| `contextMapping​Id` | String | ID or name of the context mapping that's used. | Required | 64.0 |
| `entityId` | String | ID of a quote or an order. | Required | 64.0 |
| `expressionSet​VersionId` | String | ID of the expression set that starts with `9QM`. | Required | 64.0 |

          

        
        
          

**Response body for GET**

          
: [Pricing Simulation
              Input Variables With Data](./connect_responses_pricing_simulation_input_variables_with_data_output.htm.md)
