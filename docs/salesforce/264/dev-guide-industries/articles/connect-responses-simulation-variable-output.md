---
page_id: connect-responses-simulation-variable-output
title: Simulation Variable Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-simulation-variable-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-responses
legacy_page_id: connect_responses_simulation_variable_output.htm
fetched_at: 2026-11-25
---

# Simulation Variable Output

Output representation of a simulation variable and its value.

**Note:**

This API has been deprecated as of API version 55.0. In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

- 
- 
- 
- 
- 
- 

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextValue` | Object | Context details for running the simulation on an expression set. | Small, 58.0 | 58.0 |
| `datatype` |  | The data type of the variable. Possible values are: `Boolean``Currency``Date``Number``Percent``Text` | Small, 53.0 | 53.0 |
| `name` | String | Name of the variable. | Small, 53.0 | 53.0 |
| `precision` | Integer | Precision of the variable. | Small, 54.0 | 54.0 |
| `value` | String | Value of the variable. | Small, 53.0 | 53.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-simulation-variable-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
