---
page_id: runtime-context-intance-management
title: Context Service Runtime
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/runtime-context-intance-management.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-resources
legacy_page_id: runtime_context_intance_management.htm
fetched_at: 2026-11-25
---

# Context Service Runtime

Create new runtime context instances, query data from context instances, and delete context instances.

- 

**[Context Service (POST)](./connect-resources-create-context.md)**

Create new context records by submitting metadata and associated JSON data. After validating the data, the system generates a new context ID. Context objects created using this API apply only to a single request. They cannot be used to pass data across multiple requests.

- 

**[Context Service (DELETE, GET)](./connect-resources-context-service-runtime.md)**

Retrieve the context details using a context ID. Delete a context record using a context ID.

- 

**[Context Attribute (PATCH)](./connect-resources-update-context-attribute.md)**

Update attributes of a context record.

- 

**[Context Runtime Schema (DELETE)](./connect-resources-context-runtime-schema.md)**

Clear runtime schema cache for context definitions and their associated mappings.

- 

**[Query Context Definition Interfaces (GET)](./connect-resources-query-context-interfaces.md)**

Get the lists of metadata associated with context definition interfaces.

- 

**[Query Context Definition Interface By Name (GET)](./connect-resources-query-context-interface-by-name.md)**

Get the details of a context definition interface by using the context definition interface name.

- 

**[Query Context Records and Children (POST)](./connect-resources-query-context-records.md)**

Query context records and their child records by data path.

- 

**[Query Record Status (PATCH, POST)](./connect-resources-create-update-query-data-record-status.md)**

Update the processing status and related error messages of query data records. Create the processing status and related error messages of query data records

- 

**[Query Tags (POST)](./connect-resources-create-query-tag.md)**

Create query tags within a defined context

- 

**[Write Through Tags (PATCH)](./connect-resources-write-through-tags.md)**

Update Context Attributes through tags.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/runtime-context-intance-management.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
