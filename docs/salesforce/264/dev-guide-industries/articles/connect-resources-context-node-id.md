---
page_id: connect-resources-context-node-id
title: Context Node Id (GET, DELETE)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-node-id.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-node-management
legacy_page_id: connect_resources_context_node_id.htm
fetched_at: 2026-11-25
---

# Context Node Id (GET, DELETE)

Query and delete a context node using an Id.

## Resource

```
/connect/context-definitions/{contextDefinitionId}/context-nodes/{contextNodeId}
```

The {contextDefinitionId} parameter is the ID of the context definition.

The {contextNodeId} parameter is the ID of the context node.

## Example for GET

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-definitions/{contextDefinitionId}/context-nodes/{contextNodeId}
```

{yourInstance} is the domain name of your Salesforce instance.

## Example for POST

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-definitions/{contextDefinitionId}/context-nodes/{contextNodeId}
```

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

GET, DELETE

## Response Body for GET

[Context Node Output](./connect-responses-context-node.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-node-id.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
