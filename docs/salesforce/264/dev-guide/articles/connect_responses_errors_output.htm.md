---
page_id: connect_responses_errors_output.htm
title: Errors
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_errors_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Errors

Output representation of the group of error messages with the same error code.

      
        
          

**JSON example**

          
: This example shows a group of error messages with the same error
            code.

```
{
  "errors": [
    {
      "errorCode": "EFFECTIVITY_MISMATCH",
      "errorMessages": [
        {
          "errorMessage": "PUR and RCE effective date ranges must have overlap for proper rating functionality",
          "errorDetails": []
        }
      ]
    }
  ]
}
```

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Standardized error code. For example, `EFFECTIVITY_MISMATCH`. | Big, 66.0 | 66.0 |
| `errorMessages` | [Error Message](./connect_responses_error_message_output.htm.md)[] | List of error messages for records that failed with this error code. | Big, 66.0 | 66.0 |
