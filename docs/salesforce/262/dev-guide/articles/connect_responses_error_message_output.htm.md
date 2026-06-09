---
page_id: connect_responses_error_message_output.htm
title: Error Message
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_error_message_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Error Message

Output representation of the details of records that failed with this specific
error.

JSON example
:   This example shows an error message with
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
| `errorDetails` | [Error Warning Details](./connect_responses_error_warning_details_output.htm.md "Output representation of the individual warning or error message with associated record details.")[] | Details of records that failed with this specific error. | Big, 66.0 | 66.0 |
