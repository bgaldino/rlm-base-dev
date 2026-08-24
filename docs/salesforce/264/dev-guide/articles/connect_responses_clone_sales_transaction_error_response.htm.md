---
page_id: connect_responses_clone_sales_transaction_error_response.htm
title: Clone Sales Transaction Error Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_clone_sales_transaction_error_response.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Clone Sales Transaction Error Response

Output representation of the errors that occur during the clone sales transaction
    operation.

    
      
        
          

**JSON example**

          
: 
            

```
{
  "errors": [
    {
      "errorCode": "INVALID_API_INPUT",
      "message": "Specify only one record",
      "referenceId": "0QLxx0000004CBYGA2"
    }
  ]
}
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                  
                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `errorCode` | String | Code associated with the error. | 64.0 |
| `message` | String | Message associated with the error. | 64.0 |
| `referenceId` | String | Reference ID associated with the error. | 64.0 |
