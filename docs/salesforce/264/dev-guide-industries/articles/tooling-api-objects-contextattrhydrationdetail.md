---
page_id: tooling-api-objects-contextattrhydrationdetail
title: ContextAttrHydrationDetail
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-contextattrhydrationdetail.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-tooling-api-parent
legacy_page_id: tooling_api_objects_contextattrhydrationdetail.htm
fetched_at: 2026-11-25
---

# ContextAttrHydrationDetail

Represents the SOQL (database) queries that fetch data for a chosen attribute from the input schema. This object is available in API version 59.0 and later.

## Supported SOAP API Calls

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

**Relationship Type**: Lookup

- 

**Refers To**: ContextAttributeMapping

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

### ObjectName

- **Type**: string

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The name of the object used for the attribute hydration detail.

### ParentHydrationDetailId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The parent hydration detail attribute. Based on the attribute mapping, there can be more than one hydration information sources.

This field is a relationship field.

- 

**Relationship Name**: ParentHydrationDetail

- 

**Relationship Type**: Lookup

- 

**Refers To**: ContextAttrHydrationDetail

### QueryAttribute

- **Type**: string

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The SOQL or query that is the source of the hydration.

### InheritedFrom

- **Type**: string

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The name of the parent context attribute hydration detail that’s used to derive the current context attribute hydration detail. This field is available in API version 60.0 and later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-contextattrhydrationdetail.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
