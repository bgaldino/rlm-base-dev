---
page_id: connect-requests-simulation-variable-input
title: Simulation Variable Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-simulation-variable-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-requests
legacy_page_id: connect_requests_simulation_variable_input.htm
fetched_at: 2026-11-25
---

# Simulation Variable Input

Input information of the input variable and its value.

**Note:**

This API has been deprecated as of API version 55.0. In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

## Properties

- 
- 
- 
- 
- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `datatype` | String | The data type of the variable. Possible values are: `Boolean``Currency``Date``Number``Percent``Text` | Required | 53.0 |
| `name` | String | The name of the variable. | Required | 53.0 |
| `value` | String | The value of the variable. | Required | 53.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-simulation-variable-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
