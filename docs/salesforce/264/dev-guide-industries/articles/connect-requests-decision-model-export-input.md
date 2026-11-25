---
page_id: connect-requests-decision-model-export-input
title: Decision Model Export Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-model-export-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-tables-requests
legacy_page_id: connect_requests_decision_model_export_input.htm
fetched_at: 2026-11-25
---

# Decision Model Export Input

Input representation of the request to export decision matrix data.

## JSON Example

```
{
   "decisionModelEntityIds":[
      “0lNRO00000004f72AA”,
      “0lNRO000000rfn27AA”
   ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `decision​Model​EntityIds` | String[] | A list of decision matrix version IDs to export data from. | Required | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-model-export-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
