---
page_id: connect-responses-place-quote-error-response
title: Place Quote Error Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-place-quote-error-response.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_place_quote_error_response.htm
fetched_at: 2026-11-25
---

# Place Quote Error Response

Output representation of the error responses of a place quote request.

## JSON Example

```
{
 "errorCode": "INVALID_API_INPUT",
 "message": "Include record type and method in the request and try again.",
 "referenceId": "refQuoteItem2"
 }
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​Code` | String | Error code representing the type of error encountered in the create place quote request. | Small, 60.0 | 60.0 |
| `message` | String | Message stating the reason for the error, if any. | Small, 60.0 | 60.0 |
| `reference​Id` | String | Reference ID associated with the specific error instance for tracking and reference purposes. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-place-quote-error-response.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
