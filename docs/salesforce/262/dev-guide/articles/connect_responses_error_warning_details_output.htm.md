---
page_id: connect_responses_error_warning_details_output.htm
title: Error Warning Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_error_warning_details_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Error Warning Details

Output representation of the individual warning or error message with associated record details.

JSON example
:   This example shows error details with record
    information.

    ```
    {
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
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `relatedObjectAPIName` | String | API name of the related object. | Big, 66.0 | 66.0 |
| `records` | [Record Details](./connect_responses_record_details_output.htm.md "Output representation of the record details including ID and name.")[] | Details of records that triggered the specific warning or error. | Big, 66.0 | 66.0 |
