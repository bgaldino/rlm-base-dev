---
page_id: connect_requests_simulation_variable_input.htm
title: Simulation Variable Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_simulation_variable_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_requests.htm
fetched_at: 2026-06-25
---

# Simulation Variable Input

Input information of the input variable and its
value.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `datatype` | String | The data type of the variable. Possible values are:  - `Boolean` - `Currency` - `Date` - `Number` - `Percent` - `Text` | Required | 53.0 |
    | `name` | String | The name of the variable. | Required | 53.0 |
    | `value` | String | The value of the variable. | Required | 53.0 |
