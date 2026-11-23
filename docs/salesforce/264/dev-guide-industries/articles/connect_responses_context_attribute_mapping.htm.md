---
page_id: connect_responses_context_attribute_mapping.htm
title: Context Attribute Mapping
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_attribute_mapping.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-11-23
---

# Context Attribute Mapping

Output representation of the context attribute mapping.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| contextAttr​ContextHydration​DetailList | Context Attribute Hydration Detail[] | List of the context attribute hydration records when context-to-context mappings exist. | Small, 61.0 | 61.0 |
| `context​AttrHydration​DetailList` | Context Attribute Hydration Detail[] | Details of the context attribute hydration. | Small, 59.0 | 59.0 |
| `context​AttributeId` | String | ID of the context attribute record. | Small, 59.0 | 59.0 |
| `contextAttribute​MappingId` | String | ID of the context attribute mapping record. | Small, 59.0 | 59.0 |
| `contextInput​AttributeName` | String | Input attribute name. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `parentNode​MappingId` | String | ID of the parent context node mapping record. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_attribute_mapping.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
