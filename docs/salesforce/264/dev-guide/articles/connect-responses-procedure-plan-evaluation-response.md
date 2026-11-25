---
page_id: connect-responses-procedure-plan-evaluation-response
title: Procedure Plan Evaluation Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-procedure-plan-evaluation-response.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-responses
legacy_page_id: connect_responses_procedure_plan_evaluation_response.htm
fetched_at: 2026-11-25
---

# Procedure Plan Evaluation Response

Output representation of the evaluation details of a procedure plan definition.

## JSON Example

```
  {
  "isSuccess":true,
  "procedurePlanEvaluations":[
  {
    "errorMessage":"",
    "id":"a01DU000000BylcYAC",
    "isSuccess":true,
    "primaryObject":"SignallingCustomEvaluation__c",
    "result":{
    "contextDefinition":"11ODU00000008Sw2AI",
    "procedurePlanSections":[]
  }
  }
  ]
  }
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorMessage` | String | Message indicating the error details, if any. | Small, 62.0 | 62.0 |
| `isSuccess` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `procedure​PlanDefinition​Name` | String | Name of the procedure plan definition. | Small, 62.0 | 62.0 |
| `procedure​Plan​Evaluations` | [Procedure Plan Evaluation](./connect-responses-procedure-plan-evaluation.md)[] | Evaluation details of the procedure plan. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-procedure-plan-evaluation-response.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
