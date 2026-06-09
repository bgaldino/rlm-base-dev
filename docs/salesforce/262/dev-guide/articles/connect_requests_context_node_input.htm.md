---
page_id: connect_requests_context_node_input.htm
title: Context Node Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_context_node_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Context Node Input

Input representation of the details of the context nodes for ramp segments.

JSON example
:   ```
      "updatedNodes": [
         {
          "contextNodePath": [
            "4f23961a5c98806f89305e064c67b397e93f1bb8a2a7a3a80db506f1d4110ee9", // ContextId
            "0Q0xx0000004CPACA2", //Quote or OrderId
            "0QLxx0000004CfIGAU" // Quote Line ID or Order Line ID to update
          ],
          "contextNode": {
              "Discount": 10,
              "Quantity": 5
          }
        }, 
        {
          "contextNodePath": [
            "4f23961a5c98806f89305e064c67b397e93f1bb8a2a7a3a80db506f1d4110ee9",
            "0Q0xx0000004CPACA2",
            "2b6401d144904e10aa"
          ],
          "contextNode": {
              "Discount": 20,
              "Quantity": 15
          }
        }
      ]
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `context​Node` | Map<String, Object> | Details of the context node to be added, updated, or deleted. | Required | 62.0 |
    | `contextNode​Path` | String[] | Path to the context node to be added, updated, or deleted. | Required | 62.0 |
