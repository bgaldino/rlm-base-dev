---
page_id: connect_responses_query_record_status_result.htm
title: Query Record Status Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_query_record_status_result.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Query Record Status Result

Output representation of query result status of context data records. 

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextRecordStatusListId` | String | Unique ID associated with the list of context record status required for Lightning Data Service. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the status retrieval of context data query records was successful `(true)` or not `(false)`. | Small, 59.0 | 59.0 |
| `queryResult` | [Context Data Record Status](./connect_responses_context_data_record_status.htm.md)[] | List containing the status of the queried context data records. | Small, 59.0 | 59.0 |
