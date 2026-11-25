---
page_id: tooling-api-objects-contextnodeattrdictionary
title: ContextNodeAttrDictionary
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-contextnodeattrdictionary.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-tooling-api-parent
legacy_page_id: tooling_api_objects_contextnodeattrdictionary.htm
fetched_at: 2026-11-25
---

# ContextNodeAttrDictionary

Represents the relationship between the ContextNodeMapping and ContextDictionary objects as a junction table. This object is available in API version 62.0 and later.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### ContextAttrrDictIdentifier

- **Type**: string

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The developer name of the context attribute dictionary.

### ContextNodeId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The ID of the context node.

This field is a relationship field.

- 

**Relationship Name**: ContextNode

- 

**Relationship Type**: Lookup

- 

**Refers To**: ContextNode

### ContextNodeMapingId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The ID of the context node mapping.

This field is a relationship field.

- 

**Relationship Name**: ContextNodeMapping

- 

**Relationship Type**: Lookup

- 

**Refers To**: ContextNodeMapping

### ContextNodeTagPrefix

- **Type**: string

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The tag prefix of the context node that’s used to create the unique identifier of the parent context node.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-contextnodeattrdictionary.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
