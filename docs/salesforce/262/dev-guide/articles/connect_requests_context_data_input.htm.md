---
page_id: connect_requests_context_data_input.htm
title: Context Data Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_context_data_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-06-09
---

# Context Data Input

Input representation of the context data.

JSON example
:   ```
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

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `nodeData` | Map<String, Object> | Details of the node. | Optional | 60.0 |
    | `nodeName` | String | Name of the node. | Optional | 60.0 |
