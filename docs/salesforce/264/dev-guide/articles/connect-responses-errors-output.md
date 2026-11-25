---
page_id: connect-responses-errors-output
title: Errors
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-errors-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_errors_output.htm
fetched_at: 2026-11-25
---

# Errors

Output representation of the group of error messages with the same error code.

## JSON Example

This example shows a group of error messages with the same error code.

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
| `errorMessages` | [Error Message](./connect-responses-error-message-output.md)[] | List of error messages for records that failed with this error code. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-errors-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
