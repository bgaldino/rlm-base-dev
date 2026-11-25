---
page_id: apex-connectapi-output-reference-line-error
title: ConnectApi.ReferenceLineError
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-output-reference-line-error.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-output-classes
legacy_page_id: apex_connectapi_output_reference_line_error.htm
fetched_at: 2026-11-25
---

# ConnectApi.ReferenceLineError

Output representation of the details of the line level errors.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `errors` | List<[ConnectApi.ErrorResponse](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_connectapi_output_error_response.htm)> | List of errors with error code and error message for the specified invoice line ID. | 62.0 |
| `reference​LineId` | String | ID of the invoice line specified in the API request that has an issue, causing the API request to fail. | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-output-reference-line-error.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
