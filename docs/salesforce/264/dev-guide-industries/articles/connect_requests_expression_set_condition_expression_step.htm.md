---
page_id: connect_requests_expression_set_condition_expression_step.htm
title: Expression Set Condition Expression Step
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_condition_expression_step.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-11-23
---

# Expression Set Condition Expression Step

Input representation of an expression set condition
step.

## Root XML tag

`<ExpressionSetConditionExpressionStepInput>`

## JSON Example

```
"conditionExpression": {
                "expression": "productName == 'iPhone' && City == 'Los Angeles'",
                "resultParameter": "condition_output__1"
              }
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `expression` | String | Expression that’s defined for the step. | Required | 58.0 |
| `result​Parameter` | String | Expression set version variable associated with the result of the step. | Required | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_condition_expression_step.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
