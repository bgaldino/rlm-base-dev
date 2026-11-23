---
page_id: apex_connectapi_input_decision_table.htm
title: ConnectApi.DecisionTableInput
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/apex_connectapi_input_decision_table.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apex_input_classes.htm
fetched_at: 2026-11-23
---

# ConnectApi.DecisionTableInput

Input representation of the decision table.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `conditions` | [List](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexcode.meta/apexcode/apex_methods_system_list.htm#apex_methods_system_list)<[`ConnectApi.​DecisionTableCondition`](./apex_connectapi_input_decision_table_condition_representatio.htm.md "Input representation of the decision table condition.")> | List of decision table conditions on which the decision table executes. | Required | 51.0 |
| `datasetLinkName` | [String](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexcode.meta/apexcode/apex_methods_system_string.htm#apex_methods_system_string) | The API name of the dataset link provided as an input for the decision table execution. | Optional | 51.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/apex_connectapi_input_decision_table.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
