---
page_id: connect-responses-simulation-step-additional-info-output
title: Simulation Step Additional Info Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-simulation-step-additional-info-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-responses
legacy_page_id: connect_responses_simulation_step_additional_info_output.htm
fetched_at: 2026-11-25
---

# Simulation Step Additional Info Output

Information about the decision matrix or sub expression used in a step.

**Note:**

This API has been deprecated as of API version 55.0. In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

- 
- 

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `stepType` | String | The type of the step. Possible values are: `DecisionMatrix``SubProcedure` | Small, 53.0 | 53.0 |
| `versionName` | String | The name of the decision matrix version or the sub expression version. | Small, 53.0 | 53.0 |
| `versionNumber` | String | The version ID of the decision matrix or the sub expression. | Small, 53.0 | 53.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-simulation-step-additional-info-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
