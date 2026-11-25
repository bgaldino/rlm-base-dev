---
page_id: tooling-api-objects-decisiontableparameter
title: DecisionTableParameter
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-decisiontableparameter.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: dt-setup-objects
legacy_page_id: tooling_api_objects_decisiontableparameter.htm
fetched_at: 2026-11-25
---

# DecisionTableParameter

Represents an input or output field in a decision table. An input field is a field in the business rule object or custom metadata type that contains values used by the decision table to evaluate records and values. An output field is a field in the business rule object or custom metadata type that contains the values provided as outcomes for a rule. This object is available in API version 51.0 and later.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

### DataType

- 

**Type**: picklist

- 

**Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- 

**Description**: The data type of the field that’s used in a decision table.

This field is available in API version 59.0 and later.

- 

**Possible values**:

  - `Boolean`

  - `Currency`

  - `Date`

  - `Number`

  - `Percent`

  - `String`

### DecimalScale

- 

**Type**: int

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The number of digits to the right of the decimal point.

This field is available in API version 59.0 and later.

### DecisionTableId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort

- 

**Description**: The unique identifier of the associated decision table.

This is a relationship field.

- 

**Relationship Name**: DecisionTable

- 

**Relationship Type**: Lookup

- 

**Refers To**: DecisionTable

### DomainObject

- 

**Type**: string

- 

**Properties**: Create, Filter, Group, Sort

- 

**Description**: For polymorhpic fields, indicates the domain object in the field hierarchy.

This field is available in API version 59.0 and later.

### FieldName

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The API name of the field that’s selected as an input or output for the decision table.

### FieldPath

- 

**Type**: string

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The path of the field used in a decision table in relation to the object that the field belongs to.

This field is available in API version 59.0 and later.

### IsGroupByField

- 

**Type**: boolean

- 

**Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- 

**Description**: Indicates whether an input field is used to group the business rules of the decision table (`true`) or not (`false`).

This field is available in API version 55.0 and later.

- 

**Default value**: `false`

### IsPriorityField

- 

**Type**: boolean

- 

**Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- 

**Description**: Indicates whether a field is given priority (`true`) or not (`false`).

This field is available in API version 59.0 and later.

- 

**Default value**: `false`

### IsRequired

- 

**Type**: boolean

- 

**Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- 

**Description**: Indicates whether a field is required to have input values when a look up is performed on the decision table (`true`) or not (`false`).

This field is available in API version 59.0 and later.

- 

**Default value**: `false`

### Length

- 

**Type**: int

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The maximum number of characters supported for a field that’s used in a decision table.

This field is available in API version 59.0 and later.

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

### Operator

- 

**Type**: picklist

- 

**Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- 

**Description**: The operator used for the input field.

- 

**Possible values**:

  - `Contains`

  - `DoesNotExistsIn`

  - `DoesNotMatch`

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

### Sequence

- **Type**: int

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The sequence in which input fields are processed.

### SortType

- 

**Type**: picklist

- 

**Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- 

**Description**: Sort outputs of a decision table based on the values of the input or output parameter field. This field is available in API version 56.0 and later.

Outputs can’t be sorted based on picklist and multi-select picklist fields.

- 

**Default value**: `None`

- 

**Possible values**:

  - `AscNullFirst`

  - `AscNullLast`

  - `DescNullFirst`

  - `DescNullLast`

  - `None`

### Usage

- 

**Type**: picklist

- 

**Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- 

**Description**: Required. The usage type of a field.

- 

**Possible values**:

  - `INPUT`

  - `OUTPUT`

  - `ROWCRITERIA`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-decisiontableparameter.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
