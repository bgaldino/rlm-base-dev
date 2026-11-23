---
page_id: connect_requests_expression_set_custom_element_step.htm
title: Expression Set Custom Element Step Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_custom_element_step.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-11-23
---

# Expression Set Custom Element Step Input

Input representation of a custom element step in an expression
set.

## Root XML tag

`<ExpressionSetCustomElementStepInput>`

## JSON Example

```
 "customElement": {
            "parameters": [
              {
                "input": true,
                "name": "Divisor",
                "output": false,
                "value": "v1"
              },
              {
                "input": true,
                "name": "Dividend",
                "output": false,
                "value": "v2"
              },
              {
                "input": false,
                "name": "Answer",
                "output": true,
                "value": "v3"
              }
            ]
          },
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `parameters` | [Expression Set Custom Element Parameter Input](./connect_requests_expression_set_custom_element_parameter.htm.md "Input representation of a custom element parameter in an expression set.")[] | List of parameters in a custom element. | Required | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_custom_element_step.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
