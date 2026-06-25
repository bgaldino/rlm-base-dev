---
page_id: connect_responses_context_tag_data.htm
title: Context Tag Data
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_tag_data.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Context Tag Data

Output representation of context tag data.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `dataPath` | String[] | The path in the context data structure to the tag's location. | Small, 59.0 | 59.0 |
| `tagValue` | [Object](./connect_responses_query_tags.htm.md "Output representation of query tags result.") | The value of the tag, which can be nested if the tag corresponds to an object with multiple attributes. | Small, 59.0 | 59.0 |
