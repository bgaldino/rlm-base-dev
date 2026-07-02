---
page_id: connect_responses_context_node_mapping_list.htm
title: Context Node Mapping List Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_node_mapping_list.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Context Node Mapping List Output

Output representation of list of context node mappings.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextNodeMappingListId` | String | Unique ID. Required for LDS. | Small, 59.0 | 59.0 |
| `contextNodeMappings` | [Context Node Mapping Output[]](./connect_responses_context_node_mapping.htm.md "Output representation of the context node mapping.") | List of context node mappings | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Specifies if the operation is success (`true`) or not (`false`). | Small, 59.0 | 59.0 |
