---
page_id: connect_responses_place_sales_transaction_error_response.htm
title: Sales Transaction Error Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_place_sales_transaction_error_response.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Sales Transaction Error Response

Output representation of the error details associated with the API request.

    

        
          

**JSON example**

          
: 
            

```
{
  "errorResponse": {
    "errorCode": "INVALID_API_INPUT",
    "message": "Include record type and method in the request and try again.",
    "referenceId": "refQuoteItem2"
  }
}
```

          

        
      

    
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code for the resultant error. | Small, 63.0 | 63.0 |
| `message` | String | Error message for the resultant error. | Small, 63.0 | 63.0 |
| `referenceId` | String | Unique ID that’s associated with the specific error for tracking and reference purposes. | Small, 63.0 | 63.0 |
