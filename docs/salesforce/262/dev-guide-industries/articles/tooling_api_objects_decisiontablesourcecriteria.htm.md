---
page_id: tooling_api_objects_decisiontablesourcecriteria.htm
title: DecisionTableSourceCriteria
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_decisiontablesourcecriteria.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: dt_setup_objects.htm
fetched_at: 2026-06-25
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

| Field | Details |
| --- | --- |
| DecisionTableId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the decision table that’s associated with the source criteria.  This field is a relationship field.  Relationship Name  DecisionTable  Relationship Type  Lookup  Refers To  DecisionTable |
| ManageableState | Type  ManageableState enumerated list  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package:  - `beta` - `deleted` - `deprecated` - `deprecatedEditable` - `installed` - `installedEditable` - `released` - `unmanaged` |
| Operator | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The operator that’s applied to an associated decision table’s field to filter the data.  Possible values are:  - `Contains`—Available in   API version 64.0 and later. - `DoesNotExistIn` - `DoesNotMatch`—Available   in API version 64.0 and later. - `Equals` - `ExistsIn` - `GreaterOrEqual` - `GreaterThan` - `IsNotNull` - `IsNull` - `LessOrEqual` - `LessThan` - `Matches` - `NotEquals`  The default value is `Equals`. |
| SequenceNumber | Type  int  Properties  Create, Filter, Group, Sort, Update  Description  The sequence number used in the associated decision table's source condition logic. |
| SourceFieldName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The name of the field that's used in the decision table. |
| Value | Type  textarea  Properties  Create, Nillable, Update  Description  The value that’s expected in the source field used in the decision table. |
| ValueType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The type of the value that’s used to filter the source data.  Possible values are:  - `Formula` - `Literal` - `Lookup` - `Parameter` - `Picklist`  The default value is `Literal`. |
