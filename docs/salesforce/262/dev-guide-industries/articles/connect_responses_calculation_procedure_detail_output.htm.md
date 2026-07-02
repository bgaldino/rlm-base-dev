---
page_id: connect_responses_calculation_procedure_detail_output.htm
title: Calculation Procedure Detail Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_calculation_procedure_detail_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-06-25
---

# Calculation Procedure Detail Output

Output representation of the expression set details.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

Sample Response
:   ```
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
| `inputVariables` | [Calculation Procedure Variable Output[]](./connect_responses_calculation_procedure_variable_output.htm.md "Details of the variables of an expression set.") | The list of input variables of the expression set. | Small, 53.0 | 53.0 |
| `isSuccess` | Boolean | Indicates whether the request is successful. | Small, 53.0 | 53.0 |
| `message` | String | The request response message. | Small, 53.0 | 53.0 |
| `name` | String | The name of the expression set. | Small, 53.0 | 53.0 |
| `outputVariables` | [Calculation Procedure Variable Output[]](./connect_responses_calculation_procedure_variable_output.htm.md "Details of the variables of an expression set.") | The list of output variables of the expression set. | Small, 53.0 | 53.0 |
