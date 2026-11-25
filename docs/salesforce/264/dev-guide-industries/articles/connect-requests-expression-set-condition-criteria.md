---
page_id: connect-requests-expression-set-condition-criteria
title: Expression Set Condition Criteria Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-expression-set-condition-criteria.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-requests
legacy_page_id: connect_requests_expression_set_condition_criteria.htm
fetched_at: 2026-11-25
---

# Expression Set Condition Criteria Input

Input representation of a condition criteria in an expression set.

## Root XML tag

`<ExpressionSetConditionCriteriaInput>`

## JSON Example

```
"criteria" : [ {
                "operator" : "Equals",
                "sequenceNumber" : 1,
                "sourceFieldName" : "a",
                "value" : "0",
                "valueType" : "Literal"
              } ]
```

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

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `operator` | String | Condition operator of the expression set. Valid values are: `Contains``DoesNot​Contain``Equals``GreaterThan​OrEquals``Greater​Than``IsNot​Null``IsNull``LessThan``LessThan​OrEquals``NotEqual​To` | Required | 58.0 |
| `sequence​Number` | Integer | The sequence number of the condition in the advanced condition. | Required | 58.0 |
| `sourceField​Name` | String | The expression set version variable associated with the condition criteria. | Required | 58.0 |
| `value` | String | The right-hand side of the condition is specified in this field. | Required | 58.0 |
| `valueType` | String | Criteria value type of the expression set. Valid values are: `Formula``Literal``Parameter` | Required | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-expression-set-condition-criteria.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
