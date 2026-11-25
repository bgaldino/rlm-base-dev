---
page_id: sforce-api-objects-calculationmatrix
title: CalculationMatrix
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-calculationmatrix.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-tables-standard-objects
legacy_page_id: sforce_api_objects_calculationmatrix.htm
fetched_at: 2026-11-25
---

# CalculationMatrix

Matches input values to a table row and returns the row’s output values. The label for this object is Decision Matrix. This object is available in API version 53.0 and later.

Decision Matrices are useful for implementing complex rules in a systematic, readable way. There are two types: Standard and Grouped. A Grouped Decision Matrix groups rows in different versions by one or two keys such as geographic region or product code.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`,` search(),` `undelete()`, `update()`, `upsert()`

## Special Access Rules

Access to Decision Matrices requires Omnistudio licenses.

## Fields

### DecisionMatrixDefinitionId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort

- 

**Description**: The decision matrix definition record associated with this calculation matrix.

This field is a polymorphic relationship field.

- 

**Relationship Name**: DecisionMatrixDefinition

- 

**Relationship Type**: Lookup

- 

**Refers To**: DecisionMatrixDefinition, DecisionTable

### DecisionMatrixType

- 

**Type**: picklist

- 

**Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- 

**Description**: Specifies the type of lookup table.

- 

**Default value**: `DecisionMatrix`

- 

**Possible values**:

  - `DecisionMatrix`

  - `DecisionTable`

### Description

- **Type**: textarea

- **Properties**: Create, Nillable, Update

- **Description**: A text description of the Decision Matrix.

### GroupKey

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: A key for grouping matrix rows in different versions, such as geographic region or product code.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last accessed this record, a record related to this record, or a list view.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed this record or list view. If this value is null, it’s possible the user only accessed this record or list view (`LastReferencedDate`) but didn’t view it.

### MigrationStatus

- **Type**: textarea

- **Properties**: Nillable

- **Description**: The status of migrating the data from the Calculation Matrix object to the Decision Matrix Definition object.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The Decision Matrix name.

### OwnerId

- 

**Type**: reference

- 

**Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- 

**Description**: The ID of the user who currently owns this matrix.

This is a polymorphic relationship field.

- 

**Default value**: the user logged in to the API to perform the create action.

- 

**Relationship Name**: Owner

- 

**Relationship Type**: Lookup

- 

**Refers To**: Group, User

### SubGroupKey

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: A subkey for grouping matrix rows in different versions, such as geographic region or product code. For example, if the `GroupKey` is `Country`, the `SubGroupKey` can be `State` or `Province`.

### Type

- 

**Type**: picklist

- 

**Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- 

**Description**: The Decision Matrix type. A Standard Decision Matrix has no special features. A Grouped Decision Matrix groups rows by one or two keys (`GroupKey` and `SubGroupKey`) such as geographic region or product code.

- 

**Possible values**:

  - `Grouped`

  - `Standard`

### UniqueName

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The unique identifier of the record, which is sourced from the value in the Name field of CalculationMatrix (decision matrix). For example, if the name of the calculation matrix is sample matrix, its UniqueName would be sample_matrix.

### UsageType

- 

**Type**: picklist

- 

**Properties**: Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort

- 

**Description**: A decision matrix’s usage type. Available in API version 59.0 and later.

When Business Rules Engine is enabled on your Salesforce org, Other usage types may be available to you depending on your industry solution and permission sets.

- 

**Default value**: `Bre`

- 

**Possible values**:

  - `Bre`-Default

## Usage

Expression Sets, OmniScripts, and Integration Procedures can call Decision Matrices.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-calculationmatrix.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
