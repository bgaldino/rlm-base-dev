---
page_id: connect-responses-message-templates-list-output
title: Message Templates List
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-message-templates-list-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: decision-explainer-bre-responses
legacy_page_id: connect_responses_message_templates_list_output.htm
fetched_at: 2026-11-25
---

# Message Templates List

Output representation of the list of explainability message templates.

## JSON Example

```
{
  "messageTemplates" : [ {
    "expressionSetStepType" : "Branch",
    "id" : "8U8x00000000027CAA",
    "isDefault" : true,
    "message" : "This is Branch Passing Message",
    "name" : "BranchMessageTemplate",
    "resultType" : "Passed"
  }, {
    "expressionSetStepType" : "Calculation",
    "id" : "8U8x00000000022CAA",
    "isDefault" : true,
    "message" : "CalcMessageTemplate PASS",
    "name" : "CalcMessageTemplate",
    "resultType" : "Passed"
  }, {
    "expressionSetStepType" : "Condition",
    "id" : "8U8x0000000002CCAQ",
    "isDefault" : false,
    "message" : "This is Condition Passing Message",
    "name" : "ConditionMessageTemplate",
    "resultType" : "Passed"
  }, {
    "expressionSetStepType" : "MatrixLookup",
    "id" : "8U8x0000000002HCAQ",
    "isDefault" : true,
    "message" : "This is DM passing message",
    "name" : "DMMessageTemplate",
    "resultType" : "Passed"
  }, {
    "expressionSetStepType" : "ReferenceProcedure",
    "id" : "8U8x0000000002MCAQ",
    "isDefault" : true,
    "message" : "This is SubExpression Passing Message",
    "name" : "SubExpressionMessageTemplate",
    "resultType" : "Passed"
  } ]
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | The API response code when there’s a failure in retrieving the list of explainability message templates. | Small, 56.0 | 56.0 |
| `isSuccess` | Boolean | Identifies whether the request is successful (`true`) or not (`false`). | Small, 56.0 | 56.0 |
| `message` | String | The error message when there’s a failure in retrieving the list of explainability message templates. | Small, 56.0 | 56.0 |
| `message​Templates` | [Message Template Detail](./connect-responses-message-template-detail-output.md) [] | The list of explainability message templates. | Small, 56.0 | 56.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-message-templates-list-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
