---
page_id: connect_responses_context_definition.htm
title: Context Definition Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

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
| `contextDefinitionVersionList` | [Context Definition Version](./connect_responses_context_definition_version.htm.md)[] | List of context definition versions. | Small, 59.0 | 59.0 |
| `contextTtl` | Integer | TTL of the context. | Small, 59.0 | 59.0 |
| `definition` | String | Definition. | Small, 59.0 | 59.0 |
| `definitionType` | String | Type of definition. Possible values are: `standard_executable` `standard_nonexecutable` `custom_nonexecutable` | Small, 60.0 | 60.0 |
| `developerName` | String | Developer name. | Small, 59.0 | 59.0 |
| `hasSystemTags` | String | Specifies if the context definition has system node and tags attached (`true`) or not (`false`). | Small, 63.0 | 63.0 |
| `interfaces` | String | List of implemented Context Definition Interfaces for this context definition. | Small, 62.0 | 62.0 |
| `isActive` | Boolean | Specifies if the context definition is active (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isEditable` | Boolean | Specifies if the context definition is editable (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Specifies if the operation is success (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `referenceContextDefinitions` | [ContextDefinitionReference[]](./connect_responses_context_definition_reference.htm.md) | List of reference defintions this definition is referencing . | Small, 63.0 | 63.0 |
