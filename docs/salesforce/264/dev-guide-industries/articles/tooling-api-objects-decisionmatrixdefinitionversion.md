---
page_id: tooling-api-objects-decisionmatrixdefinitionversion
title: DecisionMatrixDefinitionVersion
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-decisionmatrixdefinitionversion.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-tables-tooling-objects-parent
legacy_page_id: tooling_api_objects_decisionmatrixdefinitionversion.htm
fetched_at: 2026-11-25
---

# DecisionMatrixDefinitionVersion

Represents information about a decision matrix definition version. This object is available in API version 55.0 and later.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### DecisionMatrixDefinitionId

- 

**Type**: reference

- 

**Properties**: Filter, Group, Sort

- 

**Description**: The decision matrix definition associated with this decision matrix definition version. This is a required field.

This field is a relationship field.

- 

**Relationship Name**: DecisionMatrixDefinition

- 

**Relationship Type**: Lookup

- 

**Refers To**: DecisionMatrixDefinition

### DeveloperName

- **Type**: string

- **Properties**: Filter, Group, Sort

- **Description**: The developer name of the decision matrix definition version.

### FullName

- **Type**: string

- **Properties**: Create, Group, Nillable

- **Description**: Full name of the associated metadata type in Metadata API. Query this field only if the query result contains no more than one record. Otherwise, an error is returned. If more than one record exists, use multiple queries to retrieve the records. This limit protects performance.

### Language

- 

**Type**: picklist

- 

**Properties**: Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort

- 

**Description**: The language in which this decision matrix definition version is created.

- 

**Possible values**:

  - `da`—Danish

  - `de`—German

  - `en_US`—English

  - `es`—Spanish

  - `es_MX`—Spanish (Mexico)

  - `fi`—Finnish

  - `fr`—French

  - `it`—Italian

  - `ja`—Japanese

  - `ko`—Korean

  - `nl_NL`—Dutch

  - `no`—Norwegian

  - `pt_BR`—Portuguese (Brazil)

  - `ru`—Russian

  - `sv`—Swedish

  - `th`—Thai

  - `zh_CN`—Chinese (Simplified)

  - `zh_TW`—Chinese (Traditional)

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

### MasterLabel

- **Type**: string

- **Properties**: Filter, Group, Sort

- **Description**: The label of the decision matrix definition version.

### Metadata

- **Type**: complexvalue

- **Properties**: Create, Nillable, Update

- **Description**: Decision matrix definition version metadata.

### NamespacePrefix

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The namespace prefix associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix.

### Status

- 

**Type**: picklist

- 

**Properties**: Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort

- 

**Description**: The status of this decision matrix definition version.

- 

**Default value**: `Draft`

- 

**Possible values**:

  - `Active`

  - `Draft`

  - `Inactive`

  - `InvalidDraft`

  - `Obsolete`

### VersionNumber

- **Type**: int

- **Properties**: Filter, Group, Sort

- **Description**: The version number of this decision matrix definition version. This is a required field.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-decisionmatrixdefinitionversion.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
