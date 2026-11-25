---
page_id: sforce-api-objects-calcmatrixcolumnrange
title: CalcMatrixColumnRange
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-calcmatrixcolumnrange.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-tables-standard-objects
legacy_page_id: sforce_api_objects_calcmatrixcolumnrange.htm
fetched_at: 2026-11-25
---

# CalcMatrixColumnRange

Represents information about a value in a decision matrix column when the column is of the type number range or text range. This object is available in API version 59.0 and later.

## Supported Calls

`create()`, `delete()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

### CalculationMatrixColumnId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort

- 

**Description**: The ID of the decision matrix column associated with the column range value.

This field is a relationship field.

- 

**Relationship Name**: CalculationMatrixColumn

- 

**Relationship Type**: Lookup

- 

**Refers To**: CalculationMatrixColumn

### CalculationMatrixVersionId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The decision matrix version ID asociated with the column range value.

This field is a relationship field.

- 

**Relationship Name**: CalculationMatrixVersion

- 

**Relationship Type**: Lookup

- 

**Refers To**: CalculationMatrixVersion

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name of the decision matrix column.

### Occurrence

- **Type**: int

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The number of times a range value is used in a decision matrix version.

### RangeStartValue

- **Type**: string

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The value that defines the start of a range.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-calcmatrixcolumnrange.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
