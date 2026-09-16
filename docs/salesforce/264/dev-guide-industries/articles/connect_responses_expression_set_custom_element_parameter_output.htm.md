---
page_id: connect_responses_expression_set_custom_element_parameter_output.htm
title: Expression Set Custom Element Parameter
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_expression_set_custom_element_parameter_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Expression Set Custom Element Parameter

Output representation of a custom element parameter in an expression
      set.

            
              

              

              
- 
- 
- 
- 
- 

              

              

            

              

              

              

              

              

            

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `input` | Boolean | Indicates whether the custom element parameter is an input parameter (`true`) or not (`false`). | Small, 58.0 | 58.0 |
| `name` | String | Name of the custom element parameter. | Small, 58.0 | 58.0 |
| `output` | Boolean | Indicates whether the custom element parameter is an output parameter (`true`) or not (`false`). | Small, 58.0 | 58.0 |
| `type` | String | Type of custom element parameter. Valid values are: `Formula` `Literal` `Lookup` `Parameter` `Picklist` The default value is `Parameter`. | Small, 58.0 | 58.0 |
| `value` | String | Name of the expression set variable. | Small, 58.0 | 58.0 |
