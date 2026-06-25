---
page_id: connect_responses_simulation_input_variable_basic.htm
title: Simulation Input Variable Basic
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_simulation_input_variable_basic.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-06-25
---

# Simulation Input Variable Basic

Output representation of the details of an input variable of a
simulation.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `apiName` | String | The API name of the input variable. | Small, 53.0 | 53.0 |
| `dataType` | String | The data type of the input variable. Possible values are:  - `Boolean` - `Currency` - `Date` - `Number` - `Percent` - `Text` | Small, 53.0 | 53.0 |
| `defaultValue` | String | The default value of the input variable. | Small, 53.0 | 53.0 |
| `lastSimulatedValue` | String | The value of the input variable in the previous simulation. | Small, 53.0 | 53.0 |
| `name` | String | The name of the input variable. | Small, 53.0 | 53.0 |
| `precision` | String | The floating point precision of the variable. | Small, 53.0 | 53.0 |
