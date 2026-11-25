---
page_id: connect-resources-rules-engine-explainability-logs
title: Explainability Logs (GET)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-rules-engine-explainability-logs.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: decision-explainer-bre-resources
legacy_page_id: connect_resources_rules_engine_explainability_logs.htm
fetched_at: 2026-11-25
---

# Explainability Logs (GET)

Retrieves explainability logs for expression step elements for which explanation messages are configured.

## Resource

```
/connect/business-rules/explainability/logs
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect
/business-rules/explainability/logs?actionContextCode=001x0000005DmI3AAK
```

{yourInstance} is the domain name of your Salesforce instance.

## Available Version

56.0

## Requires Chatter

No

## HTTP Methods

GET

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `action​Context​Code` | String | The record ID within the context of the associated application’s action that’s used to retrieve action logs. | Optional | 56.0 |
| `application​SubType` | String | The subtype of the associated application for which the explainability log is generated. This matches one of the valid values in the ExplainabilityActionDef . `ApplicationSubtype` field. | Optional | 56.0 |
| `application​Type` | String | The name of the application for which the explainability service is run. This matches one of the valid values in the ExplainabilityActionDef .`ApplicationType` field. | Optional | 56.0 |
| `createdAfter` | String | A valid date time after which the explainability log records are returned. | Optional | 56.0 |
| `createdBefore` | String | A valid date time before which the explainability log records are returned. | Optional | 56.0 |
| `pageSize` | Integer | The number of explainability log records to return. The value can range from 200 to 500. | Optional | 56.0 |
| `processType` | String | The process type of the associated application for which the explainability action log is generated. This matches one of the valid values in the ExplainabilityActionDef `ProcessType` field. | Optional | 56.0 |
| `queryMore` | String | A string returned from the previous request, which you must pass to the next request to get the next page. | Optional | 56.0 |

## Response Body for GET

[Explainability Logs](./connect-responses-explainability-logs.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-rules-engine-explainability-logs.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
