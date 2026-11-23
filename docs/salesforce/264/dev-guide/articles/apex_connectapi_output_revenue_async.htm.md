---
page_id: apex_connectapi_output_revenue_async.htm
title: ConnectApi.RevenueAsyncRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_revenue_async.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-11-23
---

# ConnectApi.RevenueAsyncRepresentation

Output representation of the result of the API request with the request
identifier.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `errors` | List<[ConnectApi.ErrorResponse](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexref.meta/apexref/apex_connectapi_output_error_response.htm "HTML (New Window)")> | Details of errors, if any. | 62.0 |
| `request​​Identifier` | String | Unique identifier of the request. | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_revenue_async.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
