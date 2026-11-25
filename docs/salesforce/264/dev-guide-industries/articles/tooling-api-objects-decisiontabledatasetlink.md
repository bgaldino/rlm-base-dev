---
page_id: tooling-api-objects-decisiontabledatasetlink
title: DecisionTableDatasetLink
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-decisiontabledatasetlink.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: dt-setup-objects
legacy_page_id: tooling_api_objects_decisiontabledatasetlink.htm
fetched_at: 2026-11-25
---

# DecisionTableDatasetLink

Represents a dataset link associated with a decision table. Use dataset links in a decision table to select an object whose records the decision table must evaluate and provide outcomes for. This object is available in API version 51.0 and later.

**Note:**

Dataset links are supported only for Standard decision tables.

**Note:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### DecisionTableId

- 

**Type**: reference

- 

**Properties**: Filter, Group, Sort

- 

**Description**: Required. The unique identifier of the associated decision table.

This is a relationship field.

- 

**Relationship Name**: DecisionTable

- 

**Relationship Type**: Lookup

- 

**Refers To**: DecisionTable

### Description

- **Type**: textarea

- **Properties**: Filter, Nillable, Sort

- **Description**: The description of the dataset link.

### DeveloperName

- **Type**: string

- **Properties**: Filter, Group, Sort

- **Description**: The developer name of the dataset link.

### FullName

- 

**Type**: string

- 

**Properties**: Create, Group, Nillable

- 

**Description**: The name of the decision table dataset link.

Query this field only if the query result contains no more than one record. Otherwise, an error is returned. If more than one record exists, use multiple queries to retrieve the records. This limit protects performance.

### IsDefault

- **Type**: boolean

- **Properties**: Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort

- **Description**: Indicates whether a dataset link is the default dataset link for a decision table.

### Language

- 

**Type**: picklist

- 

**Properties**: Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort

- 

**Description**: The language in which the dataset link is created.

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

**Type**: ManageableState enumerated list

- 

**Properties**: Filter, Group, Nillable, Restricted picklist, Sort

- 

**Description**: Indicates the manageable state of the specified component that is contained in a package:

  - `beta`

  - `deleted`

  - `deprecated`

  - `deprecatedEditable`

  - `installed`

  - `installedEditable`

  - `released`

  - `unmanaged`

### MasterLabel

- **Type**: string

- **Properties**: Filter, Group, Sort

- **Description**: The label of the dataset link.

### Metadata

- 

**Type**: complexvalue

- 

**Properties**: Create, Nillable, Update

- 

**Description**: Decision table dataset link metadata.

Query this field only if the query result contains no more than one record. Otherwise, an error is returned. If more than one record exists, use multiple queries to retrieve the records. This limit protects performance.

### NamespacePrefix

- 

**Type**: string

- 

**Properties**: Filter, Group, Nillable, Sort

- 

**Description**: The namespace prefix that is associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `namespacePrefix__componentName` notation. The namespace prefix can have one of the following values.

  - In Developer Edition orgs, `NamespacePrefix` is set to the namespace prefix of the org for all objects that support it, unless an object is in an installed managed package. In that case, the object has the namespace prefix of the installed managed package. This field’s value is the namespace prefix of the Developer Edition org of the package developer.

  - In orgs that are not Developer Edition orgs, `NamespacePrefix` is set only for objects that are part of an installed managed package. All other objects have no namespace prefix.

### SetupName

- **Type**: string

- **Properties**: Filter, Group, Sort

- **Description**: Required. The name of the dataset link, which appears in Setup.

### SourceObject

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The name of the dataset link’s source object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-decisiontabledatasetlink.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
