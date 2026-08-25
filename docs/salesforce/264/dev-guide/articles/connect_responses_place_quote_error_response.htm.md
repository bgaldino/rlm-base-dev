---
page_id: connect_responses_place_quote_error_response.htm
title: Place Quote Error Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_place_quote_error_response.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Place Quote Error Response

Output representation of the error responses of a place quote request.

      
        
          

**JSON Example**

          
: 
            

```
{
 "errorCode": "INVALID_API_INPUT",
 "message": "Include record type and method in the request and try again.",
 "referenceId": "refQuoteItem2"
 }
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​Code` | String | Error code representing the type of error encountered in the create place quote request. | Small, 60.0 | 60.0 |
| `message` | String | Message stating the reason for the error, if any. | Small, 60.0 | 60.0 |
| `reference​Id` | String | Reference ID associated with the specific error instance for tracking and reference purposes. | Small, 60.0 | 60.0 |
