---
page_id: connect_responses_context_mapping.htm
title: Context Mapping Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_mapping.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Mapping Output

Output representation of context mapping.

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionVersionID` | String | ID of the context definition version. | Small, 59.0 | 59.0 |
| `contextMappingID` | String | ID of the context mapping. | Small, 59.0 | 59.0 |
| `contextNodeMappings` | [Context Node Mapping](./connect_responses_context_node_mapping.htm.md)[] | List of context node mappings. | Small, 59.0 | 59.0 |
| `description` | String | Description of context mapping. | Small, 59.0 | 59.0 |
| `isDefault` | Boolean | Specifies if you want to make it the default mapping for context definition (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isInputMapped` | Boolean | Indicates whether the specified context mapping details are mapped with the source (`true`) or not (`false`). | Small, 61.0 | 61.0 |
| `isSuccess` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `intents` | List<String> | Context mapping that’s associated with the usage of the `intents`. | Small, 61.0 | 61.0 |
| `mappedContext​DefinitionName` | String | API name of the context definition when context-to-context mappings exist. | Small, 61.0 | 61.0 |
| `name` | String | Name of the context mapping. | Small, 59.0 | 59.0 |
