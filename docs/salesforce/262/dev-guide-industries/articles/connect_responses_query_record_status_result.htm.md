---
page_id: connect_responses_query_record_status_result.htm
title: Query Record Status Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_query_record_status_result.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Query Record Status Result

Output representation of query result status of context data records.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextRecordStatusListId` | String | Unique ID associated with the list of context record status required for Lightning Data Service. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the status retrieval of context data query records was successful `(true)` or not `(false)`. | Small, 59.0 | 59.0 |
| `queryResult` | [Context Data Record Status](./connect_responses_context_data_record_status.htm.md "Output representation of context data record status.")[] | List containing the status of the queried context data records. | Small, 59.0 | 59.0 |
