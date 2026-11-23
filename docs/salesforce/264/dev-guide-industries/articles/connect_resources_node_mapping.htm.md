---
page_id: connect_resources_node_mapping.htm
title: Context Node Mapping (POST, PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_node_mapping.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_node_mapping_management.htm
fetched_at: 2026-11-23
---

# Context Node Mapping (POST, PATCH)

Create and update context node mappings.

## Resource

```
/connect/context-mappings/contextMappingId/context-node-mappings
```

## Example for POST

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-mappings/contextMappingId/context-node-mappings
```

## Example for PATCH

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-mappings/contextMappingId/context-node-mappings
```

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

POST, PATCH

## Request Body for POST

### JSON Example

```
{
    "contextNodeMappings": [
        {
            "contextNodeId": "11oxx000001G31BAAS",
            "sObjectName": "Order"
        },
        {
            "contextNodeId": "11oxx000001G31CAAS",
            "sObjectName": "OrderItem"
        }
    ]
}
```

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `attributeMappings` | [Context Attribute Mappings Input](./connect_requests_context_attribute_mappings_input.htm.md "Input representation of context attribute mapping.")[] | List of context attribute mappings. | Required | 59.0 |
| `contextNodeId` | String | Reference to context node. | Optional | 59.0 |
| `contextNodeMappingId` | String | ID of this context node mapping. Required for update. | Required | 59.0 |
| `sObjectName` | String | SObject name. | Optional | 59.0 |

## Response Body for POST

[Context Node Mapping List Output](./connect_responses_context_node_mapping_list.htm.md "Output representation of list of context node mappings.")

## Request Body for PATCH

### JSON Example

```
{
    "contextNodeMappings": [
        {
            "contextNodeMappingId": "11bxx000000YZipAAG",
            "sObjectName": "Quote"
        },
        {
            "contextNodeMappingId": "11bxx000000YZiqAAG",
            "sObjectName": "QuoteItem"
        }
    ]
}
```

## Response Body for PATCH

[Context Node Mapping List Output](./connect_responses_context_node_mapping_list.htm.md "Output representation of list of context node mappings.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_node_mapping.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
