---
page_id: connect-responses-context-tag-list
title: Context Tag List Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-tag-list.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
legacy_page_id: connect_responses_context_tag_list.htm
fetched_at: 2026-11-25
---

# Context Tag List Output

Output representation of list of context tags.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionId` | String | ID of the context definition created. | Small, 59.0 | 59.0 |
| `contextTagListId` | String | Unique ID. Required for LDS. | Small, 59.0 | 59.0 |
| `contextTags` | [Context Attribute Tag Output](./connect-responses-context-attribute-tag.md)[] | List of context tags. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-tag-list.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
