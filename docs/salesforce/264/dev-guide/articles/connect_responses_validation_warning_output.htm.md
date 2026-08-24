---
page_id: connect_responses_validation_warning_output.htm
title: Validation Warning
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_validation_warning_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Validation Warning

Output representation of the validation warnings grouped by rule name.

      
        
          

**JSON example**

          
: This example shows a validation warning grouped by rule
            name.

```
{
  "validationWarnings": [
    {
      "ruleName": "Performance Optimization",
      "warnings": [
        {
          "warningCode": "PERFORMANCE_SUBOPTIMAL",
          "warningMessages": []
        }
      ]
    }
  ]
}
```

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `ruleName` | String | Name of the validation rule. For example, `Performance Optimization`. | Big, 66.0 | 66.0 |
| `warnings` | [Warnings](./connect_responses_warnings_output.htm.md)[] | List of warning code groups for this validation. | Big, 66.0 | 66.0 |
