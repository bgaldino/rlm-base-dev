---
page_id: sforce-api-objects-calculationmatrixcolumn
title: CalculationMatrixColumn
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-calculationmatrixcolumn.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-tables-standard-objects
legacy_page_id: sforce_api_objects_calculationmatrixcolumn.htm
fetched_at: 2026-11-25
---

# CalculationMatrixColumn

Defines a column in a Decision Matrix. The label for this object is Decision Matrix Column. This object is available in API version 53.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

Access to Decision Matrices requires Omnistudio licenses.

## Fields

### ApiName

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The API name of the column.

### CalculationMatrixId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort

- 

**Description**: The ID of the Decision Matrix to which this column belongs.

This is a relationship field.

- 

**Relationship Name**: CalculationMatrix

- 

**Relationship Type**: Lookup

- 

**Refers To**: CalculationMatrix

### ColumnType

- 

**Type**: picklist

- 

**Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort

- 

**Description**: Specifies whether the column matches matrix input or is returned as output.

- 

**Possible values**:

  - `Input`

  - `Output`

### DataType

- 

**Type**: picklist

- 

**Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort

- 

**Description**: The type of data in the column.

- 

**Possible values**:

  - `Boolean`

  - `Currency`

  - `Number`

  - `NumberRange`

  - `Percent`

  - `Text`

  - `TextRange`

### DisplaySequence

- **Type**: int

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The position of this column in the column order.

### IsWildcardColumn

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Specifies that this column can contain a wildcard value such as `ALL`.

- **Default value**: `false`

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The column name.

### RangeValues

- **Type**: textarea

- **Properties**: Create, Nillable, Update

- **Description**: A list of values that define range boundaries.

### WildcardColumnValue

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The value that indicates a wildcard, for example `ALL`. Applicable if `IsWildcardColumn` is `true`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-calculationmatrixcolumn.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
