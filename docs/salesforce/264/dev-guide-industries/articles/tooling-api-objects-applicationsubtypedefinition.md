---
page_id: tooling-api-objects-applicationsubtypedefinition
title: ApplicationSubtypeDefinition
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-applicationsubtypedefinition.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Decision Explainer
parent_page: decision-explainer-tooling-api-parent
legacy_page_id: tooling_api_objects_applicationsubtypedefinition.htm
fetched_at: 2026-11-25
---

# ApplicationSubtypeDefinition

Represents a subtype of an application within an application domain. Available in API version 54.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### ApplicationUsageType

- 

**Type**: string

- 

**Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- 

**Description**: Specifies the application’s domain that defines the application’s subtype.

- 

**Default value**: `ExplainabilityService`

- 

**Possible values**:

  - `Explainability Service`

### Description

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The description of the application subtype definition record.

### DeveloperName

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The unique name of the application subtype definition.

### Language

- **Type**: string

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The language of the application subtype definition.

### ManageableState

- 

**Type**: string

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

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The UI label of the application subtype definition.

### NamespacePrefix

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The namespace prefix that is associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `namespacePrefix__componentName` notation.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-applicationsubtypedefinition.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
