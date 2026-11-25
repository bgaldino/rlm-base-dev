---
page_id: connect-resources-context-runtime-schema
title: Context Runtime Schema (DELETE)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-runtime-schema.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: runtime-context-intance-management
legacy_page_id: connect_resources_context_runtime_schema.htm
fetched_at: 2026-11-25
---

# Context Runtime Schema (DELETE)

Clear runtime schema cache for context definitions and their associated mappings.

## Resource

```
/connect/context-runtime-schema/clear
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/context-runtime-schema/clear?contextDefinitionDevlName=CustomerProfile&contextMappingNames=StandardMapping,CustomMapping
```

{yourInstance} is the domain name of your Salesforce instance.

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

This resource uses query parameters only and returns HTTP 204 No Content on success.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-runtime-schema.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
