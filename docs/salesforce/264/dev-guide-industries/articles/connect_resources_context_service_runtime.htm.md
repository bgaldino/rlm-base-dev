---
page_id: connect_resources_context_service_runtime.htm
title: Context Service (DELETE, GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_service_runtime.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-11-23
---

# Context Service (DELETE, GET)

Retrieve the context details using a context ID. Delete a context record using a
context ID.

## Resource

```
/connect/contexts/${contextId}
```

## Example

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/contexts/c4c69a9a-3841-4fc3-a10d-a52779ade3d8
```

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

DELETE, GET

## Response Body for GET

[Context Info](./connect_responses_context_info.htm.md "Output representation containing detailed information about a context.")

## Response Body for DELETE

None.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_service_runtime.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
