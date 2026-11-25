---
page_id: connect-resources-query-context-records
title: Query Context Records and Children (POST)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-query-context-records.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: runtime-context-intance-management
fetched_at: 2026-11-25
---

# Query Context Records and Children (POST)

Query context records and their child records by data path.

Use this resource to return the records at one or more data paths, including child records. Each data path is an ordered list of record IDs. The response includes attribute values and the current state of each matching record.

## Resource

```
/connect/contexts/query-records
```

## Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/contexts/query-records
```

{yourInstance} is the domain name of your Salesforce instance.

## Available Version

60.0

## Requires Chatter

No

## HTTP Methods

POST

## Request Body for POST

### JSON Example

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

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | ID of the context to query. | Required | 60.0 |
| `mappingId` | String | ID of the context mapping used to resolve the queried records. | Optional | 60.0 |
| `queryPaths` | [Context Data Path Input](./connect-requests-context-data-path-input.md)[] | List of data paths for the records to query. Each path identifies one record. | Required | 60.0 |

## Response Body for POST

[Query Records Result](./connect-responses-query-records-result.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-query-context-records.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
