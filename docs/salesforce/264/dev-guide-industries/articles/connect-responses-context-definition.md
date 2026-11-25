---
page_id: connect-responses-context-definition
title: Context Definition Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-definition.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
legacy_page_id: connect_responses_context_definition.htm
fetched_at: 2026-11-25
---

# Context Definition Output

Output representation of context definition.

- 
- 
- 

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `activeVersionId` | String | ID of the active context definition version. | Small, 59.0 | 59.0 |
| `canBeReferenceDefinition` | Boolean | Specifies if the context definition can be used as a reference definition to other context definitions (`true`) or not (`false`). | Small, 63.0 | 63.0 |
| `contextDefinitionId` | String | ID of the context definition. | Small, 59.0 | 59.0 |
| `contextDefinitionVersionList` | [Context Definition Version](./connect-responses-context-definition-version.md)[] | List of context definition versions. | Small, 59.0 | 59.0 |
| `contextTtl` | Integer | TTL of the context. | Small, 59.0 | 59.0 |
| `definition` | String | Definition. | Small, 59.0 | 59.0 |
| `definitionType` | String | Type of definition. Possible values are:`standard_executable``standard_nonexecutable``custom_nonexecutable` | Small, 60.0 | 60.0 |
| `developerName` | String | Developer name. | Small, 59.0 | 59.0 |
| `hasSystemTags` | String | Specifies if the context definition has system node and tags attached (`true`) or not (`false`). | Small, 63.0 | 63.0 |
| `interfaces` | String | List of implemented Context Definition Interfaces for this context definition. | Small, 62.0 | 62.0 |
| `isActive` | Boolean | Specifies if the context definition is active (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isEditable` | Boolean | Specifies if the context definition is editable (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Specifies if the operation is success (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `referenceContextDefinitions` | [ContextDefinitionReference[]](./connect-responses-context-definition-reference.md) | List of reference defintions this definition is referencing . | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-definition.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
