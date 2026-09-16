---
page_id: connect_requests_simulation_context_input.htm
title: Simulation Context Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_simulation_context_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Simulation Context Input

Input representation of context details for
  simulation.

**Properties**

: 

                  
                    

                    

                    

                    

                    

                  

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `context​MappingId` | String | ID of the context mapping. | Optional | 62.0 |
| `name` | String | Name of the input context. | Required | 58.0 |
| `value` | Object | Value of the input context. | Required | 58.0 |
