---
page_id: connect-responses-simulation-runtime-output
title: Simulation Runtime Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-simulation-runtime-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-responses
legacy_page_id: connect_responses_simulation_runtime_output.htm
fetched_at: 2026-11-25
---

# Simulation Runtime Output

Output representation of the results of an expression set from the simulation.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `aggregationResults` | Map<String, String> | Aggregation results of the expression set from the simulation when the step type is `Aggregation`. | Small, 54.0 | 54.0 |
| `calculationResults` | Map<String, String>[] | Calculation results of the expression set from the simulation when the step type is `Calculation`. | Small, 54.0 | 54.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-simulation-runtime-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
