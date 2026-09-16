---
page_id: connect_requests_context_node_input.htm
title: Context Node Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_context_node_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Node Input

Input representation of the details of the context nodes for ramp segments.

**JSON example**

: 

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

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `context​Node` | Map<String, Object> | Details of the context node to be added, updated, or deleted. | Required | 62.0 |
| `contextNode​Path` | String[] | Path to the context node to be added, updated, or deleted. | Required | 62.0 |
