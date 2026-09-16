---
page_id: connect_responses_error_message_output.htm
title: Error Message
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_error_message_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Error Message

Output representation of the details of records that failed with this specific
    error.

      
        
          

**JSON example**

          
: This example shows an error message with
            details.

```
{
  "errorMessages": [
    {
      "errorMessage": "PUR and RCE effective date ranges must have overlap for proper rating functionality",
      "errorDetails": [
        {
          "relatedObjectAPIName": "ProductUsageRule",
          "records": [
            {
              "id": "a0bxx0000004CqZAAU",
              "name": "PUR-001"
            }
          ]
        }
      ]
    }
  ]
}
```

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorMessage` | String | Human-readable error message that describes the validation failure. | Big, 66.0 | 66.0 |
| `errorDetails` | [Error Warning Details](./connect_responses_error_warning_details_output.htm.md)[] | Details of records that failed with this specific error. | Big, 66.0 | 66.0 |
