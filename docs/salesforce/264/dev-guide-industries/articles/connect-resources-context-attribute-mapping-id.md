---
page_id: connect-resources-context-attribute-mapping-id
title: Context Attribute Mapping ID (GET, DELETE)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-attribute-mapping-id.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-mapping-management
legacy_page_id: connect_resources_context_attribute_mapping_id.htm
fetched_at: 2026-11-25
---

# Context Attribute Mapping ID (GET, DELETE)

Query and delete a context attribute mapping using an ID.

## Resource

```
/connect/context-node-mappings/{contextNodeMappingId}/context-attribute-mappings/{contextAttributeMappingId}
```

The {contextNodeMappingId} parameter is the ID of the context node mapping.

The {contextAttributeMappingId} parameter is the ID of the context attribute mapping.

## Example for GET

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-node-mappings/{contextNodeMappingId}/context-attribute-mappings/{contextAttributeMappingId}
```

{yourInstance} is the domain name of your Salesforce instance.

## Example for DELETE

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-node-mappings/{contextNodeMappingId}/context-attribute-mappings/{contextAttributeMappingId}
```

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

GET, DELETE

## Response Body for GET

[Context Attribute Mapping Output](./connect-responses-context-attribute-mapping.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-attribute-mapping-id.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
