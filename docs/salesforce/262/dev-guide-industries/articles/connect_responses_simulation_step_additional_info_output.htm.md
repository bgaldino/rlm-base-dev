---
page_id: connect_responses_simulation_step_additional_info_output.htm
title: Simulation Step Additional Info Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_simulation_step_additional_info_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-06-25
---

# Simulation Step Additional Info Output

Information about the decision matrix or sub expression used in a
step.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `stepType` | String | The type of the step. Possible values are:  - `DecisionMatrix` - `SubProcedure` | Small, 53.0 | 53.0 |
| `versionName` | String | The name of the decision matrix version or the sub expression version. | Small, 53.0 | 53.0 |
| `versionNumber` | String | The version ID of the decision matrix or the sub expression. | Small, 53.0 | 53.0 |
