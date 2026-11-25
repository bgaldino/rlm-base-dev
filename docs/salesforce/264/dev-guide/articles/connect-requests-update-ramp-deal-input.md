---
page_id: connect-requests-update-ramp-deal-input
title: Update Ramp Deal Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-update-ramp-deal-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-requests
legacy_page_id: connect_requests_update_ramp_deal_input.htm
fetched_at: 2026-11-25
---

# Update Ramp Deal Input

Input representation of the request to update a ramp deal.

## JSON Example

```
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

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `added​Nodes` | [Context Node Input](./connect-requests-context-node-input.md)[] | Details of the nodes to be added. | Required | 62.0 |
| `deleted​Nodes` | [Context Node Input](./connect-requests-context-node-input.md)[] | Details of the nodes to be deleted. | Required | 62.0 |
| `execution​Settings` | [Execution Settings Input](./connect-requests-execution-settings-input.md)[] | Settings to run the pricing or configuration rules. | Optional | 62.0 |
| `updated​Nodes` | [Context Node Input](./connect-requests-context-node-input.md)[] | Details of the nodes to be updated. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-update-ramp-deal-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
