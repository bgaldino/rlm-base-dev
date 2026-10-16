---
page_id: connect_requests_simulation_variable_input.htm
title: Simulation Variable Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_simulation_variable_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Simulation Variable Input

Input information of the input variable and its
    value.

      

#### Note

This API has been deprecated as of API version 55.0.
        In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

**Properties**

: 

- 
- 
- 
- 
- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `datatype` | String | The data type of the variable.Possible values are: `Boolean` `Currency` `Date` `Number` `Percent` `Text` | Required | 53.0 |
| `name` | String | The name of the variable. | Required | 53.0 |
| `value` | String | The value of the variable. | Required | 53.0 |
