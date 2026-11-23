---
page_id: connect_responses_explainability_action_logs.htm
title: Explainability Action Logs
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_explainability_action_logs.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Decision Explainer
parent_page: decision_explainer_apis_responses.htm
fetched_at: 2026-11-23
---

# Explainability Action Logs

Output representation of the list of Explainability action
logs.

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
| `actionLogs` | [Explainability Action Log Detail](./connect_responses_explainability_action_log_detail.htm.md "Output representation of the Explainability action log details.")[] | Represents the list of explainability action logs. | Small, 54.0 | 54.0 |
| `queryMore` | String | A string that can be passed to the next call to fetch the next batch of explainability action log records. | Small, 54.0 | 54.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_explainability_action_logs.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
