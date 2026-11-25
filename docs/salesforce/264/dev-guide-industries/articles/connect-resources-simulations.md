---
page_id: connect-resources-simulations
title: Simulations
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-simulations.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-resources
legacy_page_id: connect_resources_simulations.htm
fetched_at: 2026-11-25
---

# Simulations

Retrieve the input variables of an expression set that are required to run a simulation. Run a simulation. An expression set, also known as calculation procedure, is a group of steps that perform mathematical operations and transformations.

## Resource

```
/connect/omnistudio/evaluation-services/version-definitions/${id}/simulation
```

## Example URI for GET

```
/services/data/v53.0/connect/omnistudio/evaluation-services/version-definitions/a1o5w000002EJPPAA4/simulation
```

## Example URI for PATCH

```
/services/data/v53.0/connect/omnistudio/evaluation-services/version-definitions/a1o5w000002EJPPAA4/simulation
```

## Available Version

53.0

## Requires Chatter

No

## HTTP Methods

GET, PATCH

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `inputVariables` | Boolean | Reserved for future use. | Optional | 53.0 |

## Response Body for GET

[Simulation Input Variables Result List](./connect-responses-simulation-input-variables-result-list.md)

## Request Body for PATCH

### JSON Example

```
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

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `config` | [Simulation Config Input](./connect-requests-simulation-config-input.md) | Configuration details for the simulation. | Required | 53.0 |
| `contextInput` | [Simulation Context Input](./connect-requests-simulation-context-input.md) | Context details for the simulation. | Required | 58.0 |
| `input` | [Simulation Variable Input[]](./connect-requests-simulation-variable-input.md) | List of input variables to run the simulation. | Required | 53.0 |

## Response Body for PATCH

[Simulation Eval Service Output](./connect-responses-simulation-eval-service-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-simulations.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
