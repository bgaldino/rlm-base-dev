---
page_id: connect_requests_context_definition_input.htm
title: Context Definition Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definition_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-11-23
---

# Context Definition Input

Input representation of the context definitions in an expression
set.

## Root XML tag

`<ContextDefinitionInput>`

## JSON Example

```
  "contextDefinitionList": {
      "contextDefinitions":[{
      "id":"11Oxx0000006PcLEAU"
      }]
  }
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the context definition. | Required | 58.0 |
| `name` | String | Developer name of the context definition. | Optional | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definition_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
