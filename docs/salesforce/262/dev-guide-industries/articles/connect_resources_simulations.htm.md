---
page_id: connect_resources_simulations.htm
title: Simulations
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_simulations.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_resources.htm
fetched_at: 2026-06-25
---

# Simulations

Retrieve the input variables of an expression set that are required to
run a simulation. Run a simulation. An expression set, also known as calculation
procedure, is a group of steps that perform mathematical operations and
transformations.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

Resource
:   ```
    /connect/omnistudio/evaluation-services/version-definitions/${id}/simulation
    ```

Example URI for GET
:   ```
    /services/data/v53.0/connect/omnistudio/evaluation-services/version-definitions/a1o5w000002EJPPAA4/simulation
    ```

Example URI for PATCH
:   ```
    /services/data/v53.0/connect/omnistudio/evaluation-services/version-definitions/a1o5w000002EJPPAA4/simulation
    ```

Available version
:   53.0

Requires Chatter
:   No

HTTP methods
:   GET, PATCH

Query parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `inputVariables` | Boolean | Reserved for future use. | Optional | 53.0 |

Response body for GET
:   [Simulation Input Variables Result List](./connect_responses_simulation_input_variables_result_list.htm.md "Output representation of the list of input variables of a simulation.")

Request body for PATCH
:   Root XML tag
    :   `SimulationEvalServiceInput`

    JSON example
    :   ```
        {
           "input":{
              "variables":[
                 {
                    "name":"artEstimatedValue",
                    "value":"301",
                    "datatype":"number"
                 },
                 {
                    "name":"quantity",
                    "value":"301",
                    "datatype":"number"
                 }
              ]
           },
           "contextInput":{
              "name":"PensionFunds",
              "value":{
                 "PolicyDetails":[
                    {
                       "PolicyName":"Policy1",
                       "TotalMember":"100",
                       "PrincipalAmout":"500",
                       "Status":"Active",
                       "TotalPremium":"0"
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
                       "TotalPremium":"0"
                    }
                 ]
              }
           },
           "config":{
              "versionInfo":{
                 "configurationVersionId":"a1o5w000002EJPPAA4",
                 "effectiveDate":"2019-02-13 00:00:00"
              }
           }
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `config` | [Simulation Config Input](./connect_requests_simulation_config_input.htm.md "Input information of the configuration version to run a simulation.") | Configuration details for the simulation. | Required | 53.0 |
        | `contextInput` | [Simulation Context Input](./connect_requests_simulation_context_input.htm.md "Input representation of context details for simulation.") | Context details for the simulation. | Required | 58.0 |
        | `input` | [Simulation Variable Input[]](./connect_requests_simulation_variable_input.htm.md "Input information of the input variable and its value.") | List of input variables to run the simulation. | Required | 53.0 |

Response body for PATCH
:   [Simulation Eval
    Service Output](./connect_responses_simulation_eval_service_output.htm.md "Output representation of the simulation run on an expression set.")
