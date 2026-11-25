---
page_id: tooling-api-objects-contextdefinitionversion
title: ContextDefinitionVersion
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-contextdefinitionversion.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-tooling-api-parent
legacy_page_id: tooling_api_objects_contextdefinitionversion.htm
fetched_at: 2026-11-25
---

# ContextDefinitionVersion

Represents information about the context definition version. Only one version can be active at a time. This object is available in API version 59.0 and later.

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

**Description**: The context definition record associated with the context definition version.

This field is a relationship field.

- 

**Relationship Name**: ContextDefinition

- 

**Relationship Type**: Lookup

- 

**Refers To**: ContextDefinition

### EndDate

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The date and time when the context definition version becomes inactive.

### InheritedApexVersion

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The version of the Apex class generated from the context definition version. It is null when no Apex class is generated, 0.0 when an Apex class is generated for a custom definition, and equal to the value in InheritedVersionNumber when an Apex class is generated from an extended definition.

### IsActive

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Indicates whether the context definition version is active (true) or not (false).

- **Default value**: `false`

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

### StartDate

- **Type**: dateTime

- **Properties**: Create, Filter, Sort, Update

- **Description**: The date and time when the context definition version becomes active.

### VersionNumber

- **Type**: int

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The context definition version number.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-contextdefinitionversion.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
