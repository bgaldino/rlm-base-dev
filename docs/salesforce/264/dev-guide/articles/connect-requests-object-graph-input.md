---
page_id: connect-requests-object-graph-input
title: Object Graph Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-object-graph-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-requests
legacy_page_id: connect_requests_object_graph_input.htm
fetched_at: 2026-11-25
---

# Object Graph Input

Input representation of an sObject with a graph ID.

## JSON Example

```
{
  "graph": {
    "graphId": "1",
    "records": [
      {
        "referenceId": "refOrder",
        "record": {
          "attributes": {
            "type": "Order",
            "method": "POST"
          }
        }
      }
    ]
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `graphId` | String | The ID of the graph. | Required | 60.0 |
| `records` | [Object with Reference Input](./connect-requests-object-with-reference-input.md)[] | List of the records to be ingested. | Required | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-object-graph-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
