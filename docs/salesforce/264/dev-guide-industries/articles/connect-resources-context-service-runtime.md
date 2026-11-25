---
page_id: connect-resources-context-service-runtime
title: Context Service (DELETE, GET)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-service-runtime.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: runtime-context-intance-management
legacy_page_id: connect_resources_context_service_runtime.htm
fetched_at: 2026-11-25
---

# Context Service (DELETE, GET)

Retrieve the context details using a context ID. Delete a context record using a context ID.

## Resource

```
/connect/contexts/${contextId}
```

## Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/contexts/c4c69a9a-3841-4fc3-a10d-a52779ade3d8
```

{yourInstance} is the domain name of your Salesforce instance.

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

DELETE, GET

## Response Body for GET

[Context Info](./connect-responses-context-info.md)

## Response Body for DELETE

None.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-service-runtime.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
