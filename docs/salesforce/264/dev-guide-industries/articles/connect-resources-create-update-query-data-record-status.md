---
page_id: connect-resources-create-update-query-data-record-status
title: Query Record Status (PATCH, POST)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-create-update-query-data-record-status.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: runtime-context-intance-management
legacy_page_id: connect_resources_create_update_query_data_record_status.htm
fetched_at: 2026-11-25
---

# Query Record Status (PATCH, POST)

Update the processing status and related error messages of query data records. Create the processing status and related error messages of query data records

## Resource

```
/connect/contexts/query-record-status
```

## Example for PATCH

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/contexts/query-record-status/18732dfd
```

{yourInstance} is the domain name of your Salesforce instance.

## Example for POST

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/contexts/query-record-status/18732dfd
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

[Context Output](./connect-responses-context-output.md)

## Response Body for POST

[Query Record Status Result](./connect-responses-query-record-status-result.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-create-update-query-data-record-status.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
