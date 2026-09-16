---
page_id: connect_responses_simulation_variable_output.htm
title: Simulation Variable Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_simulation_variable_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Simulation Variable Output

Output representation of a simulation variable and its
    value.

      

#### Note

This API has been deprecated as of API version 55.0.
        In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

            
              

              

              
- 
- 
- 
- 
- 
- 

              

              

            

            
              

              

              

              

              

            

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextValue` | Object | Context details for running the simulation on an expression set. | Small, 58.0 | 58.0 |
| `datatype` |  | The data type of the variable.Possible values are: `Boolean` `Currency` `Date` `Number` `Percent` `Text` | Small, 53.0 | 53.0 |
| `name` | String | Name of the variable. | Small, 53.0 | 53.0 |
| `precision` | Integer | Precision of the variable. | Small, 54.0 | 54.0 |
| `value` | String | Value of the variable. | Small, 53.0 | 53.0 |
