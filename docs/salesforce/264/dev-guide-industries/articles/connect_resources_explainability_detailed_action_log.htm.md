---
page_id: connect_resources_explainability_detailed_action_log.htm
title: Explainability Detailed Action Log (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_explainability_detailed_action_log.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Decision Explainer
parent_page: decision_explainer_apis_resources.htm
fetched_at: 2026-11-23
---

# Explainability Detailed Action Log (GET)

Retrieve detailed action logs and combine log segments to generate a consolidated
explainability action log.

## Resource

```
/connect/decision-explainer/detailed-action-log
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/decision-explainer/detailed-action-log?actionContextCode=001xx000003GYiCAAW&applicationType=0&applicationSubType=BREDES&processType=BREDES&actionLogDateTime=2024-03-06T05:09:32.000Z&uniqueIdentifier=f89eff41-94ed-4fe7-9b72-f6df2bb5f4aa
```

## Available Version

61.0

## HTTP Methods

GET

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `actionContextCode` | String | Record ID within the context of the associated application's action that can be used to retrieve the action log | Required | 61.0 |
| `actionLogDateTime` | String | Date and time when the explainability action log records are to be returned Date format - yyyy-MM-ddTHH:mm:ss.SSSZ. | Required | 61.0 |
| `applicationSubType` | String | Subtype of the associated application for which the explainability log is generated. | Required | 61.0 |
| `applicationType` | String | Name of the application for which the explainability service is run. | Required | 61.0 |
| `processType` | String | Type of business process associated with the explainability action. | Required | 61.0 |
| `uniqueIdentifier` | String | A unique ID that's associated with a specific explainability action log. | Required | 61.0 |

## Response Body for GET

[Explainability Detailed Action Log Detail](./connect_responses_explainability_detailed_action_log_detail.htm.md "Output representation of explainability action log in detail.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_explainability_detailed_action_log.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
