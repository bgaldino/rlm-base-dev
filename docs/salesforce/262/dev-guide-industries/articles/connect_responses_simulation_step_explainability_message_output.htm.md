---
page_id: connect_responses_simulation_step_explainability_message_output.htm
title: Simulation Step Explainability Message Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_simulation_step_explainability_message_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-06-25
---

# Simulation Step Explainability Message Output

Output representation of a decision explanation message for a step
from the simulation.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextTag​Messages` | String | Explainability messages of the step when context tags are used in the step. | Small, 60.0 | 60.0 |
| `message` | String | Decision explanation message of the step. | Small, 56.0 | 56.0 |
| `showCondition​Details` | Boolean | For the `Condition` step type, this property indicates whether the decision explanation includes the condition's details (`true`) or not (`false`). The default value for this field is `false`. | Small, 56.0 | 56.0 |
| `showOnly​ExecutedPath​Message` | Boolean | For the `Branch` step type, this property indicates whether the decision explanation includes information about the executed path only (`true`) or not (`false`). The default value for this field is `true`. | Small, 56.0 | 56.0 |
| `template​Id` | String | Decision explainer template ID of the step. | Small, 56.0 | 56.0 |
