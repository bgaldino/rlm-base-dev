---
page_id: connect_responses_message_template_detail_output.htm
title: Message Template Detail
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_message_template_detail_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_explainer_bre_responses.htm
fetched_at: 2026-11-23
---

# Message Template Detail

Output representation of explainability message template
details.

## JSON Example

```
{
  "expressionSetStepType": "Branch",
  "id": "8U8x00000000027CAA",
  "isDefault": true,
  "message": "This is Branch Passing Message",
  "name": "BranchMessageTemplate",
  "resultType": "Passed"
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `expression​SetStep​Type` | String | The step type in an expression set version that uses the explainability message template. Possible values:   - Calculation - Branch - Condition - Decision Matrix Lookup - Decision Table Lookup - Aggregation - Sub Expression - Business Element | Small, 56.0 | 56.0 |
| `id` | String | The record ID of the explainability message template. | Small, 56.0 | 56.0 |
| `isDefault` | Boolean | Indicates whether the decision explainer template for a specified step type is default (`true`) or not (`false`). | Small, 56.0 | 56.0 |
| `message` | String | The explanation message in the explainability message template for a specific expression set step type. | Small, 56.0 | 56.0 |
| `name` | String | The name that identifies the explainability message template. | Small, 56.0 | 56.0 |
| `resultType` | String | The type of result for which the message template can be used. The step type for which the result is evaluated can be a condition, conditional group, or branch.  Possible Values:   - `Passed` - `Failed` | Small, 56.0 | 56.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_message_template_detail_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
