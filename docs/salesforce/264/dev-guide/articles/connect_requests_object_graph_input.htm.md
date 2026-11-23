---
page_id: connect_requests_object_graph_input.htm
title: Object Graph Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_object_graph_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-11-23
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
| `records` | [Object with Reference Input](./connect_requests_object_with_reference_input.htm.md "Input representation of a list of records to be inserted or updated. To update a record, specify the record ID.")[] | List of the records to be ingested. | Required | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_object_graph_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
