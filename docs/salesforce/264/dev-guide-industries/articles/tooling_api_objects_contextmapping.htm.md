---
page_id: tooling_api_objects_contextmapping.htm
title: ContextMapping
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextmapping.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-11-23
---

# ContextMapping

Represents the mapping of both attributes and nodes to related objects.
This object is available in API version 59.0 and later.

## Supported SOAP API Calls

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

### ContextDefinitionVersionId

- **Type**: reference
- **Properties**: Create, Filter, Group, Sort
- **Description**: The context definition version record that's associated with the
  context mapping.

  This field is a relationship field.
- **Relationship Name**: ContextDefinitionVersion
- **Relationship Type**: Lookup
- **Refers To**: ContextDefinitionVersion

### Description

- **Type**: string
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The description of the context mapping.

### IsDefault

- **Type**: boolean
- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update
- **Description**: Indicates whether the mapping for a context definition version is
  default (true) or not (false).
- **Default value**: `false`

### ManageableState

- **Type**: picklist
- **Properties**: Filter, Group, Nillable, Restricted picklist, Sort
- **Description**: Indicates the manageable state of the specified component that is
  contained in a package.
- **Possible values**:
  - `beta`—Managed-Beta
  - `deleted`—Managed-Proposed-Deleted
  - `deprecated`—Managed-Proposed-Deprecated
  - `deprecatedEditable`—SecondGen-Installed-Deprecated
  - `installed`—Managed-Installed
  - `installedEditable`—SecondGen-Installed-Editable
  - `released`—Managed-Released
  - `unmanaged`—Unmanaged

### Title

- **Type**: string
- **Properties**: Create, Filter, Group, Sort, Update
- **Description**: The name of the context mapping.

### InheritedFrom

- **Type**: string
- **Properties**: Create, Filter, Nillable, Sort, Update
- **Description**: The name of the parent mapping that's used to derive the current
  mapping. This field is available in API version 60.0 and
  later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextmapping.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
