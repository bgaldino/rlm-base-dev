---
page_id: connect_resources_execution_logs.htm
title: API Execution Logs (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_execution_logs.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# API Execution Logs (GET)

Get the log details of a pricing API execution record by using the
      execution ID.

    
      
        
          

**Resource**

          
: 
            

```
/connect/core-pricing/apiexecutionlogs/executionId
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/apiexecutionlogs/29646938297972
```

          

        
        
          

**Available version**

          
: 63.0

        
        
          

**HTTP methods**

          
: GET

        
        
          

**Path parameter for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `executionId` | String | ID of the pricing process execution record. | Required | 63.0 |

          

        
        
          

**Response body for GET**

          
: [Pricing Execution
              Waterfall Response](./connect_responses_api_execution_waterfall_response.htm.md)
