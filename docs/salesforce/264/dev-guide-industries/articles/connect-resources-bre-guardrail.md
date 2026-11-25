---
page_id: connect-resources-bre-guardrail
title: Guardrails (GET)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-bre-guardrail.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-resources
legacy_page_id: connect_resources_bre_guardrail.htm
fetched_at: 2026-11-25
---

# Guardrails (GET)

Fetches guardrails from the Business Rules Engine (BRE) to manage rate limits for BRE components.

## Resource

```
/connect/business-rules/guardrails
```

## Example POST

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/business-rules/guardrails
```

{yourInstance} is the domain name of your Salesforce instance.

## Available Version

63.0

## HTTP Methods

GET

## Request Parameters for GET

- 
- 
- 
- 
- 

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `componentNames` | String | BRE component to fetch the guardrails. It contains a comma-separated list of predefined components. Valid component values are: `ExpressionSet``DecisionTable``DecisionMatrix``Explainability``DynamicRules`If no values are provided, guardrails for all components accessible to the user are returned. | Optional | 63.0 |
| `isNotification​Enabled` | Boolean | Indicates whether to return only the guardrails with enabled notifications (`true`) or not (`false`). | Optional | 63.0 |

## Response Body for GET

[BRE Guardrails](./connect-responses-bre-guardrails.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-bre-guardrail.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
