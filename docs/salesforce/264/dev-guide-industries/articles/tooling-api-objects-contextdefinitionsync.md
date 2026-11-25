---
page_id: tooling-api-objects-contextdefinitionsync
title: ContextDefinitionSync
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-contextdefinitionsync.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-tooling-api-parent
legacy_page_id: tooling_api_objects_contextdefinitionsync.htm
fetched_at: 2026-11-25
---

# ContextDefinitionSync

Stores information for the sync operation of the custom definition with the standard definition. This object is available in API version 62.0 and later.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### ContextDefinitionName

- **Type**: string

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The context definition the sync is running for.

### EndDateTime

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The date and time when the synchronization ends.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the context definition sync record. This is a default field created for a platform entity.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The ID of the owner who created the record. This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### StartDateTime

- **Type**: dateTime

- **Properties**: Create, Filter, Sort, Update

- **Description**: The date and time when the synchronization starts.

### Status

- 

**Type**: picklist

- 

**Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- 

**Description**: The status of the sync operation.

- 

**Possible values**:

  - `failed`

  - `in_progress`

  - `success`

### SynchronizationInformation

- **Type**: textarea

- **Properties**: Create, Nillable, Update

- **Description**: The details of the context definition synchronization.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-contextdefinitionsync.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
