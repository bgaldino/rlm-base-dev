---
page_id: tooling_api_objects_decisiontbldatasetparameter.htm
title: DecisionTblDatasetParameter
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_decisiontbldatasetparameter.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: dt_setup_objects.htm
fetched_at: 2026-11-23
---

# DecisionTblDatasetParameter

Represents the mapping between a decision table parameter and a field of the
object selected in the dataset link. This mapping allows the decision table to know which
object fields from the dataset link must be evaluated by the input fields of the decision
table. This object is available in API version 51.0 and later.

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

### DatasetFieldName

- **Type**: string
- **Properties**: Create, Filter, Group, Sort, Update
- **Description**: Required. The name of the field whose value must be compared against an
  input type decision table parameter when providing the outcome.

### DatasetSourceObject

- **Type**: string
- **Properties**: Create,
  Filter, Group, Nillable,
  Sort,
  Update
- **Description**: The object whose field values are evaluated by the associated decision table
  to provide outcomes.

### DecisionTableDatasetLinkId

- **Type**: reference
- **Properties**: Create, Filter, Group, Sort
- **Description**: The unique identifier of the associated decision table dataset link.

  This is a relationship field.
- **Relationship Name**: DecisionTableDatasetLink
- **Relationship Type**: Lookup
- **Refers To**: DecisionTableDatasetLink

### DecisionTableParameterId

- **Type**: reference
- **Properties**: Create, Filter, Group, Sort, Update
- **Description**: Required. The unique identifier of the associated decision table
  parameter.

  This is a relationship field.
- **Relationship Name**: DecisionTableParameter
- **Relationship Type**: Lookup
- **Refers To**: DecisionTableParameter

### ManageableState

- **Details**:

  Type
  :   ManageableState enumerated list

  Properties
  :   Filter, Group, Nillable, Restricted picklist, Sort

  Description
  :   Indicates the manageable state of the specified component that is contained
      in a package:
      - `beta`
      - `deleted`
      - `deprecated`
      - `deprecatedEditable`
      - `installed`
      - `installedEditable`
      - `released`
      - `unmanaged`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_decisiontbldatasetparameter.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
