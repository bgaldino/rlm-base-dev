---
page_id: connect_requests_context_data_input.htm
title: Context Data Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_context_data_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-11-23
---

# Context Data Input

Input representation of the context data.

## JSON Example

```
"additionalContextData":[
  {
  "nodeName": "Contract",
  "nodeData": {
    "id": "xxxxx231",
    "name": "Contract1"
    
  }
},
{
  "nodeName": "Lead",
  "nodeData": {
    "id": "lllllll31",
    "name": "Lead1"
    
  }
}]
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `nodeData` | Map<String, Object> | Details of the node. | Optional | 60.0 |
| `nodeName` | String | Name of the node. | Optional | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_context_data_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
