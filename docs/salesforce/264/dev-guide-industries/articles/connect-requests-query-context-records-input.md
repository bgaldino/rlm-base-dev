---
page_id: connect-requests-query-context-records-input
title: Query Context Records and Children Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-query-context-records-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-requests
fetched_at: 2026-11-25
---

# Query Context Records and Children Input

Input representation for querying context records and their child records.

Identify the context to query and the data paths of the records to return. Include a mapping ID to query with a specific context mapping.

## JSON Example

```
{
  "contextId": "7bc695bc-f38b-4a94-8a95-0caa50f3da53",
  "mappingId": "11jxx0000004Q83AAE",
  "queryPaths": [
    {
      "dataPath": [
        "001xx000003GaX6AAK"
      ]
    }
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | ID of the context to query. | Required | 60.0 |
| `mappingId` | String | ID of the context mapping used to resolve the queried records. | Optional | 60.0 |
| `queryPaths` | [Context Data Path Input](./connect-requests-context-data-path-input.md)[] | List of data paths for the records to query. Each path identifies one record. | Required | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-query-context-records-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
