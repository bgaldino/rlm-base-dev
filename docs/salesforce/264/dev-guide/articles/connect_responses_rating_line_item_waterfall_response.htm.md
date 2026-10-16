---
page_id: connect_responses_rating_line_item_waterfall_response.htm
title: Line Item Waterfall Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_rating_line_item_waterfall_response.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Line Item Waterfall Response

Output representation of the line item waterfall response.

    
      
        
          

**JSON example**

          
: 
            

```
{
       "currencyCode": "USD",
       "error": null,
       "executionEndTimestamp": "2023-07-31T20:11:29.625Z",
       "executionId": "gdLVwn2x1uats2xWMAjV",
       "executionStartTimestamp": null,
       "lineItemId": "item1",
       "success": true,
       "usageType":"Rating",
       "output": {
          "quantity": "10",
          "netUnitPrice": "10",
          "subtotal": "100"
        },
        "waterfall": []
}

```

          

        
      

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `context​Definition​VersionId` | String | Context definition version ID of the rating procedure. | Small, 62.0 | 62.0 |
| `context​MappingId` | String | Context mapping ID of the record. | Small, 62.0 | 62.0 |
| `currency​Code` | String | Currency code. For example, USD or INR. | Small, 62.0 | 62.0 |
| `error` | [Rating Error Response](./connect_responses_rating_error_response.htm.md) | Details of any errors. | Small, 62.0 | 62.0 |
| `execution​End​Timestamp` | String | End timestamp of procedure execution. | Small, 62.0 | 62.0 |
| `execution​Id` | String | Execution ID of a particular execution of a rating procedure. | Small, 62.0 | 62.0 |
| `execution​Start​Timestamp` | String | Start timestamp of procedure execution. | Small, 62.0 | 62.0 |
| `line​ItemId` | String | Line item ID for which the price is being calculated. | Small, 62.0 | 62.0 |
| `output` | Map<String, Object> | Output of the rating procedure. | Small, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `usage​Type` | String | Usage type of the waterfall log record. | Small, 62.0 | 62.0 |
| `waterfall` | [Rating Waterfall Response](./connect_responses_rating_waterfall_response.htm.md)[] | Details of the rating waterfall. | Small, 62.0 | 62.0 |
