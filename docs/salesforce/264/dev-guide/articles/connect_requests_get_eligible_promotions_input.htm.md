---
page_id: connect_requests_get_eligible_promotions_input.htm
title: Eligible Promotions Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_get_eligible_promotions_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Eligible Promotions Input

Input representation of the request to get eligible promotions for line items. This
    representation includes the details to accept line item IDs and a sales transaction
    ID.

    
      
        
          

**JSON example**

          
: 
            

```
{
  "salesTransactionId": "0Q0xx0000004EOECA2",
  "lineItemIds": [
    "0QLxx0000004E7eGAE",
    "0QLxx0000004GCeGAM",
    "0QLxx0000004E7gGAE"
  ]
}

```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `lineItemIds` | String[] | List of line item IDs to evaluate for promotions. The object type is auto-determined from the sales transaction ID. | Required | 66.0 |
| `salesTransactionId` | String | The sales transaction ID, such as an order ID or a quote ID, for the promotion evaluation. | Required | 66.0 |
