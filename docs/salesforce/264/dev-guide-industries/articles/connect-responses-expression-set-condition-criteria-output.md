---
page_id: connect-responses-expression-set-condition-criteria-output
title: Expression Set Condition Criteria
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-expression-set-condition-criteria-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-responses
legacy_page_id: connect_responses_expression_set_condition_criteria_output.htm
fetched_at: 2026-11-25
---

# Expression Set Condition Criteria

Output representation of a condition criteria in an expression set.

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
| `operator` | String | Condition operator of the expression set. Valid values are: `Contains``DoesNotContain``Equals``GreaterThan​OrEquals``GreaterThan``IsNotNull``IsNull``LessThan``LessThan​OrEquals``NotEqualTo` | Small, 58.0 | 58.0 |
| `sequence​Number` | Integer | Sequence number of the condition in the advanced condition. | Small, 58.0 | 58.0 |
| `source​Field​Name` | String | Expression set version variable associated with the condition criteria. | Small, 58.0 | 58.0 |
| `value` | String | Value specified in the right-hand side of the condition. | Small, 58.0 | 58.0 |
| `value​Type` | String | Criteria value type of the expression set. Valid values are: `Formula``Literal``Parameter` | Small, 58.0 | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-expression-set-condition-criteria-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
