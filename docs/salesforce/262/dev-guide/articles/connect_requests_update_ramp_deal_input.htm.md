---
page_id: connect_requests_update_ramp_deal_input.htm
title: Update Ramp Deal Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_update_ramp_deal_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Update Ramp Deal Input

Input representation of the request to update a ramp deal.

JSON example
:   ```
    {
      "executionSettings": {
           "executePricing": true,
           "executeConfigRules": false
      },
      "addedNodes": [
        {
          "contextNodePath": [
            "4f23961a5c98806f89305e064c67b397e93f1bb8a2a7a3a80db506f1d4110ee9", // Context ID
            "0Q0xx0000004CPACA2", //Quote or Order ID
            "RandomUUID" // random UUID for Quote Line Item or Order Item ID
          ],
          "contextNode": {
             "Discount": 10,
             "Quantity": 5,
             "ItemSegmentName": "Year 5",
             "StartDate":"2024-09-07T00:00:00.000Z",
             "EndDate":"2024-09-07T00:00:00.000Z"
          }
        }
      ],
      "updatedNodes": [
         {
          "contextNodePath": [
            "4f23961a5c98806f89305e064c67b397e93f1bb8a2a7a3a80db506f1d4110ee9", // Context ID
            "0Q0xx0000004CPACA2", //Quote or Order ID
            "0QLxx0000004CfIGAU" // Quote Line ID or Order Line ID to update
          ],
          "contextNode": {
              "Discount": 10,
              "Quantity": 5
          }
        } 
      ],
      "deletedNodes": [
        {
          "contextNodePath": [
            "4f23961a5c98806f89305e064c67b397e93f1bb8a2a7a3a80db506f1d4110ee9",
            "0Q0xx0000004CPACA2",
            "0QLxx0000004CfIGAU" // Quote Line Item ID to delete
          ]
        }
      ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `added​Nodes` | [Context Node Input](./connect_requests_context_node_input.htm.md "Input representation of the details of the context nodes for ramp segments.")[] | Details of the nodes to be added. | Required | 62.0 |
    | `deleted​Nodes` | [Context Node Input](./connect_requests_context_node_input.htm.md "Input representation of the details of the context nodes for ramp segments.")[] | Details of the nodes to be deleted. | Required | 62.0 |
    | `execution​Settings` | [Execution Settings Input](./connect_requests_execution_settings_input.htm.md "Input representation of the execution settings for a ramp deal.")[] | Settings to run the pricing or configuration rules. | Optional | 62.0 |
    | `updated​Nodes` | [Context Node Input](./connect_requests_context_node_input.htm.md "Input representation of the details of the context nodes for ramp segments.")[] | Details of the nodes to be updated. | Required | 62.0 |
