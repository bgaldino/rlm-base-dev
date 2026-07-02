---
page_id: connect_responses_errors_output.htm
title: Errors
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_errors_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Errors

Output representation of the group of error messages with the same error code.

JSON example
:   This example shows a group of error messages with the same error
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
| `errorMessages` | [Error Message](./connect_responses_error_message_output.htm.md "Output representation of the details of records that failed with this specific error.")[] | List of error messages for records that failed with this error code. | Big, 66.0 | 66.0 |
