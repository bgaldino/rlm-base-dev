---
page_id: connect_responses_context_tag_data.htm
title: Context Tag Data
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_tag_data.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Tag Data

Output representation of context tag data.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `dataPath` | String[] | The path in the context data structure to the tag's location. | Small, 59.0 | 59.0 |
| `tagValue` | [Object](./connect_responses_query_tags.htm.md) | The value of the tag, which can be nested if the tag corresponds to an object with multiple attributes. | Small, 59.0 | 59.0 |
