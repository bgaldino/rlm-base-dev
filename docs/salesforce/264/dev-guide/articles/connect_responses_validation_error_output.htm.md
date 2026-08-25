---
page_id: connect_responses_validation_error_output.htm
title: Validation Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_validation_error_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Validation Error

Output representation of the validation errors grouped by rule name.

      
        
          

**JSON example**

          
: This example shows a validation error grouped by rule
            name.

```
{
  "validationErrors": [
    {
      "ruleName": "Usage vs Rating Effectivity",
      "errors": [
        {
          "errorCode": "EFFECTIVITY_MISMATCH",
          "errorMessages": []
        }
      ]
    }
  ]
}
```

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `ruleName` | String | Name of the validation rule. For example, `Usage vs Rating Effectivity`. | Big, 66.0 | 66.0 |
| `errors` | [Errors](./connect_responses_errors_output.htm.md)[] | List of error code groups for this validation. | Big, 66.0 | 66.0 |
