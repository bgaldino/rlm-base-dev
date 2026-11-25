---
page_id: connect-requests-expression-set-lookup-table-step
title: Expression Set Lookup Table Step Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-expression-set-lookup-table-step.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-requests
legacy_page_id: connect_requests_expression_set_lookup_table_step.htm
fetched_at: 2026-11-25
---

# Expression Set Lookup Table Step Input

Input representation of a lookup table step in an expression set.

## Root XML tag

`<ExpressionSetLookupTableStepInput>`

## JSON Example

```
              "lookupTable": {
                "lookupTableName": "DM_for_test",
                "type": "DecisionMatrix"
              }
```

## Properties

- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `lookup​TableName` | String | Decision matrix or decision table name that’s used in the lookup table step. | Required | 58.0 |
| `type` | String | Lookup table type of the expression set. Valid values are: `DecisionMatrix``DecisionTable` | Required | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-expression-set-lookup-table-step.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
