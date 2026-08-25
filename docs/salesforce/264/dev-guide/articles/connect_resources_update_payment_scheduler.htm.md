---
page_id: connect_resources_update_payment_scheduler.htm
title: Payment Scheduler Update (PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_update_payment_scheduler.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Payment Scheduler Update (PATCH)

Activate or deactivate a payment scheduler. You can set the status of
      a payment scheduler to `Active`, `Canceled`, `Draft`, or
        `Inactive`.

    
      
        
          

**Special Access Rules**

          
: You need the Payment Ops permission set to use this API.

        
        
          

**Resource**

          
: 
            

```
/commerce/payments/payment-schedulers/billingBatchSchedulerId
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/payments/payment-schedulers/5BSxx0000004TwGGAU
```

          

        
        
          

**Available version**

          
: 64.0

        
        
          

**HTTP methods**

          
: PATCH

        
        
          

**Path parameter for POST**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billingBatch​SchedulerId` | String | ID of the payment scheduler record. | Required | 64.0 |

          

        
        
          

**Request body for PATCH**

          
: 
            
        
          

**JSON example**

          
: 
            
              
                

**JSON example**

                
: 
                  

```
{
  "status": "Active"
}
```

                

              
            

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

- 
- 
- 
- 

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `status` | String | Status that must be set to activate or deactivate a payment scheduler. Valid values are: `Active` `Canceled` `Draft` `Inactive` | Required | 64.0 |

          

        
      

          

        
        
          

**Response body for PATCH**

          
: [Payments Scheduler
              Update](./connect_responses_payment_scheduler_update_output.htm.md)
