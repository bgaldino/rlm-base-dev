---
page_id: tooling_api_objects_decisiontableparameter.htm
title: DecisionTableParameter
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_decisiontableparameter.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: dt_setup_objects.htm
fetched_at: 2026-06-25
---

# DecisionTableParameter

Represents an input or output field in a decision table. An input
field is a field in the business rule object or custom metadata type that contains values used
by the decision table to evaluate records and values. An output field is a field in the
business rule object or custom metadata type that contains the values provided as outcomes for
a rule. This object is available in API version 51.0 and later.

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

| Field | Details |
| --- | --- |
| DecisionTableId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The unique identifier of the associated decision table.  This is a relationship field.  Relationship Name  DecisionTable  Relationship Type  Lookup  Refers To  DecisionTable |
| DomainObject | Type  string  Properties  Create, Filter, Group, Sort  Description  For polymorhpic fields, indicates the domain object in the field hierarchy.  This field is available in API version 59.0 and later. |
| FieldName | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The API name of the field that’s selected as an input or output for the decision table. |
| FieldPath | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The path of the field used in a decision table in relation to the object that the field belongs to.  This field is available in API version 59.0 and later. |
| IsGroupByField | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether an input field is used to group the business rules of the decision table (`true`) or not (`false`).  The default value is `false`'.  This field is available in API version 55.0 and later. |
| IsRequired | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether a field is required to have input values when a look up is performed on the decision table (`true`) or not (`false`).  The default value is `false`'.  This field is available in API version 59.0 and later. |
| ManageableState | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package.  Possible values are:  - `beta`—Managed-Beta - `deleted`—Managed-Proposed-Deleted - `deprecated`—Managed-Proposed-Deprecated - `deprecatedEditable`—SecondGen-Installed-Deprecated - `installed`—Managed-Installed - `installedEditable`—SecondGen-Installed-Editable - `released`—Managed-Released - `unmanaged`—Unmanaged |
| Operator | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The operator used for the input field.  Possible values are:  - `Contains` - `DoesNotExistsIn` - `DoesNotMatch` - `Equals` - `ExistsIn` - `GreaterOrEqual` - `GreaterThan` - `IsNotNull` - `IsNull` - `LessOrEqual` - `LessThan` - `Matches` - `NotEquals` |
| Sequence | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The sequence in which input fields are processed. |
| SortType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Sort outputs of a decision table based on the values of the input or output parameter field. This field is available in API version 56.0 and later.  Possible values are:  - `AscNullFirst` - `AscNullLast` - `DescNullFirst` - `DescNullLast` - `None`  The default value is `None`. Outputs can’t be sorted based on picklist and multi-select picklist fields. |
| Usage | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The usage type of a field.  Possible values are:  - `INPUT` - `OUTPUT` - `ROWCRITERIA` |
