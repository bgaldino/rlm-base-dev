---
page_id: connect-responses-query-tags-result
title: Query Tags Result
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-query-tags-result.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
legacy_page_id: connect_responses_query_tags_result.htm
fetched_at: 2026-11-25
---

# Query Tags Result

Output representation of the results when querying context tags.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `isDone` | Boolean | Indicates whether the tag query process is complete `(true)` or not `(false)`. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates if the query was successful `(true)` or not `(false)`. | Small, 59.0 | 59.0 |
| `queryResult` | [Map<String, ContextTagDataRepresentation>>](./connect-responses-context-tag-data.md) | Contains a mapping of each queried tag to its results. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-query-tags-result.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
