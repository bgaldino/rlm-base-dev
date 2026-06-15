---
page_id: connect_requests_object_input_representation_map.htm
title: Object Input Map
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_object_input_representation_map.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Object Input Map

Input representation of an sObject record in a key-value map format.

JSON example
:   ```
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

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `attributes` | Map <String, String> | Configuration input for the record process. Valid values are:  - `type`—Type of sales   transaction such as Quote or Order. - `method`—HTTP methods such as   POST, PATCH, and DELETE. - `id`—Unique identifier for the   record. Required for PATCH and DELETE operations. - `criteria`—Criteria to group   order or quote line items. For example, group order or quote line items   based on a monthly billing frequency. - `action`—Action to group order   or quote line items. Valid values are:   - `GroupBy`   - `Group`   - `Ungroup`   - `GroupAll`   - `DeleteGroup` | Required | 60.0 |
