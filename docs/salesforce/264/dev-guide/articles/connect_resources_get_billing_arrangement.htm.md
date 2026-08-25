---
page_id: connect_resources_get_billing_arrangement.htm
title: Billing Arrangement (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_billing_arrangement.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Billing Arrangement (GET)

Retrieve a billing arrangement and its associated billing arrangement
    lines.

    
      

This API fetches billing information, including the split percentage allocation for
        accounts, the remainder percentage, and whether adjustments are applied to the owning
        account.

    

    
      
        
          

**Resource**

          
: 
            

```
/revenue/billing/billing-arrangement/billingArrangementId
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/revenue/billing/billing-arrangement//revenue/billing/billing-arrangement/1bdxx000000004rAAA
```

          

        
        
          

**Available version**

          
: 66.0

        
        
          

**HTTP methods**

          
: GET

        
        
          

**Request parameter for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billing​ArrangementId` | String | Unique ID of the billing arrangement to retrieve. | Required | 66.0 |

          

        
        
          

**Response body for GET**

          
: [Billing Arrangement](./connect_responses_billing_arrangement_output.htm.md)
