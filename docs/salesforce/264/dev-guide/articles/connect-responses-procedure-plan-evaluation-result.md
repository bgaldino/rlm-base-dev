---
page_id: connect-responses-procedure-plan-evaluation-result
title: Procedure Plan Evaluation Result
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-procedure-plan-evaluation-result.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-responses
legacy_page_id: connect_responses_procedure_plan_evaluation_result.htm
fetched_at: 2026-11-25
---

# Procedure Plan Evaluation Result

Output representation of the evaluation result of a procedure plan definition.

## JSON Example

```
    "result":{
    "contextDefinition":"11ODU00000008Sw2AI",
    "procedurePlanSections":[]
  }
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `context​Definition` | String | Context definition that’s associated with the procedure plan evaluation. | Small, 62.0 | 62.0 |
| `procedure​PlanSections` | [Procedure Plan Section Evaluation Runtime](./connect-responses-procedure-plan-section-evaluation-runtime.md)[] | Results from the procedure plan evaluation. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-procedure-plan-evaluation-result.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
