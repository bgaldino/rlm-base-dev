---
page_id: connect_responses_simulation_step_additional_info_output.htm
title: Simulation Step Additional Info Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_simulation_step_additional_info_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Simulation Step Additional Info Output

Information about the decision matrix or sub expression used in a
      step.

      

#### Note

This API has been deprecated as of API version 55.0.
        In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

              

              

              
- 
- 

              

              

            

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `stepType` | String | The type of the step.Possible values are: `DecisionMatrix` `SubProcedure` | Small, 53.0 | 53.0 |
| `versionName` | String | The name of the decision matrix version or the sub expression version. | Small, 53.0 | 53.0 |
| `versionNumber` | String | The version ID of the decision matrix or the sub expression. | Small, 53.0 | 53.0 |
