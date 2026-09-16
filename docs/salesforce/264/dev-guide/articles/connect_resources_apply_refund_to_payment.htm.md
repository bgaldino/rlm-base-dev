---
page_id: connect_resources_apply_refund_to_payment.htm
title: Refund Line Apply (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_apply_refund_to_payment.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Refund Line Apply (POST)

Make a refund transaction against a payment.

    
      
        
          

**Resource**

          
: 
            

```
/commerce/billing/refunds/refundId/actions/apply
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/billing/refunds/0cbVc0000000G4nIAE/actions/apply
```

          

        
        
          

**Available version**

          
: 64.0

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Path parameter for POST**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `refundId` | String | ID of the refund record. | Required | 64.0 |

          

        
        
          

**Request body for POST**

          
: 
            

**JSON example**

: 

```
{
  "appliedToId": "0aQR00000004ZkKMAU",
  "amount": 10,
  "effectiveDate": "2020-08-11T07:53:15.000Z",
  "comments": "Payment application."
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `amount` | Double | Amount to refund. | Required | 64.0 |
| `appliedToId` | String | ID of a payment or credit memo record. The refund is applied to this object. | Required | 64.0 |
| `comments` | String | Additional details of the refund request. | Optional | 64.0 |
| `effectiveDate` | String | Date from when the refund is in effect. | Optional | 64.0 |

          

        
        
          

**Response body for POST**

          
: [Refund Line
              Apply](./connect_responses_refund_line_apply_output.htm.md)
