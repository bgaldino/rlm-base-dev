---
page_id: connect-resources-node-mapping
title: Context Node Mapping (POST, PATCH)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-node-mapping.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-node-mapping-management
legacy_page_id: connect_resources_node_mapping.htm
fetched_at: 2026-11-25
---

# Context Node Mapping (POST, PATCH)

Create and update context node mappings.

## Resource

```
/connect/context-mappings/{contextMappingId}/context-node-mappings
```

The {contextMappingId} parameter is the ID of the context mapping.

## Example for POST

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-mappings/{contextMappingId}/context-node-mappings
```

{yourInstance} is the domain name of your Salesforce instance.

## Example for PATCH

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-mappings/{contextMappingId}/context-node-mappings
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
| `attributeMappings` | [Context Attribute Mappings Input](./connect-requests-context-attribute-mappings-input.md)[] | List of context attribute mappings. | Required | 59.0 |
| `contextNodeId` | String | Reference to context node. | Optional | 59.0 |
| `contextNodeMappingId` | String | ID of this context node mapping. Required for update. | Required | 59.0 |
| `sObjectName` | String | SObject name. | Optional | 59.0 |

## Response Body for POST

[Context Node Mapping List Output](./connect-responses-context-node-mapping-list.md)

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

[Context Node Mapping List Output](./connect-responses-context-node-mapping-list.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-node-mapping.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
