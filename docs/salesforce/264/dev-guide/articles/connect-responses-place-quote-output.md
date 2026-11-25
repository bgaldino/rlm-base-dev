---
page_id: connect-responses-place-quote-output
title: Place Quote
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-place-quote-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_place_quote_output.htm
fetched_at: 2026-11-25
---

# Place Quote

Output representation of the request to create or update a quote.

## JSON Example

This example shows a sample response of the place quote request.

```
{
    "quoteId": "0Q0xx0000004E2mCAE",
    "requestIdentifier": "95Txx0000004Cx2",
    "responseError": [],
    "statusURL": "/services/data/v60.0/sobjects/RevenueAsyncOperation/95Txx0000004Cx2EAE",
    "success": true
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `quoteId` | String | ID of the quote created after a successful request. | Small, 60.0 | 60.0 |
| `request​Identifier` | String | Unique request identifier that can be used to poll the async request. | Big, 60.0 | 60.0 |
| `response​Error` | [Place Quote Error Response](./connect-responses-place-quote-error-response.md) [] | List of errors encountered during the synchronous processing. | Small, 60.0 | 60.0 |
| `status​URL` | String | Asynchronous status URL to track the operation, if available. | Big, 60.0 | 60.0 |
| `success` | Boolean | Indicates whether the synchronous part of the processing is successful (`true`) or not (`false`). | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-place-quote-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
