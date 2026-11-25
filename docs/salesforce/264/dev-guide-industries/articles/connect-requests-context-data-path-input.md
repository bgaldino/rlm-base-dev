---
page_id: connect-requests-context-data-path-input
title: Context Data Path Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-data-path-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-requests
fetched_at: 2026-11-25
---

# Context Data Path Input

Input representation of the data path to a context record.

A data path identifies one record in a context. Use a single record ID for a root record. To identify a nested record, list the parent record ID first and then each child record ID in order.

## JSON Example

```
{
  "dataPath": [
    "001xx000003GaX6AAK"
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `dataPath` | String[] | Ordered list of record IDs that identifies the record to query. | Required | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-data-path-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
