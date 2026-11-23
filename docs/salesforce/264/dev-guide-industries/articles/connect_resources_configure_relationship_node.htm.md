---
page_id: connect_resources_configure_relationship_node.htm
title: Context Node Relationship (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_configure_relationship_node.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_node_mapping_management.htm
fetched_at: 2026-11-23
---

# Context Node Relationship (POST)

Configure a relationship node by adding child context nodes to a specific context
node.

## Resource

```
/connect/context-nodes/contextNodeId/configurerelationship
```

The contextNodeId specifies the ID of the context node to which you
want to add the context nodes from the request body as child nodes.

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/context-nodes/11oxx000001G3dtAAC/configurerelationship
```

## Available Version

61.0

## HTTP Methods

POST

## Request Body for POST

### JSON Example

```
{
  "contextNodeIds": [
    "11oxx000001G3dtAAC",
    "11oxx000001G3duAAC"
  ]
}
```

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextNodeIds` | String | List of context node IDs to create the relationship nodes by adding them as child nodes to the context node that’s specified in the endpoint. | Required | 61.0 |

## Response Body for POST

[Context Node List](./connect_responses_context_node_list.htm.md "Output representation of the list of context nodes.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_configure_relationship_node.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
