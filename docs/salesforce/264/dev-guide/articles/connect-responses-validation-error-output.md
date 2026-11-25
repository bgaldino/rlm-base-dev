---
page_id: connect-responses-validation-error-output
title: Validation Error
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-validation-error-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_validation_error_output.htm
fetched_at: 2026-11-25
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
| `errors` | [Errors](./connect-responses-errors-output.md)[] | List of error code groups for this validation. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-validation-error-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
