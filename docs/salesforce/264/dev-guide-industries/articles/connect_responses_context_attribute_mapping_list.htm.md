---
page_id: connect_responses_context_attribute_mapping_list.htm
title: Context Attribute Mapping List
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_attribute_mapping_list.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Attribute Mapping List

Output representation of list of context attribute mappings.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextAttributeMappingListId` | String | Unique ID. Required for LDS. | Small, 59.0 | 59.0 |
| `contextAttributeMappings` | [Context Attribute Mapping](./connect_responses_context_attribute_mapping.htm.md)[] | List of context attribute mappings. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the request is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
