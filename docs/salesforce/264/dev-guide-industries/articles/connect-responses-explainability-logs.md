---
page_id: connect-responses-explainability-logs
title: Explainability Logs
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-explainability-logs.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: decision-explainer-bre-responses
legacy_page_id: connect_responses_explainability_logs.htm
fetched_at: 2026-11-25
---

# Explainability Logs

Output representation of the list of explainability action logs.

## JSON Example

```
{
  "actionLogs": [
    {
      "actionContextCode": "001x0000005SdzIAAS",
      "actionLog": "{This is a sample action log data.}",
      "applicationLogDate": "Mon Aug 01 10:29:35 GMT 2022",
      "applicationSubtype": "ASD1",
      "applicationType": "0",
      "name": "EAD1",
      "processType": "BPT1"
    }
  ],
  "queryMore": " "
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `actionLogs` | [Explainability Log Detail](./connect-responses-explainability-log-detail.md)[] | The list of explainability logs that matches the search criteria. | Small, 56.0 | 56.0 |
| `queryMore` | String | A string that can be passed to the next call to fetch the next batch of explainability log records. | Small, 56.0 | 56.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-explainability-logs.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
