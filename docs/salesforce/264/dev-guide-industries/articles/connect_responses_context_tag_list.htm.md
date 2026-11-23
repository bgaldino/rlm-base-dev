---
page_id: connect_responses_context_tag_list.htm
title: Context Tag List Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_tag_list.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-11-23
---

# Context Tag List Output

Output representation of list of context tags.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionId` | String | ID of the context definition created. | Small, 59.0 | 59.0 |
| `contextTagListId` | String | Unique ID. Required for LDS. | Small, 59.0 | 59.0 |
| `contextTags` | [Context Attribute Tag Output](./connect_responses_context_attribute_tag.htm.md "Output representation of context attribute tag.")[] | List of context tags. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_tag_list.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
