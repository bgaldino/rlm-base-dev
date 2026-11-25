---
page_id: connect-responses-rate-plan-response
title: Rate Plan Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-rate-plan-response.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Rate Management
parent_page: rate-management-business-apis-responses
legacy_page_id: connect_responses_rate_plan_response.htm
fetched_at: 2026-11-25
---

# Rate Plan Response

Output representation of the details of a rate plan.

## JSON Example

```
{
  "success": true,
  "executionId" : "a521d592-71c3-4db3-8048-r64504df1605",
  "error": {}
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Rating Error Response](./connect-responses-rating-error-response.md)[] | Error response for the API request, if any. | Small, 62.0 | 62.0 |
| `executionId` | String | ID of the procedure execution record. | Small, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the request is successful (`true`) or not (`false`) | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-rate-plan-response.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
