---
page_id: connect_responses_context_attribute_mapping_list.htm
title: Context Attribute Mapping List
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_attribute_mapping_list.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Context Attribute Mapping List

Output representation of list of context attribute mappings.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextAttributeMappingListId` | String | Unique ID. Required for LDS. | Small, 59.0 | 59.0 |
| `contextAttributeMappings` | [Context Attribute Mapping](./connect_responses_context_attribute_mapping.htm.md "Output representation of the context attribute mapping.")[] | List of context attribute mappings. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the request is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
