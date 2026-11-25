---
page_id: tooling-api-objects-contexttag
title: ContextTag
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-contexttag.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-tooling-api-parent
legacy_page_id: tooling_api_objects_contexttag.htm
fetched_at: 2026-11-25
---

# ContextTag

Represents a shortened name of an attribute or node instead of its fully qualified tag structure name. This object is available in API version 59.0 and later.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### ContextAttributeId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The context attribute record that’s associated with the context tag.

This field is a relationship field.

- 

**Relationship Name**: ContextAttribute

- 

**Relationship Type**: Lookup

- 

**Refers To**: ContextAttribute

### ContextNodeId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The context node record that’s associated with the context tag.

This field is a relationship field.

- 

**Relationship Name**: ContextNode

- 

**Relationship Type**: Lookup

- 

**Refers To**: ContextNode

### Title

- **Type**: string

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The name of the context tag.

### InheritedFrom

- **Type**: string

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The name of the parent context tag that’s used to derive the current context tag. This field is available in API version 60.0 and later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-contexttag.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
