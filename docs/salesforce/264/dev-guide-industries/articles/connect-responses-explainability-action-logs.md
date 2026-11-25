---
page_id: connect-responses-explainability-action-logs
title: Explainability Action Logs
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-explainability-action-logs.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Decision Explainer
parent_page: decision-explainer-apis-responses
legacy_page_id: connect_responses_explainability_action_logs.htm
fetched_at: 2026-11-25
---

# Explainability Action Logs

Output representation of the list of Explainability action logs.

## JSON Example

```
{
   "actionLogs" : [ {
      "actionContextCode" : "001x0000005DmI3AAK",
      "actionLog" : “{This is a sample action log data.}”,
      "applicationLogDate" : "Mon Dec 06 10:29:35 GMT 2021",
      "applicationSubtype" : "AST1",
      "applicationType" : "0",
      "name" : "EAD1",
      "processType" : "BPT1"
   }, {
      "actionContextCode" : "001x0000005DmI3AAK",
      "actionLog" : “{This is a sample action log data.}”,
      "applicationLogDate" : "Mon Dec 06 15:21:09 GMT 2021",
      "applicationSubtype" : "AST1",
      "applicationType" : "0",
      "name" : "EAD1",
      "processType" : "BPT1"
   } ],
   "queryMore" : ""
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `actionLogs` | [Explainability Action Log Detail](./connect-responses-explainability-action-log-detail.md)[] | Represents the list of explainability action logs. | Small, 54.0 | 54.0 |
| `queryMore` | String | A string that can be passed to the next call to fetch the next batch of explainability action log records. | Small, 54.0 | 54.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-explainability-action-logs.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
