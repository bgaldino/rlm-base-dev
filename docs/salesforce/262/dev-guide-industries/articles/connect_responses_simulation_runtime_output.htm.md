---
page_id: connect_responses_simulation_runtime_output.htm
title: Simulation Runtime Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_simulation_runtime_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-06-25
---

# Simulation Runtime Output

Output representation of the results of an expression set from the
simulation.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `aggregationResults` | Map<String, String> | Aggregation results of the expression set from the simulation when the step type is `Aggregation`. | Small, 54.0 | 54.0 |
| `calculationResults` | Map<String, String>[] | Calculation results of the expression set from the simulation when the step type is `Calculation`. | Small, 54.0 | 54.0 |
