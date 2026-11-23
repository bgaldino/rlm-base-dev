---
page_id: connect_responses_context_definition_version.htm
title: Context Definition Version
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_version.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-11-23
---

# Context Definition Version

Output representation of context definition version.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionId` | String | ID of context definition. | Small, 59.0 | 59.0 |
| `contextDefinitionVersionId` | String | ID of context definition version. | Small, 59.0 | 59.0 |
| `contextMappings` | [Context Mapping[]](./connect_responses_context_mapping.htm.md "Output representation of context mapping.") | List of context mappings. | Small, 59.0 | 59.0 |
| `contextNodes` | [Context Node[]](./connect_responses_context_node.htm.md "Output representation of the details of context nodes.") | List of context nodes. | Small, 59.0 | 59.0 |
| `endDate` | String | End date till context definition version is valid. | Small, 59.0 | 59.0 |
| `isActive` | Boolean | Specifies if the context definition version is active (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isEditable` | Boolean | Specifies if the context definition version is editable (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Specifies if the operation is success (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `startDate` | String | Start date from when context definition version is valid. | Small, 59.0 | 59.0 |
| `versionNumber` | Integer | Version number. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_version.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
