---
page_id: connect_responses_context_attribute_mapping.htm
title: Context Attribute Mapping
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_attribute_mapping.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

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
