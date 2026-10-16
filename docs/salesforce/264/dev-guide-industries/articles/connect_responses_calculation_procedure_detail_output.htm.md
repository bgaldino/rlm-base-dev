---
page_id: connect_responses_calculation_procedure_detail_output.htm
title: Calculation Procedure Detail Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_calculation_procedure_detail_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Calculation Procedure Detail Output

Output representation of the expression set details.

      

#### Note

This API has been deprecated as of API version 55.0.
        In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

      
        
          

**Sample Response**

          
: 
            

```
{
   "code" : "200",
   "id" : "0k0x000000000BQAAY",
   "inputVariables" : [ {
      "dataType" : "Number",
      "name" : "var1"
   } ],
   "isSuccess" : true,
   "message" : "",
   "name" : "RuleWith100Conditions42",
   "outputVariables" : [ {
      "dataType" : "Number",
      "name" : "var2"
   } ]
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | The request response code. | Small, 53.0 | 53.0 |
| `description` | String | The description of the expression set. | Small, 53.0 | 53.0 |
| `id` | String | The ID of the expression set record. | Small, 53.0 | 53.0 |
| `inputVariables` | [Calculation Procedure Variable Output[]](./connect_responses_calculation_procedure_variable_output.htm.md) | The list of input variables of the expression set. | Small, 53.0 | 53.0 |
| `isSuccess` | Boolean | Indicates whether the request is successful. | Small, 53.0 | 53.0 |
| `message` | String | The request response message. | Small, 53.0 | 53.0 |
| `name` | String | The name of the expression set. | Small, 53.0 | 53.0 |
| `outputVariables` | [Calculation Procedure Variable Output[]](./connect_responses_calculation_procedure_variable_output.htm.md) | The list of output variables of the expression set. | Small, 53.0 | 53.0 |
