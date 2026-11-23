---
page_id: apex_connectapi_output_decision_table_outcome.htm
title: ConnectApi.DecisionTableOutcome
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/apex_connectapi_output_decision_table_outcome.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apex_output_classes.htm
fetched_at: 2026-11-23
---

# ConnectApi.DecisionTableOutcome

Output representation of the decision table
execution.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `errorCode` | [Integer](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexcode.meta/apexcode/apex_methods_system_integer.htm#apex_methods_system_integer) | The error code if transaction fails for any reason. | 51.0 |
| `errorMessage` | [String](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexcode.meta/apexcode/apex_methods_system_string.htm#apex_methods_system_string) | The error message if transaction fails for any reason. | 51.0 |
| `outcomeList` | [List](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexcode.meta/apexcode/apex_methods_system_list.htm#apex_methods_system_list)<[`ConnectApi.​DecisionTableOutcomeItem`](./apex_connectapi_output_decision_table_outcome_item.htm.md "Output representation of the decision table outcome item.")> | The outcome list that stores two or more outcomes provided by the decision table. Note: A decision table that is invoked by the Decision Table custom invocable action can provide up to 50 outcomes. | 51.0 |
| `outcomeType` | [String](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexcode.meta/apexcode/apex_methods_system_string.htm#apex_methods_system_string) | The outcome type after the request is successful. Valid values are:  - `MultipleMatch`—Outcome returns   multiple matches. - `NoMatch`—Outcome returns no   match. - `SingleMatch`—Outcome returns single   match. | 51.0 |
| `successStatus` | [Boolean](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexcode.meta/apexcode/apex_methods_system_boolean.htm#apex_methods_system_boolean) | Indicates the status of the decision table execution. | 51.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/apex_connectapi_output_decision_table_outcome.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
