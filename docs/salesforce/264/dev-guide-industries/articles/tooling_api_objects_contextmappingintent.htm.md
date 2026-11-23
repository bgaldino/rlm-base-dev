---
page_id: tooling_api_objects_contextmappingintent.htm
title: ContextMappingIntent
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextmappingintent.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-11-23
---

# ContextMappingIntent

Represents the purpose associated to a context mapping. This object is
available in API version 61.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeSObjects()`,
`query()`,
`retrieve()`,
`update()`,
`upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### ContextMappingId

- **Type**: reference
- **Properties**: Create, Filter, Group, Sort
- **Description**: The context mapping that's associated with usage intent.

  This field is a relationship field.
- **Relationship Name**: ContextMapping
- **Relationship Type**: Master-detail
- **Refers To**: ContextMapping (the master object)

### MappingIntent

- **Type**: picklist
- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update
- **Description**: Specifies the purpose to identify the type of context mapping
  required.
- **Possible values**:
  - `association`—Association
  - `hydration`—Hydration
  - `persistence`—Persistence
  - `translation`—Translation

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextmappingintent.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
