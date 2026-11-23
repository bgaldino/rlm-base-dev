---
page_id: connect_responses_guardrail_current_value.htm
title: Guardrail Current Value
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_guardrail_current_value.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-11-23
---

# Guardrail Current Value

Output representation of the current values of the guardrails along with the resource
type.

```
{
  "currentValues": {
    "resourceType": "ExampleResource",
    "values": {
      "currentValue": "50",
      "resourceName": "Resource1"
    }
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `resource​Type` | String | Name of the sObject that the current value of the guardrail is determined from. | Small, 63.0 | 63.0 |
| `values` | [Current Value[]](./connect_responses_current_value.htm.md "Output representation of the current value of the guardrail at a row level.") | Row-level current values of the guardrail. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_guardrail_current_value.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
