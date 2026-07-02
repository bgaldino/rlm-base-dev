---
page_id: connect_responses_warnings_output.htm
title: Warnings
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_warnings_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Warnings

Output representation of a group of warning messages with the same warning
code.

JSON example
:   This example shows a group of warning messages with the same warning
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
| `warningMessages` | [Warning Message](./connect_responses_warning_message_output.htm.md "Output representation of the details of records that triggered this specific warning.")[] | List of warning messages for records that triggered with this warning. | Big, 66.0 | 66.0 |
