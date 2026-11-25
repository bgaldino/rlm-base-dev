---
page_id: connect-responses-simulation-step-result-output
title: Simulation Step Result Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-simulation-step-result-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-responses
legacy_page_id: connect_responses_simulation_step_result_output.htm
fetched_at: 2026-11-25
---

# Simulation Step Result Output

Output representation of the simulation results of a step.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `additionalInfo` | [Simulation Step Additional Info Output](./connect-responses-simulation-step-additional-info-output.md) | Additional information if the step type is decision matrix or sub expression. | Small, 53.0 | 53.0 |
| `explainabilityMessage` | [Simulation Step Explainability Message Output](./connect-responses-simulation-step-explainability-message-output.md) | Decision explanation message for a step. | Small, 56.0 | 56.0 |
| `isDefaulted` | Boolean | Indicates whether the step has default values (`true`) or not (`false`). | Small, 57.0 | 57.0 |
| `stepErrors` | Map<String, String> | Errors occurred in a step. | Small, 54.0 | 54.0 |
| `stepInputs` | [Simulation Variable Output](./connect-responses-simulation-variable-output.md)[] | Input variables of a step. | Small, 53.0 | 53.0 |
| `stepResults` | [Simulation Variable Output](./connect-responses-simulation-variable-output.md)[] | Output variables of a step. | Small, 53.0 | 53.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-simulation-step-result-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
