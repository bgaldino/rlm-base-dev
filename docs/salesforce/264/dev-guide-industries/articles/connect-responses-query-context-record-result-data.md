---
page_id: connect-responses-query-context-record-result-data
title: Query Context Record Result Data
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-query-context-record-result-data.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
fetched_at: 2026-11-25
---

# Query Context Record Result Data

Output representation of the query result for one data path.

Each item pairs a data path from the request with the records returned for that path. The query result includes the matching record and its child records.

## JSON Example

```
{
  "dataPath": [
    "001xx000003GaX6AAK"
  ],
  "queryResult": {
    "contextId": "7bc695bc-f38b-4a94-8a95-0caa50f3da53",
    "isDone": true,
    "isSuccess": true,
    "queryRecords": [
      {
        "childQueryRecords": [],
        "record": {
          "attributesAndValues": {
            "Name": "Acme Corp",
            "Industry": "Manufacturing",
            "Type": "Prospect"
          },
          "businessObjectType": "Account",
          "childBusinessObjectTypes": [
            "OpportunityItem",
            "OrderItem"
          ],
          "contextDataRecordId": "001xx000003GaX6AAK",
          "currentState": "CREATED",
          "lastUpdatedTimeStamp": "2023-10-11 04:46:13.804"
        }
      }
    ]
  }
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `dataPath` | String[] | Record IDs that identify the queried record. | Small, 60.0 | 60.0 |
| `queryResult` | [Query Context Record Result](./connect-responses-query-context-record-result.md) | Records returned for this data path, including child records. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-query-context-record-result-data.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
