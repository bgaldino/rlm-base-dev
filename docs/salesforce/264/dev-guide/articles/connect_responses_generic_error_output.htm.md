---
page_id: connect_responses_generic_error_output.htm
title: Generic Error Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_generic_error_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Generic Error Details

Output representation of the error details encountered during the API
    request.

      
        
          

**JSON example**

          
: 
            

```
{
  "data": [],
  "error": {
    "errorCode": "INVALID_API_INPUT",
    "message": "Liable summary IDs cannot be null or empty."
  },
  "success": false
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Error code that represents the type of error. | Big, 67.0 | 67.0 |
| `message` | String | Detailed error message that specifies the cause of failure. | Big, 67.0 | 67.0 |
