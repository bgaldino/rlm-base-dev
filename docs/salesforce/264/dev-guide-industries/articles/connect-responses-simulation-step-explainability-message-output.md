---
page_id: connect-responses-simulation-step-explainability-message-output
title: Simulation Step Explainability Message Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-simulation-step-explainability-message-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-responses
legacy_page_id: connect_responses_simulation_step_explainability_message_output.htm
fetched_at: 2026-11-25
---

# Simulation Step Explainability Message Output

Output representation of a decision explanation message for a step from the simulation.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextTag​Messages` | String | Explainability messages of the step when context tags are used in the step. | Small, 60.0 | 60.0 |
| `message` | String | Decision explanation message of the step. | Small, 56.0 | 56.0 |
| `showCondition​Details` | Boolean | For the `Condition` step type, this property indicates whether the decision explanation includes the condition’s details (`true`) or not (`false`). The default value for this field is `false`. | Small, 56.0 | 56.0 |
| `showOnly​ExecutedPath​Message` | Boolean | For the `Branch` step type, this property indicates whether the decision explanation includes information about the executed path only (`true`) or not (`false`). The default value for this field is `true`. | Small, 56.0 | 56.0 |
| `template​Id` | String | Decision explainer template ID of the step. | Small, 56.0 | 56.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-simulation-step-explainability-message-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
