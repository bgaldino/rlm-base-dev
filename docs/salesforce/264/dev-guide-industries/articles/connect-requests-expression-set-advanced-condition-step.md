---
page_id: connect-requests-expression-set-advanced-condition-step
title: Expression Set Advanced Condition Step Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-expression-set-advanced-condition-step.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-requests
legacy_page_id: connect_requests_expression_set_advanced_condition_step.htm
fetched_at: 2026-11-25
---

# Expression Set Advanced Condition Step Input

Input representation of an advanced condition step in an expression set.

## Root XML tag

`<ExpressionSetAdvancedConditionStepInput>`

## JSON Example

```
"advancedCondition" : {
            "conditionLogic" : "1",
              "criteria" : [ {
                "operator" : "Equals",
                "sequenceNumber" : 1,
                "sourceFieldName" : "a",
                "value" : "0",
                "valueType" : "Literal"
              } ],
            "resultParameter" : "condition_output__1"
          }
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `condition​Logic` | String | Condition that’s defined for the advanced condition. For example, if all conditions are met or any of the conditions are met. | Required | 58.0 |
| `criteria` | [Expression Set Condition Criteria Input](./connect-requests-expression-set-condition-criteria.md)[] | List of condition criteria in an expression set. | Required | 58.0 |
| `result​Parameter` | String | Expression set definition version variable associated with the result of the step. | Required | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-expression-set-advanced-condition-step.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
