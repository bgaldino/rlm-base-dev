---
page_id: connect_responses_simulation_input_variables_result_list.htm
title: Simulation Input Variables Result List
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_simulation_input_variables_result_list.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-06-25
---

# Simulation Input Variables Result List

Output representation of the list of input variables of a
simulation.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

Sample Response
:   ```
    {
       "code": "200",
       "message": "",
       "isSuccess": true
       "inputVariables": [
         {
             "DataType": "Number",
             "Name": "medicalPayment",
             "ApiName": "medicalPayment",
             "DefaultValue": "10",
             "LastSimulatedValue": "10",
             "Precision": "1"
          }, {
             "DataType": "Number",
             "ApiName": "dedWaiverFactor",
             "Name": "dedWaiverFactor",
             "DefaultValue": "10",
             "LastSimulatedValue": "15",
             "Precision": "1"
          }
       ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | The request response code. | Small, 53.0 | 53.0 |
| `inputVariables` | [Simulation Input Variables Basic](./connect_responses_simulation_input_variable_basic.htm.md "Output representation of the details of an input variable of a simulation.")[] | The list of input variables of a simulation. | Small, 53.0 | 53.0 |
| `isSuccess` | Boolean | Indicates whether the request is successful. | Small, 53.0 | 53.0 |
| `message` | String | The request response message. | Small, 53.0 | 53.0 |
