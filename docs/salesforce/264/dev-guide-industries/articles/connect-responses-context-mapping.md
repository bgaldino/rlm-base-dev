---
page_id: connect-responses-context-mapping
title: Context Mapping Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-mapping.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
legacy_page_id: connect_responses_context_mapping.htm
fetched_at: 2026-11-25
---

# Context Mapping Output

Output representation of context mapping.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionVersionID` | String | ID of the context definition version. | Small, 59.0 | 59.0 |
| `contextMappingID` | String | ID of the context mapping. | Small, 59.0 | 59.0 |
| `contextNodeMappings` | [Context Node Mapping](./connect-responses-context-node-mapping.md)[] | List of context node mappings. | Small, 59.0 | 59.0 |
| `description` | String | Description of context mapping. | Small, 59.0 | 59.0 |
| `isDefault` | Boolean | Specifies if you want to make it the default mapping for context definition (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isInputMapped` | Boolean | Indicates whether the specified context mapping details are mapped with the source (`true`) or not (`false`). | Small, 61.0 | 61.0 |
| `isSuccess` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `intents` | List<String> | Context mapping that’s associated with the usage of the `intents`. | Small, 61.0 | 61.0 |
| `mappedContext​DefinitionName` | String | API name of the context definition when context-to-context mappings exist. | Small, 61.0 | 61.0 |
| `name` | String | Name of the context mapping. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-mapping.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
