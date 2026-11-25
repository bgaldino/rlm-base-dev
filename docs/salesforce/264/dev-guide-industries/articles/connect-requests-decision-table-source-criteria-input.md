---
page_id: connect-requests-decision-table-source-criteria-input
title: Decision Table Source Criteria Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-table-source-criteria-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-tables-requests
legacy_page_id: connect_requests_decision_table_source_criteria_input.htm
fetched_at: 2026-11-25
---

# Decision Table Source Criteria Input

Input representation of source criteria for the decision table.

## Properties

- 
- 
- 
- 
- 
- 
- 
- 
- 
- 

- 
- 
- 
- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `operator` | String | Operator used in the filter criteria. Possible values are:`Contains``DoesNotContain``Equals``GreaterThan``GreaterThanOrEqual``IsNotNull``IsNull``LessThan``LessThanOrEqual``NotEqual` | Required | 58.0 |
| `sequenceNumber` | Integer | Sequence number of the filter criteria in the associated decision table source condition. | Optional | 58.0 |
| `sourceFieldName` | String | Name of the field in the filter criteria. | Required | 58.0 |
| `value` | String | Expected value of the field. | Optional | 58.0 |
| `valueType` | String | Type of a filter value. Possible values are:`Formula``Literal``Lookup``Parameter``PickList` | Required | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-table-source-criteria-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
