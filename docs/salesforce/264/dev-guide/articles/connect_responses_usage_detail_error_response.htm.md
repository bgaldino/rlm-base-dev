---
page_id: connect_responses_usage_detail_error_response.htm
title: Usage Details Error Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_usage_detail_error_response.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-11-23
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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_usage_detail_error_response.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
