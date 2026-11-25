---
page_id: connect-requests-context-node-mappings-input
title: Context Node Mappings Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-node-mappings-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-requests
fetched_at: 2026-11-25
---

# Context Node Mappings Input

Input representation of context node mapping.

## JSON Example

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

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `attributeMappings` | [Context Attribute Mappings Input](./connect-requests-context-attribute-mappings-input.md)[] | List of context attribute mappings. | Required | 59.0 |
| `contextNodeId` | String | Reference to context node. | Optional | 59.0 |
| `contextNodeMappingId` | String | ID of this context node mapping. Required for update. | Required | 59.0 |
| `sObjectName` | String | SObject name. | Optional | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-node-mappings-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
