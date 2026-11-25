---
page_id: connect-requests-query-persist-context-input
title: Query Persist Context
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-query-persist-context-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-requests
fetched_at: 2026-11-25
---

# Query Persist Context

Persist context data to the system by providing the relevant context ID. The context and corresponding records will be persisted for further processing.

## JSON Example

```
{
  "contextPersistInput": {
    "contextId": "384fdcef-36e2-4bbb-82ed-2e7bc4e670c7",
    "targetMappingId": "11jxx0000004Q83AAE"
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextPersistInput` | Object | Contains contextId and targetMappingId for persisting context. | Required | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-query-persist-context-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
