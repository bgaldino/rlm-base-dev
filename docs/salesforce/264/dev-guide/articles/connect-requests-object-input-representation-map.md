---
page_id: connect-requests-object-input-representation-map
title: Object Input Map
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-object-input-representation-map.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-requests
legacy_page_id: connect_requests_object_input_representation_map.htm
fetched_at: 2026-11-25
---

# Object Input Map

Input representation of an sObject record in a key-value map format.

## JSON Example

```
{
  "records": [
    {
      "referenceId": "refOrder",
      "record": {
        "attributes": {
          "type": "Order",
          "method": "PATCH",
          "id": "402xx000003KY5vJGH"
        },
        "Quantity": 5
      }
    }
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| `attributes` | Map <String, String> | Configuration input for the record process. Valid values are `type` —Type of sales transaction such as Quote or Order; `method` —HTTP methods such as POST, PATCH, and DELETE; `id` —Unique identifier for the record. Required for PATCH and DELETE operations; `criteria` —Criteria to group order or quote line items. For example, group order or quote line items based on a monthly billing frequency; or `action` —Action to group order or quote line items. Valid values are `GroupBy`, `Group`, `Ungroup`, `GroupAll`, or `DeleteGroup`. | Required | 60.0 |  |  |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-object-input-representation-map.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
