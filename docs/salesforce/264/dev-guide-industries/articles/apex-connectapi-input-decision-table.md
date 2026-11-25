---
page_id: apex-connectapi-input-decision-table
title: ConnectApi.DecisionTableInput
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/apex-connectapi-input-decision-table.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: decision-table-apex-input-classes
legacy_page_id: apex_connectapi_input_decision_table.htm
fetched_at: 2026-11-25
---

# ConnectApi.DecisionTableInput

Input representation of the decision table.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `conditions` | [List](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_methods_system_list.htm#apex_methods_system_list)<[`ConnectApi.​DecisionTableCondition`](./apex-connectapi-input-decision-table-condition-representatio.md)> | List of decision table conditions on which the decision table executes. | Required | 51.0 |
| `datasetLinkName` | [String](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_methods_system_string.htm#apex_methods_system_string) | The API name of the dataset link provided as an input for the decision table execution. | Optional | 51.0 |
| `options` | [`ConnectApi.DecisionTableBulkLookupOptions`](./apex-connectapi-input-decision-table-bulk-lookup-options.md) | Lookup options for a versioned CSV decision table. The API ignores these options for any other decision table type. | Optional | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/apex-connectapi-input-decision-table.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
