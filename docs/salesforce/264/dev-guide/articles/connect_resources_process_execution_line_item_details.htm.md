---
page_id: connect_resources_process_execution_line_item_details.htm
title: Pricing Process Execution for Line Items (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_process_execution_line_item_details.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Pricing Process Execution for Line Items (GET)

Get the pricing execution details for the line items of a pricing
      process by using the execution ID and execution type.

    
      
        
          

**Resource**

          
: 
            

```
/connect/core-pricing/pricing-process-execution/lineitems/executionId/executionType
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/pricing-process-execution/lineitems/29646938297972/Pricing_Line
```

          

        
        
          

**Available version**

          
: 63.0

        
        
          

**HTTP methods**

          
: GET

        
      

      
        
          

**Path parameters for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    
- 
- 

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `executionId` | String | ID of the pricing process execution record. | Required | 63.0 |
| `executionType` | String | Type of the execution that's defined internally within the pricing API. Valid values are: `Pricing_Line` `Discovery_Line` | Required | 63.0 |

          

        
      

      
        
          

**Response body for GET**

          
: [Pricing Process
              Execution Details for Line Items](./connect_responses_process_execution_line_item_details_get_output.htm.md)
