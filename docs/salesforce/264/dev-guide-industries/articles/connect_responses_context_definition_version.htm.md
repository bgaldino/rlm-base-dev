---
page_id: connect_responses_context_definition_version.htm
title: Context Definition Version
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_version.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Definition Version 

Output representation of context definition version.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionId` | String | ID of context definition. | Small, 59.0 | 59.0 |
| `contextDefinitionVersionId` | String | ID of context definition version. | Small, 59.0 | 59.0 |
| `contextMappings` | [Context Mapping[]](./connect_responses_context_mapping.htm.md) | List of context mappings. | Small, 59.0 | 59.0 |
| `contextNodes` | [Context Node[]](./connect_responses_context_node.htm.md) | List of context nodes. | Small, 59.0 | 59.0 |
| `endDate` | String | End date till context definition version is valid. | Small, 59.0 | 59.0 |
| `isActive` | Boolean | Specifies if the context definition version is active (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isEditable` | Boolean | Specifies if the context definition version is editable (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Specifies if the operation is success (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `startDate` | String | Start date from when context definition version is valid. | Small, 59.0 | 59.0 |
| `versionNumber` | Integer | Version number. | Small, 59.0 | 59.0 |
