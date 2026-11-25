---
page_id: sforce-api-objects-calculationmatrixrow
title: CalculationMatrixRow
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-calculationmatrixrow.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-tables-standard-objects
legacy_page_id: sforce_api_objects_calculationmatrixrow.htm
fetched_at: 2026-11-25
---

# CalculationMatrixRow

Defines a row in a Decision Matrix. The label for this object is Decision Matrix Row. This object is available in API version 53.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

Access to Decision Matrices requires Omnistudio licenses.

## Fields

### CalculationMatrixVersionId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort, Update

- 

**Description**: The ID of the Decision Matrix Version to which this row belongs.

This is a relationship field.

- 

**Relationship Name**: CalculationMatrixVersion

- 

**Relationship Type**: Lookup

- 

**Refers To**: CalculationMatrixVersion

### EndDateTime

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The last date on which this row version is active. Applicable if `IsVersionEnabled` is `true`.

### InputData

- **Type**: textarea

- **Properties**: Create, Nillable, Update

- **Description**: The input columns and associated values for this row of the matrix.

### IsVersionEnabled

- **Type**: boolean

- **Properties**: Defaulted on create, Filter, Group, Sort

- **Description**: Specifies whether the associated matrix version is active. Derived from the associated Decision Matrix Version (CalculationMatrixVersion object).

- **Default value**: `false`

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The row name.

### OutputData

- **Type**: textarea

- **Properties**: Create, Nillable, Update

- **Description**: The output columns and associated values for this row of the matrix.

### StartDateTime

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The first date on which this row version is active. Applicable if `IsVersionEnabled` is `true`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-calculationmatrixrow.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
