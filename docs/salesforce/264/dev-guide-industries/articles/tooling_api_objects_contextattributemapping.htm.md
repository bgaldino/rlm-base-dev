---
page_id: tooling_api_objects_contextattributemapping.htm
title: ContextAttributeMapping
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextattributemapping.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-11-23
---

# ContextAttributeMapping

Represents the relationship between the attribute defined in the context and
the values in the related objects. This object is available in API version 59.0 and
later.

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

### ContextAttributeId

- **Type**: reference
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The context attribute record associated with this context
  attribute mapping.

  This field is a relationship field.
- **Relationship Name**: ContextAttribute
- **Relationship Type**: Lookup
- **Refers To**: ContextAttribute

### ContextInputAttributeName

- **Type**: string
- **Properties**: Create, Filter, Group, Sort, Update
- **Description**: Stores the name of input attribute.

### ContextNodeMappingId

- **Type**: reference
- **Properties**: Create, Filter, Group, Sort
- **Description**: The context node mapping record that's associated with the context
  attribute mapping.

  This field is a relationship field.
- **Relationship Name**: ContextNodeMapping
- **Relationship Type**: Lookup
- **Refers To**: ContextNodeMapping

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

### InheritedFrom

- **Type**: string
- **Properties**: Create, Filter, Nillable, Sort, Update
- **Description**: The name of the parent context attribute mapping that's used to
  derive the current context attribute mapping. This field is
  available in API version 60.0 and later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextattributemapping.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
