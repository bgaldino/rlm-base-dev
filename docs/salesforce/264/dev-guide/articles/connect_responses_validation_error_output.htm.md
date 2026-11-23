---
page_id: connect_responses_validation_error_output.htm
title: Validation Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_validation_error_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Validation Error

Output representation of the validation errors grouped by rule name.

## JSON Example

This example shows a validation error grouped by rule name.

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
| `errors` | [Errors](./connect_responses_errors_output.htm.md "Output representation of the group of error messages with the same error code.")[] | List of error code groups for this validation. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_validation_error_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
