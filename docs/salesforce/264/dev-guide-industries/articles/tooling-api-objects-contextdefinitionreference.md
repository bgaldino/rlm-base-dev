---
page_id: tooling-api-objects-contextdefinitionreference
title: ContextDefinitionReference
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-contextdefinitionreference.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-tooling-api-parent
legacy_page_id: tooling_api_objects_contextdefinitionreference.htm
fetched_at: 2026-11-25
---

# ContextDefinitionReference

Represents information about reference from one Context Definition to another Context Definition. This object is available in API version 60.0 and later.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### ContextDefinitionId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort

- 

**Description**: The context definition record that’s associated with the context definition reference.

This field is a relationship field.

- 

**Relationship Name**: ContextDefinition

- 

**Relationship Type**: Master-detail

- 

**Refers To**: ContextDefinition

### InheritedFrom

- **Type**: string

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The name of the parent context definition that’s used to derive the current context definition. This field is available in API version 60.0 and later.

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

### ReferenceContextDefinition

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: Specifies the referred context definition.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-contextdefinitionreference.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
