---
page_id: tooling-api-objects-contextnodemapping
title: ContextNodeMapping
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-contextnodemapping.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-tooling-api-parent
legacy_page_id: tooling_api_objects_contextnodemapping.htm
fetched_at: 2026-11-25
---

# ContextNodeMapping

Represents the relationship between the node in the context and values in the input schema. This object is available in API version 59.0 and later.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### ContextMappingId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort

- 

**Description**: The context mapping record that’s associated with the context node mapping.

This field is a relationship field.

- 

**Relationship Name**: ContextMapping

- 

**Relationship Type**: Lookup

- 

**Refers To**: ContextMapping

### ContextNodeId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The context node record associated with this context node mapping.

This field is a relationship field.

- 

**Relationship Name**: ContextNode

- 

**Relationship Type**: Lookup

- 

**Refers To**: ContextNode

### ManageableState

- 

**Type**: picklist

- 

**Properties**: Filter, Group, Nillable, Restricted picklist, Sort

- 

**Description**: Indicates the manageable state of the specified component that is contained in a package.

- 

**Possible values**:

  - `beta`—Managed-Beta

  - `deleted`—Managed-Proposed-Deleted

  - `deprecated`—Managed-Proposed-Deprecated

  - `deprecatedEditable`—SecondGen-Installed-Deprecated

  - `installed`—Managed-Installed

  - `installedEditable`—SecondGen-Installed-Editable

  - `released`—Managed-Released

  - `unmanaged`—Unmanaged

### Object

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The name of the object used for the mapping.

### InheritedFrom

- **Type**: string

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The name of the parent context node mapping that’s used to derive the current context node mapping. This field is available in API version 60.0 and later.

### MappedContextDefinition

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The API name of the context definition when context-to-context mappings exist. This field is available in API version 61.0 and later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-contextnodemapping.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
