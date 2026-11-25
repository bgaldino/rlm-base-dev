---
page_id: connect-responses-validation-result-output
title: Validation Result
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-validation-result-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_validation_result_output.htm
fetched_at: 2026-11-25
---

# Validation Result

Output representation of the validation results grouped by rule name.

## JSON Example

This example shows a validation result with errors and warnings.

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
| `validationErrors` | [Validation Error](./connect-responses-validation-error-output.md)[] | List of validation errors grouped by rule name. | Big, 66.0 | 66.0 |
| `validationWarnings` | [Validation Warning](./connect-responses-validation-warning-output.md)[] | List of validation warnings grouped by rule name. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-validation-result-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
