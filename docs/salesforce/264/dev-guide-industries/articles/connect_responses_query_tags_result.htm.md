---
page_id: connect_responses_query_tags_result.htm
title: Query Tags Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_query_tags_result.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Query Tags Result

Output representation of the results when querying context tags.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `isDone` | Boolean | Indicates whether the tag query process is complete `(true)` or not `(false)`. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates if the query was successful `(true)` or not `(false)`. | Small, 59.0 | 59.0 |
| `queryResult` | [Map<String, ContextTagDataRepresentation>>](./connect_responses_context_tag_data.htm.md) | Contains a mapping of each queried tag to its results. | Small, 59.0 | 59.0 |
