---
page_id: connect_responses_context_tag_list.htm
title: Context Tag List Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_tag_list.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Context Tag List Output

Output representation of list of context tags.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionId` | String | ID of the context definition created. | Small, 59.0 | 59.0 |
| `contextTagListId` | String | Unique ID. Required for LDS. | Small, 59.0 | 59.0 |
| `contextTags` | [Context Attribute Tag Output](./connect_responses_context_attribute_tag.htm.md "Output representation of context attribute tag.")[] | List of context tags. | Small, 59.0 | 59.0 |
