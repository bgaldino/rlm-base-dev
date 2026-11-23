---
page_id: tooling_api_objects_contextattribute.htm
title: ContextAttribute
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextattribute.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-11-23
---

# ContextAttribute

Represents information about an attribute used to describe a context node.
Each node can have one or many attributes associated with it.  This object is
available in API version 59.0 and later.

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

### ContextNodeId

- **Type**: reference
- **Properties**: Create, Filter, Group, Sort
- **Description**: The context node record that's associated with the context
  attribute.

  This field is a relationship field.
- **Relationship Name**: ContextNode
- **Relationship Type**: Lookup
- **Refers To**: ContextNode

### DataType

- **Type**: picklist
- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update
- **Description**: Specifies the type of data that's stored in the context
  attribute.
- **Default value**: `string`
- **Possible values**:
  - `boolean`Boolean
  - `currency`—Currency
  - `date`—Date
  - `datetime`—Datetime
  - `lookup`—Lookup
  - `number`—Number
  - `percent`—Percent
  - `picklist`—Picklist
  - `reference`—Reference
  - `string`—String

### DomainSet

- **Type**: string
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The list of node references to show a parent-child relationship
  between nodes in a definition.

### FieldType

- **Type**: picklist
- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update
- **Description**: List of node references to depict parent/child relation between
  the nodes in a definition
- **Default value**: `input`
- **Possible values**:
  - `input`—INPUT
  - `inputoutput`—INPUTOUTPUT
  - `output`—OUTPUT

### IsKey

- **Type**: boolean
- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update
- **Description**: Indicates whether the attribute is a key attribute in the node
  (true) or not (false).
- **Default value**: `false`

### IsLocalizationDisabled

- **Type**: boolean
- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update
- **Description**: Indicates whether the context attribute is to be localized or
  not

  This field is available in API version 68.0 and later.
- **Default value**: `false`

### IsTransient

- **Type**: boolean
- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update
- **Description**: Indicates if an attribute must be skipped in context
  persistence.
- **Default value**: `false`

### IsValue

- **Type**: boolean
- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update
- **Description**: Indicates the attribute that identifies as a value in a node.
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
- **Description**: The name of the context attribute.

### InheritedFrom

- **Type**: string
- **Properties**: Create, Filter, Nillable, Sort, Update
- **Description**: The name of the parent attribute that's used to derive the current
  attribute. This field is available in API version 60.0 and
  later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextattribute.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
