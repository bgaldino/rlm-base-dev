---
page_id: connect-requests-context-node-input
title: Context Node Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-context-node-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-requests
legacy_page_id: connect_requests_context_node_input.htm
fetched_at: 2026-11-25
---

# Context Node Input

Input representation of the details of the context nodes for ramp segments.

## JSON Example

```
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

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `context​Node` | Map<String, Object> | Details of the context node to be added, updated, or deleted. | Required | 62.0 |
| `contextNode​Path` | String[] | Path to the context node to be added, updated, or deleted. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-context-node-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
