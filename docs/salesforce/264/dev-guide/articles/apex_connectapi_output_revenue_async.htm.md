---
page_id: apex_connectapi_output_revenue_async.htm
title: ConnectApi.RevenueAsyncRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_revenue_async.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.RevenueAsyncRepresentation

Output representation of the result of the API request with the request
    identifier.

    
      

          
          
          
          
          
            
              

              

              

              

            

          

          
            
              

              

              

              

            

            
              

              

              

              

            

            
              

              

              

              

            

          

        
| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `errors` | List<[ConnectApi.ErrorResponse](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexref.meta/apexref/apex_connectapi_output_error_response.htm)> | Details of errors, if any. | 62.0 |
| `request​​Identifier` | String | Unique identifier of the request. | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | 62.0 |
