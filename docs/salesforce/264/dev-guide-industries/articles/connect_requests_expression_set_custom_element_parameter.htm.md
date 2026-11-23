---
page_id: connect_requests_expression_set_custom_element_parameter.htm
title: Expression Set Custom Element Parameter Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_custom_element_parameter.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-11-23
---

# Expression Set Custom Element Parameter Input

Input representation of a custom element parameter in an expression
set.

## Root XML tag

`<ExpressionSetCustomElementParameterInput>`

## JSON Example

```
"parameters": [
              {
                "input": true,
                "name": "Divisor",
                "output": false,
                "value": "v1",
                "type": "Parameter"
              },
              {
                "input": true,
                "name": "Dividend",
                "output": false,
                "value": "v2",
                "type": "Parameter"
              },
              {
                "input": false,
                "name": "Answer",
                "output": true,
                "value": "v3",
                "type": "Parameter"
              }
            ]
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `input` | Boolean | Indicates whether the custom element parameter is an input parameter (`true`) or not (`false`). | Required | 58.0 |
| `name` | String | Name of the custom element parameter. | Required | 58.0 |
| `output` | Boolean | Indicates whether the custom element parameter is an output parameter (`true`) or not (`false`). | Required | 58.0 |
| `type` | String | Type of custom element parameter. Valid values are:  - `Formula` - `Literal` - `Lookup` - `Parameter` - `Picklist` The default value is `Parameter`. | Optional | 58.0 |
| `value` | String | Name of the expression set variable. | Required | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_custom_element_parameter.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
