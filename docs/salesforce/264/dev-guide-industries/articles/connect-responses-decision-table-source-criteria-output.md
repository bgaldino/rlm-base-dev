---
page_id: connect-responses-decision-table-source-criteria-output
title: Decision Table Source Criteria Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-decision-table-source-criteria-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-tables-responses
legacy_page_id: connect_responses_decision_table_source_criteria_output.htm
fetched_at: 2026-11-25
---

# Decision Table Source Criteria Output

Output representation of the decision table source criteria.

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

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `operator` | String | Operator used in the filter criteria. Possible values are:`Contains``DoesNotContain``Equals``GreaterThan``GreaterThanOrEqual``IsNotNull``IsNull``LessThan``LessThanOrEqual``NotEqual` | Small, 58.0 | 58.0 |
| `sequenceNumber` | Integer | Sequence number of the filter criteria in the associated decision table source condition. | Small, 58.0 | 58.0 |
| `sourceFieldName` | String | Name of the field in the filter criteria. | Small, 58.0 | 58.0 |
| `value` | String | Expected value of the field. | Small, 58.0 | 58.0 |
| `valueType` | String | Type of filter value. Possible values are:`Formula``Literal``Lookup``Parameter``PickList` | Small, 58.0 | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-decision-table-source-criteria-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
