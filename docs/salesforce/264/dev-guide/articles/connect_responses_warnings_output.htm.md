---
page_id: connect_responses_warnings_output.htm
title: Warnings
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_warnings_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Warnings

Output representation of a group of warning messages with the same warning
    code.

      
        
          

**JSON example**

          
: This example shows a group of warning messages with the same warning
            code.

```
{
  "warnings": [
    {
      "warningCode": "PERFORMANCE_SUBOPTIMAL",
      "warningMessages": [
        {
          "warningMessage": "PUR and RCE date ranges could be optimized for better performance",
          "warningDetails": []
        }
      ]
    }
  ]
}
```

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `warningCode` | String | Standardized warning code. For example, `PERFORMANCE_SUBOPTIMA`L. | Big, 66.0 | 66.0 |
| `warningMessages` | [Warning Message](./connect_responses_warning_message_output.htm.md)[] | List of warning messages for records that triggered with this warning. | Big, 66.0 | 66.0 |
