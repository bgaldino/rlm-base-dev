---
page_id: connect_resources_create_update_query_data_record_status.htm
title: Query Record Status (PATCH, POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_create_update_query_data_record_status.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-11-23
---

# Query Record Status (PATCH, POST)

Update the processing status and related error messages of query data records. Create
the processing status and related error messages of query data records

## Resource

```
/connect/contexts/query-record-status
```

## Example for PATCH

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/contexts/query-record-status/18732dfd
```

## Example for POST

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/contexts/query-record-status/18732dfd
```

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

PATCH, POST

## Request Body for POST

### JSON example

```
{
    "queryRecordStatusInput": {
        "contextId": "3729ed60-d16d-41b8-8951-9ad4f6407ad2",
        "queryPaths": [
            {
                "dataPath": [
                    "TestOrder123"
                ]
            }
        ]
    }
}
```

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `queryRecordStatusInput` | Object | Input representation for context ID and the list of paths for querying the status. | Required | 59.0 |

### JSON example

```
{
  "contextId": "3729ed60-d16d-41b8-8951-9ad4f6407ad2",
  "queryPaths": [
    {
      "dataPath": [
        "TestOrder123"
      ]
    }
  ]
}
```

## Response Body for PATCH

[Context
Output](./connect_responses_context_output.htm.md "Output Representation of attributes associated with defined context.")

## Response Body for POST

[Query
Record Status Result](./connect_responses_query_record_status_result.htm.md "Output representation of query result status of context data records.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_create_update_query_data_record_status.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
