---
page_id: connect_resources_view_ramp_deal.htm
title: View Ramp Deal (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_view_ramp_deal.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# View Ramp Deal (GET)

View a ramp deal related to a quote line item or an order
    item.

    
This API request retrieves the segments if the ramp deal already exists.

#### Note

This API is applicable when you're working with line
          ramps. To work with ramp deals for groups, you must use the Place Sales Transaction API
          and specify the `groupRampActions` property.

    
      
        
          

**Resource**

          
: 
            

```
/connect/revenue-management/sales-transaction-contexts/resourceId/actions/ramp-deal-view
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/revenue-management/sales-transaction-contexts/0QLxx0000004CSOGA2/actions/ramp-deal-view?transactionId=0Q0xx0000004CDxCAM&transactionLineId=0QLxx0000004CSOGA2
```

          

        
        
          

**Available version**

          
: 62.0

        
        
          

**HTTP methods**

          
: GET

        
        
          

**Path parameter for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `resourceId` | String | ID of the quote line item, order item, or context. | Required | 62.0 |

          

        
        
          

**Request parameters for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `transaction​Id` | String | ID of the quote or order required to hydrate the context and retrieve the quote lines. | Required | 62.0 |
| `transaction​LineId` | String | ID of the quote or order line required to retrieve the segmented details. | Required | 62.0 |

          

        
        
          

**Response body for GET**

          
: [Ramp Deal
              Service](./connect_responses_ramp_deal_service_output.htm.md)
