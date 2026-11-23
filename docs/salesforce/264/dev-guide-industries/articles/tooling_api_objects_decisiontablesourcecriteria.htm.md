---
page_id: tooling_api_objects_decisiontablesourcecriteria.htm
title: DecisionTableSourceCriteria
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_decisiontablesourcecriteria.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: dt_setup_objects.htm
fetched_at: 2026-11-23
---

# DecisionTableSourceCriteria

Represents the fields and values from a data source that are used to
define the condition logic of the data that's used in a decision table. This object is
available in API version 59.0 and later.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### DecisionTableId

- **Type**: reference
- **Properties**: Create, Filter, Group, Sort
- **Description**: The ID of the decision table that’s associated with the source
  criteria.

  This field is a relationship field.
- **Relationship Name**: DecisionTable
- **Relationship Type**: Lookup
- **Refers To**: DecisionTable

### ManageableState

### Operator

- **Type**: picklist
- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist,
  Sort, Update
- **Description**: The operator that’s applied to an associated decision table’s
  field to filter the data.
- **Default value**: `Equals`
- **Possible values**:
  - `Contains`—Available in
    API version 64.0 and later.
  - `DoesNotExistIn`
  - `DoesNotMatch`—Available
    in API version 64.0 and later.
  - `Equals`
  - `ExistsIn`
  - `GreaterOrEqual`
  - `GreaterThan`
  - `IsNotNull`
  - `IsNull`
  - `LessOrEqual`
  - `LessThan`
  - `Matches`
  - `NotEquals`

### SequenceNumber

- **Type**: int
- **Properties**: Create, Filter, Group, Sort, Update
- **Description**: The sequence number used in the associated decision table's source
  condition logic.

### SourceFieldName

- **Type**: string
- **Properties**: Create, Filter, Group, Sort, Update
- **Description**: The name of the field that's used in the decision table.

### Value

- **Type**: textarea
- **Properties**: Create, Nillable, Update
- **Description**: The value that’s expected in the source field used in the decision
  table.

### ValueType

- **Type**: picklist
- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist,
  Sort, Update
- **Description**: The type of the value that’s used to filter the source data.
- **Default value**: `Literal`
- **Possible values**:
  - `Formula`
  - `Literal`
  - `Lookup`
  - `Parameter`
  - `Picklist`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_decisiontablesourcecriteria.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
