---
page_id: connect-responses-query-records-result
title: Query Records Result
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-query-records-result.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
fetched_at: 2026-11-25
---

# Query Records Result

Output representation of the results when querying context records and their child records.

The result contains one entry for each data path in the request. Use `isSuccess` to see whether the query succeeded. Each entry links the data path to its [Query Context Record Result](./connect-responses-query-context-record-result.md), which contains the returned records.

## JSON Example

```
{
  "contextQueryRecordListId": "8c1f2a40-6b2e-4d1a-9c55-1e2b7a9d4f10",
  "isSuccess": true,
  "queryResults": [
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
  ]
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextQuery​RecordListId` | String | Unique ID of this query records result. | Small, 60.0 | 60.0 |
| `isSuccess` | Boolean | Indicates whether the query is successful `(true)` or not `(false)`. | Small, 60.0 | 60.0 |
| `queryResults` | [Query Context Record Result Data](./connect-responses-query-context-record-result-data.md)[] | List of query results, one for each data path. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-query-records-result.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
