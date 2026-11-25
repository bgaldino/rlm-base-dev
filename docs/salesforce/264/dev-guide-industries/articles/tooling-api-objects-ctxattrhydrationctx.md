---
page_id: tooling-api-objects-ctxattrhydrationctx
title: CtxAttrHydrationCtx
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-ctxattrhydrationctx.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-tooling-api-parent
legacy_page_id: tooling_api_objects_ctxattrhydrationctx.htm
fetched_at: 2026-11-25
---

# CtxAttrHydrationCtx

Represents the queries that fetch the data for a chosen attribute from the input schema for context-to-context mapping This object is available in API version 61.0 and later.

## Supported Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### ContextAttributeMappingId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort

- 

**Description**: The context attribute mapping record that’s associated with the attribute hydration detail.

This field is a relationship field.

- 

**Relationship Name**: ContextAttributeMapping

- 

**Relationship Type**: Master-detail

- 

**Refers To**: ContextAttributeMapping (the master object)

### ContextQueryAttribute

- **Type**: string

- **Properties**: Create, Filter, Sort, Update

- **Description**: The attribute in context definition that’s the source of context hydration.

### InheritedFrom

- **Type**: string

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The name of the parent CtxAttrCtxHydrationDetail that’s used to derive the current CtxAttrCtxHydrationDetail.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-ctxattrhydrationctx.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
