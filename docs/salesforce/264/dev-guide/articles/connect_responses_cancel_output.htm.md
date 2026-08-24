---
page_id: connect_responses_cancel_output.htm
title: Cancellation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_cancel_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Cancellation

Output representation of the details of a cancellation record.

      
        
          

**JSON example**

          
: 
            

```
{
  "cancellationRecordId": "0Q0xx0000004NsSCAU",
  "errors": [
    {
      "errorCode": "REQUIRED_FIELD_MISSING",
      "errorMessage": "Specify a value for quantityChange, and try again."
    }
  ],
  "requestId": "16Pxx0000004NIy",
  "success": true
}
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `cancellation​RecordId` | String | ID of the cancellation record that’s created for a quote or an order. | Small, 62.0 | 62.0 |
| `errors` | [ARC Base Error](./connect_responses_assets_arc_error.htm.md)[] | Error responses if the creation of a cancellation record fails. | Small, 62.0 | 62.0 |
| `requestId` | String | Request ID that’s used to track the async request. | Small, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
