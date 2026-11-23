---
page_id: connect_responses_generic_error_output.htm
title: Generic Error Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_generic_error_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-11-23
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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_generic_error_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
