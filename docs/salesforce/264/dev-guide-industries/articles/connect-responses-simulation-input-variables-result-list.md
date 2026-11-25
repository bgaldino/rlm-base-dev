---
page_id: connect-responses-simulation-input-variables-result-list
title: Simulation Input Variables Result List
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-simulation-input-variables-result-list.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-responses
legacy_page_id: connect_responses_simulation_input_variables_result_list.htm
fetched_at: 2026-11-25
---

# Simulation Input Variables Result List

Output representation of the list of input variables of a simulation.

**Note:**

This API has been deprecated as of API version 55.0. In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

**Sample Response**

: 

```
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
| `inputVariables` | [Simulation Input Variables Basic](./connect-responses-simulation-input-variable-basic.md)[] | The list of input variables of a simulation. | Small, 53.0 | 53.0 |
| `isSuccess` | Boolean | Indicates whether the request is successful. | Small, 53.0 | 53.0 |
| `message` | String | The request response message. | Small, 53.0 | 53.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-simulation-input-variables-result-list.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
