---
page_id: connect_responses_context_mapping.htm
title: Context Mapping Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_mapping.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Context Mapping Output

Output representation of context mapping.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionVersionID` | String | ID of the context definition version. | Small, 59.0 | 59.0 |
| `contextMappingID` | String | ID of the context mapping. | Small, 59.0 | 59.0 |
| `contextNodeMappings` | [Context Node Mapping](./connect_responses_context_node_mapping.htm.md "Output representation of the context node mapping.")[] | List of context node mappings. | Small, 59.0 | 59.0 |
| `description` | String | Description of context mapping. | Small, 59.0 | 59.0 |
| `isDefault` | Boolean | Specifies if you want to make it the default mapping for context definition (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isInputMapped` | Boolean | Indicates whether the specified context mapping details are mapped with the source (`true`) or not (`false`). | Small, 61.0 | 61.0 |
| `isSuccess` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `intents` | List<String> | Context mapping that’s associated with the usage of the `intents`. | Small, 61.0 | 61.0 |
| `mappedContext​DefinitionName` | String | API name of the context definition when context-to-context mappings exist. | Small, 61.0 | 61.0 |
| `name` | String | Name of the context mapping. | Small, 59.0 | 59.0 |
