---
page_id: connect-requests-configurator-updated-node-input
title: Configurator Updated Node Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-configurator-updated-node-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-requests
legacy_page_id: connect_requests_configurator_updated_node_input.htm
fetched_at: 2026-11-25
---

# Configurator Updated Node Input

Input representation of the nodes to be updated in a product configuration.

## JSON Example

This example updates a field on an already-added sales transaction item. The path uses the persistent Salesforce record ID, not a `ref_*` reference. Only include the changed fields in `updatedAttributes`.

```
{
  "updatedNodes": [
    {
      "path": ["801xx0000000001AAA", "802xx0000000001AAA"],
      "updatedAttributes": {
        "businessObjectType": "OrderItem",
        "Quantity": 5
      }
    }
  ]
}
```

This example updates an attribute value on an already-added sales transaction item attribute. The path uses the persistent attribute record ID. Only include the changed fields in `updatedAttributes`. When a constraint model is active, include `AttributeName` and set it to the attribute’s developer name.

```
{
  "updatedNodes": [
    {
      "path": ["801xx0000000001AAA", "802xx0000000001AAA", "0AZxx0000000001AAA"],
      "updatedAttributes": {
        "businessObjectType": "OrderItemAttribute",
        "AttributeName": "Length",
        "AttributeValue": "10",
        "AttributePicklistValue": null
      }
    }
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `path` | String[] | Path to the node that’s being updated. | Required | 60.0 |
| `updated​Attributes` | Map<String, Object> | Details of the object that’s being updated. This property supports fields of objects from the Sales Transaction context definition, including custom objects and fields in your extended context definition. When you update an `OrderItemAttribute` or `QuoteLineItemAttribute` node and a constraint model is active, include `AttributeName` and set it to the product attribute’s developer name. For matching behavior and default fallback, see [Configurator API: Include the Attribute Developer Name When Creating or Updating Attributes](./cml-best-practice-attribute-name.md). | Required | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-configurator-updated-node-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
