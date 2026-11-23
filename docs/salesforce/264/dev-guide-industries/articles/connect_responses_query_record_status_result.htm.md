---
page_id: connect_responses_query_record_status_result.htm
title: Query Record Status Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_query_record_status_result.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-11-23
---

# Query Record Status Result

Output representation of query result status of context data records.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextRecordStatusListId` | String | Unique ID associated with the list of context record status required for Lightning Data Service. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the status retrieval of context data query records was successful `(true)` or not `(false)`. | Small, 59.0 | 59.0 |
| `queryResult` | [Context Data Record Status](./connect_responses_context_data_record_status.htm.md "Output representation of context data record status.")[] | List containing the status of the queried context data records. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_query_record_status_result.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
