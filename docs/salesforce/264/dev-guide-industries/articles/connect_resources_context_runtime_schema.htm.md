---
page_id: connect_resources_context_runtime_schema.htm
title: Context Runtime Schema (DELETE)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_runtime_schema.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-11-23
---

# Context Runtime Schema (DELETE)

Clear runtime schema cache for context definitions and their associated mappings.

## Resource

```
/connect/context-runtime-schema/clear
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/context-runtime-schema/clear?contextDefinitionDevlName=CustomerProfile&contextMappingNames=StandardMapping,CustomMapping
```

## Available Version

65.0

## HTTP Methods

DELETE

## Request Parameters for DELETE

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionDevlName` | String | Developer name of the context definition whose runtime schema is to be cleared. | Required | 65.0 |
| `contextMappingNames` | String[] | Comma-separated list of mapping names to clear. If not provided, the default mapping for the definition is cleared. | Optional | 65.0 |

## Response Body for DELETE

This resource uses query parameters only and returns HTTP 204 No Content on
success.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_runtime_schema.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
