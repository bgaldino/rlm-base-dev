---
page_id: connect-responses-generic-error-output
title: Generic Error Details
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-generic-error-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_generic_error_output.htm
fetched_at: 2026-11-25
---

# Generic Error Details

Output representation of the error details encountered during the API request.

## JSON Example

```
{
  "data": [],
  "error": {
    "errorCode": "INVALID_API_INPUT",
    "message": "Liable summary IDs cannot be null or empty."
  },
  "success": false
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Error code that represents the type of error. | Big, 67.0 | 67.0 |
| `message` | String | Detailed error message that specifies the cause of failure. | Big, 67.0 | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-generic-error-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
