---
page_id: connect_responses_context_tag_data.htm
title: Context Tag Data
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_tag_data.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-11-23
---

# Context Tag Data

Output representation of context tag data.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `dataPath` | String[] | The path in the context data structure to the tag's location. | Small, 59.0 | 59.0 |
| `tagValue` | [Object](./connect_responses_query_tags.htm.md "Output representation of query tags result.") | The value of the tag, which can be nested if the tag corresponds to an object with multiple attributes. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_tag_data.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
