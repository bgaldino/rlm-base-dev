---
page_id: connect_responses_query_tags_result.htm
title: Query Tags Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_query_tags_result.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Query Tags Result

Output representation of the results when querying context tags.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `isDone` | Boolean | Indicates whether the tag query process is complete `(true)` or not `(false)`. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates if the query was successful `(true)` or not `(false)`. | Small, 59.0 | 59.0 |
| `queryResult` | [Map<String, ContextTagDataRepresentation>>](./connect_responses_context_tag_data.htm.md "Output representation of context tag data.") | Contains a mapping of each queried tag to its results. | Small, 59.0 | 59.0 |
