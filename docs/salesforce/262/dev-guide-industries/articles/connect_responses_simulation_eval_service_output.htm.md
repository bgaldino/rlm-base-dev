---
page_id: connect_responses_simulation_eval_service_output.htm
title: Simulation Eval Service Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_simulation_eval_service_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-06-25
---

# Simulation Eval Service Output

Output representation of the simulation run on an expression
set.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

Sample Responses
:   This is an example of a simulation run pass.

    ```
    {
       "executionId":"9QMRN00000004Sn4AI_20230112_091636_a091001d",
       "output":{
          "aggregationResults":{
             
          },
          "calculationResults":[
             {
                "res":25.00
             }
          ]
       },
       "simulationResults":[
          {
             "datatype":"Number",
             "name":"var1",
             "precision":2,
             "value":"25.00"
          },
          {
             "contextValue":{
                "PolicyDetails":[
                   {
                      "PolicyName":"Policy1",
                      "TotalMember":"100",
                      "PrincipalAmout":"500",
                      "Status":"Active",
                      "TotalPremium":"1500"
                   },
                   {
                      "PolicyName":"Policy2",
                      "TotalMember":"200",
                      "PrincipalAmout":"100",
                      "Status":"Inactive",
                      "TotalPremium":"0"
                   },
                   {
                      "PolicyName":"Policy3",
                      "TotalMember":"300",
                      "PrincipalAmout":"400",
                      "Status":"Active",
                      "TotalPremium":"300"
                   }
                ]
             },
             "datatype":"Context",
             "name":"PensionFunds",
             "precision":"",
             "value":""
          }
       ],
       "simulationStepResults":{
          "ListFilter":{
             "isDefaulted":false,
             "stepErrors":{
                
             },
             "stepInputs":[
                {
                   "name":"PrincipalAmount",
                   "contextValue":[
                      "500",
                      "100",
                      "400"
                   ],
                   "dataType":"Number",
                   "value":""
                },
                {
                   "name":"PolicyName",
                   "contextValue":[
                      "Policy1",
                      "Policy2",
                      "Policy3"
                   ],
                   "dataType":"Text",
                   "value":""
                },
                {
                   "name":"TotalMembers",
                   "contextValue":[
                      "100",
                      "200",
                      "300"
                   ],
                   "dataType":"Number",
                   "value":""
                },
                {
                   "name":"Status",
                   "contextValue":[
                      "true",
                      "true",
                      "false"
                   ],
                   "dataType":"Boolean",
                   "value":""
                }
             ]
          },
          "stepResults":[
             {
                "datatype":"Number",
                "name":"filter_output_total_items",
                "value":"3"
             },
             {
                "datatype":"Number",
                "name":"filter_output_filtered_items",
                "value":"2"
             },
             {
                "name":"filter_output",
                "datatype":"Boolean",
                "contextValue":[
                   true,
                   false,
                   true
                ],
                "value":""
             }
          ]
       },
       "Calculation":{
          "explainabilityMessage":{
             "message":"Pass calculation msg",
             "showConditionDetails":false,
             "showOnlyExecutedPathMessage":true,
             "templateId":"8U8D20000004C9DKAU"
          },
          "isDefaulted":false,
          "stepErrors":{
             
          },
          "stepInputs":[
             {
                "name":"PrincipalAmount",
                "contextValue":[
                   "500",
                   "100"
                ],
                "dataType":"Number",
                "value":""
             },
             {
                "name":"TotalMembers",
                "contextValue":[
                   "100",
                   "200"
                ],
                "dataType":"Number",
                "value":""
             }
          ],
          "stepResults":[
             {
                "name":"TotalPremium",
                "contextValue":[
                   "1500",
                   "300"
                ],
                "dataType":"Number",
                "value":""
             }
          ]
       }
    }
    ```
:   This is an example of a simulation run failure.

    ```
    {
       "error" : {
          "errorCode" : "",
          "errorMsg" : "localized error msg",
          "errorDetail" : "" // stacktrace
       }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Simulation Error Output](./connect_responses_simulation_error_output.htm.md "Error code and details.") | Error details of the simulation, if any. | Small, 53.0 | 53.0 |
| `executionId` | String | Execution ID generated after a successful request. | Small, 53.0 | 53.0 |
| `output` | [Simulation Runtime Output](./connect_responses_simulation_runtime_output.htm.md "Output representation of the results of an expression set from the simulation.") | Results of the expression set from the simulation. | Small, 54.0 | 54.0 |
| `simulationResults` | [Simulation Variable Output](./connect_responses_simulation_variable_output.htm.md "Output representation of a simulation variable and its value.")[] | List of output variables of the simulation. | Small, 53.0 | 53.0 |
| `simulationStepResults` | Map<String, [Simulation Step Result Output](./connect_responses_simulation_step_result_output.htm.md "Output representation of the simulation results of a step.")> | List of steps in the simulation including the inputs and results of each step. | Small, 53.0 | 53.0 |
