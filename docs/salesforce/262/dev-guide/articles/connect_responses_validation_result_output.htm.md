---
page_id: connect_responses_validation_result_output.htm
title: Validation Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_validation_result_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Validation Result

Output representation of the validation results grouped by rule name.

JSON example
:   This example shows a validation result with errors and
    warnings.

    ```
    {
      "validationResult": {
        "validationErrors": [
          {
            "ruleName": "Usage vs Rating Effectivity",
            "errors": []
          }
        ],
        "validationWarnings": [
          {
            "ruleName": "Performance Optimization",
            "warnings": []
          }
        ]
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `validationErrors` | [Validation Error](./connect_responses_validation_error_output.htm.md "Output representation of the validation errors grouped by rule name.")[] | List of validation errors grouped by rule name. | Big, 66.0 | 66.0 |
| `validationWarnings` | [Validation Warning](./connect_responses_validation_warning_output.htm.md "Output representation of the validation warnings grouped by rule name.")[] | List of validation warnings grouped by rule name. | Big, 66.0 | 66.0 |
