---
page_id: connect-responses-usage-detail-error-response
title: Usage Details Error Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-usage-detail-error-response.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_usage_detail_error_response.htm
fetched_at: 2026-11-25
---

# Usage Details Error Response

Output representation of the details of an error related to usage details.

## JSON Example

```
{
   "errors": [
        {
            "referenceId": "MyOrderItem",
            "errorCode": "INVALID_API_INPUT",
            "message": "Something has failed"
        }
   ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code associated with the error. | Small, 63.0 | 63.0 |
| `message` | String | Message associated with the error. | Small, 63.0 | 63.0 |
| `referenceId` | String | Unique ID that’s associated with the specific error for tracking and reference purposes. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-usage-detail-error-response.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
