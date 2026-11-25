---
page_id: connect-responses-error-response
title: Error Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-error-response.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_error_response.htm
fetched_at: 2026-11-25
---

# Error Response

Output representation of the error details encountered during the API request.

## JSON Example

This example shows a sample error response.

```
{
  "errors": [
    {
      "errorCode": "INVALID_STATUS",
      "message": "CreditMemo 50gxx00000000XtAAI is not in the Posted status."
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code that indicates the type of error. | Big, 66.0 | 66.0 |
| `message` | String | Message stating the reason for error, if any. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-error-response.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
