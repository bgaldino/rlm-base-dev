---
page_id: connect_resources_bre_guardrail.htm
title: Guardrails (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_guardrail.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_resources.htm
fetched_at: 2026-11-23
---

# Guardrails (GET)

Fetches guardrails from the Business Rules Engine (BRE) to manage rate limits for BRE
components.

## Resource

```
/connect/business-rules/guardrails
```

## Example POST

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/business-rules/guardrails
```

## Available Version

63.0

## HTTP Methods

GET

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `componentNames` | String | BRE component to fetch the guardrails. It contains a comma-separated list of predefined components. Valid component values are:   - `ExpressionSet` - `DecisionTable` - `DecisionMatrix` - `Explainability` - `DynamicRules`  If no values are provided, guardrails for all components accessible to the user are returned. | Optional | 63.0 |
| `isNotification​Enabled` | Boolean | Indicates whether to return only the guardrails with enabled notifications (`true`) or not (`false`). | Optional | 63.0 |

## Response Body for GET

[BRE Guardrails](./connect_responses_bre_guardrails.htm.md "Output representation of the BRE guardrails for each component.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_guardrail.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
