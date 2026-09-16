---
page_id: connect_responses_place_order_output.htm
title: Place Order Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_place_order_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Place Order Response

Output representation of the request to create or update an order.

        
          

**JSON example**

          
: 
            

```
{
  "requestId": "16PRM0000004DBq",
  "orderId": "801S70000001VKgIAM",
  "success": true,
  "errors": [],
  "statusURL": "/services/data/vXX.X/sobjects/AsyncOperationTracker/16PRM0000004DBq"
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              
              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Place Order​Error​Response](./connect_responses_place_order_error_response.htm.md)[] | List of errors encountered during the synchronous processing. | Small, 60.0 | 60.0 |
| `orderId` | String | ID of the order created after a successful request. | Small, 60.0 | 60.0 |
| `requestId` | String | Request ID of the process to query asynchronous status of the place order API. | Small, 60.0 | 60.0 |
| `status​URL` | String | Asynchronous status URL of the request, if available. | Small, 60.0 | 60.0 |
| `success` | Boolean | Indicates whether the synchronous part of the processing is successful (`true`) or not (`false`). | Small, 60.0 | 60.0 |
