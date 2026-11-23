---
page_id: connect_resources_query_context_interface_by_name.htm
title: Query Context Definition Interface By Name (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_query_context_interface_by_name.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-11-23
---

# Query Context Definition Interface By Name (GET)

Get the details of a context definition interface by using the context definition
interface name.

## Resource

```
/connect/context-definition-interfaces/contextDefinitionInterfaceName
```

## Section

The contextDefinitionInterfaceName path parameter is the API name
of the context definition interface.

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/context-definition-interfaces/exampleDefinitionInterface
```

## Available Version

62.0

## HTTP Methods

GET

## Response Body for GET

[Context Definition
Interface](./connect_responses_context_definition_interface.htm.md "Output representation of the details of the context definition interface.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_query_context_interface_by_name.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
