---
page_id: connect_responses_object_with_reference_response.htm
title: Object Reference
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_object_with_reference_response.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Object Reference

Output representation of an sObject with a reference ID along with any potential
    error.

    
      
        
          

**Sample Response**

          
: 
            

```
{
  "referenceid": "refQuote",
  "record": {
    "attributes": {
      "type": "Quote",
      "method": "POST"
    },
    "quantity": "2"
  },
  "error": {
    "errorCode": "INVALID_API_INPUT",
    "message": "Reference Id format is irrelevant."
  }
}
```

          

        
      

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `referenceId` | String | ID that identifies the specific Salesforce object that’s returned in the API response. | Small, 59.0 | 59.0 |
| `record` | Map<String, Object> | The sObject record data represented as a map of attribute names to their values. | Small, 59.0 | 59.0 |
| `error` | [https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/connect_responses_error_response.htm](https://developer.salesforce.com/docs/atlas.en-us.264.0.chatterapi.meta/chatterapi/connect_responses_error_response.htm)[] | Detailed information about any error associated with the sObject in the response. | Small, 59.0 | 59.0 |
