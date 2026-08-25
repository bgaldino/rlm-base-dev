---
page_id: connect_responses_simulation_step_result_output.htm
title: Simulation Step Result Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_simulation_step_result_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Simulation Step Result Output

Output representation of the simulation results of a
    step.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `additionalInfo` | [Simulation Step Additional Info Output](./connect_responses_simulation_step_additional_info_output.htm.md) | Additional information if the step type is decision matrix or sub expression. | Small, 53.0 | 53.0 |
| `explainabilityMessage` | [Simulation Step Explainability Message Output](./connect_responses_simulation_step_explainability_message_output.htm.md) | Decision explanation message for a step. | Small, 56.0 | 56.0 |
| `isDefaulted` | Boolean | Indicates whether the step has default values (`true`) or not (`false`). | Small, 57.0 | 57.0 |
| `stepErrors` | Map<String, String> | Errors occurred in a step. | Small, 54.0 | 54.0 |
| `stepInputs` | [Simulation Variable Output](./connect_responses_simulation_variable_output.htm.md)[] | Input variables of a step. | Small, 53.0 | 53.0 |
| `stepResults` | [Simulation Variable Output](./connect_responses_simulation_variable_output.htm.md)[] | Output variables of a step. | Small, 53.0 | 53.0 |
