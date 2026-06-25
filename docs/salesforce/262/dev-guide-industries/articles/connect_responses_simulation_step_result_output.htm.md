---
page_id: connect_responses_simulation_step_result_output.htm
title: Simulation Step Result Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_simulation_step_result_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-06-25
---

# Simulation Step Result Output

Output representation of the simulation results of a
step.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `additionalInfo` | [Simulation Step Additional Info Output](./connect_responses_simulation_step_additional_info_output.htm.md "Information about the decision matrix or sub expression used in a step.") | Additional information if the step type is decision matrix or sub expression. | Small, 53.0 | 53.0 |
| `explainabilityMessage` | [Simulation Step Explainability Message Output](./connect_responses_simulation_step_explainability_message_output.htm.md "Output representation of a decision explanation message for a step from the simulation.") | Decision explanation message for a step. | Small, 56.0 | 56.0 |
| `isDefaulted` | Boolean | Indicates whether the step has default values (`true`) or not (`false`). | Small, 57.0 | 57.0 |
| `stepErrors` | Map<String, String> | Errors occurred in a step. | Small, 54.0 | 54.0 |
| `stepInputs` | [Simulation Variable Output](./connect_responses_simulation_variable_output.htm.md "Output representation of a simulation variable and its value.")[] | Input variables of a step. | Small, 53.0 | 53.0 |
| `stepResults` | [Simulation Variable Output](./connect_responses_simulation_variable_output.htm.md "Output representation of a simulation variable and its value.")[] | Output variables of a step. | Small, 53.0 | 53.0 |
