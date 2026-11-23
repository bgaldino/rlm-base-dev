---
page_id: tooling_api_objects_expressionsetdefinitionversion.htm
title: ExpressionSetDefinitionVersion
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_expressionsetdefinitionversion.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_tooling_objects_parent.htm
fetched_at: 2026-11-23
---

# ExpressionSetDefinitionVersion

Represents information about an expression set definition
version. This object is available in API version 55.0 and later.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### DeveloperName

- **Type**: string
- **Properties**: Filter, Group, Sort
- **Description**: The developer name of the expression set definition version.

### ExpressionSetDefinitionId

- **Type**: reference
- **Properties**: Filter, Group, Sort
- **Description**: The expression set definition record associated with this
  expression set definition version.

  This field is a relationship field.
- **Relationship Name**: ExpressionSetDefinition
- **Relationship Type**: Lookup
- **Refers To**: ExpressionSetDefinition

### FullName

- **Type**: string
- **Properties**: Create, Group, Nillable
- **Description**: Full name of the associated metadata type in Metadata API. Query
  this field only if the query result contains no more than one
  record. Otherwise, an error is returned. If more than one record
  exists, use multiple queries to retrieve the records. This limit
  protects performance.

### Language

- **Type**: picklist
- **Properties**: Defaulted on create, Filter, Group, Nillable, Restricted picklist,
  Sort
- **Description**: The language in which this expression set definition version is
  created.
- **Possible values**:
  - `da`—Danish
  - `de`—German
  - `en_US`—English
  - `es`—Spanish
  - `es_MX`—Spanish
    (Mexico)
  - `fi`—Finnish
  - `fr`—French
  - `it`—Italian
  - `ja`—Japanese
  - `ko`—Korean
  - `nl_NL`—Dutch
  - `no`—Norwegian
  - `pt_BR`—Portuguese
    (Brazil)
  - `ru`—Russian
  - `sv`—Swedish
  - `th`—Thai
  - `zh_CN`—Chinese
    (Simplified)
  - `zh_TW`—Chinese
    (Traditional)

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

### MasterLabel

- **Type**: string
- **Properties**: Filter, Group, Sort
- **Description**: The label of the expression set definition version.

### Metadata

- **Type**: complexvalue
- **Properties**: Create, Nillable, Update
- **Description**: Expression set definition version metadata.

### NamespacePrefix

- **Type**: string
- **Properties**: Filter, Group, Nillable, Sort
- **Description**: The namespace prefix associated with this object. Each Developer
  Edition org that creates a managed package has a unique namespace
  prefix.

### Status

- **Type**: picklist
- **Properties**: Defaulted on create, Filter, Group, Nillable, Restricted picklist,
  Sort
- **Description**: Indicates the status of the expression set definition
  version.
- **Default value**: `Draft`
- **Possible values**:
  - `Active`
  - `Draft`
  - `Inactive`
  - `InvalidDraft`
  - `Obsolete`

### VersionNumber

- **Type**: int
- **Properties**: Filter, Group, Sort
- **Description**: The version number of the expression set definition version. This
  is a required field.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_expressionsetdefinitionversion.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
