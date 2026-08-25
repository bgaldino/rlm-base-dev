---
page_id: connect_responses_simulation_runtime_output.htm
title: Simulation Runtime Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_simulation_runtime_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Simulation Runtime Output

Output representation of the results of an expression set from the
      simulation.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `aggregationResults` | Map<String, String> | Aggregation results of the expression set from the simulation when the step type is `Aggregation`. | Small, 54.0 | 54.0 |
| `calculationResults` | Map<String, String>[] | Calculation results of the expression set from the simulation when the step type is `Calculation`. | Small, 54.0 | 54.0 |
