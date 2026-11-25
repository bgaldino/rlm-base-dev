---
page_id: connect-resources-context-tag-id
title: Context Tag ID (GET, DELETE)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-tag-id.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-tag-managament
legacy_page_id: connect_resources_context_tag_id.htm
fetched_at: 2026-11-25
---

# Context Tag ID (GET, DELETE)

Query and delete a context tag.

## Resource

```
/connect/context-definitions/{contextDefinitionId}/context-tags/{contextTagId}
```

The {contextDefinitionId} parameter is the ID of the context definition.

The {contextTagId} parameter is the ID of the context tag.

## Example for GET

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-definitions/{contextDefinitionId}/context-tags/{contextTagId}
```

{yourInstance} is the domain name of your Salesforce instance.

## Example for DELETE

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-definitions/{contextDefinitionId}/context-tags/{contextTagId}
```

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

GET, DELETE

## Response Body for GET

[Context Attribute Tag Output](./connect-responses-context-attribute-tag.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-tag-id.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
