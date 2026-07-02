---
page_id: sforce_api_objects_calculationmatrix.htm
title: CalculationMatrix
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_calculationmatrix.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_standard_objects.htm
fetched_at: 2026-06-25
---

# CalculationMatrix

Matches input values to a table row and returns the row's output
values. The label for this object is Decision Matrix. This object is available in API
version 53.0 and later.

Decision Matrices are useful for implementing complex rules in a systematic, readable
way. There are two types: Standard and Grouped. A Grouped Decision Matrix groups rows in
different versions by one or two keys such as geographic region or product code.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search(),`
`undelete()`, `update()`, `upsert()`

## Special Access Rules

Access to Decision Matrices requires Omnistudio
licenses.

## Fields

| Field | Details |
| --- | --- |
| DecisionMatrixDefinitionId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort  Description  The decision matrix definition record associated with this calculation matrix.  This field is a polymorphic relationship field.  Relationship Name  DecisionMatrixDefinition  Relationship Type  Lookup  Refers To  DecisionMatrixDefinition, DecisionTable |
| DecisionMatrixType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the type of lookup table.  Possible values are:  - `DecisionMatrix` - `DecisionTable`  The default value is `DecisionMatrix`. |
| Description | Type  textarea  Properties  Create, Nillable, Update  Description  A text description of the Decision Matrix. |
| GroupKey | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  A key for grouping matrix rows in different versions, such as geographic region or product code. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record, a record related to this record, or a list view. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, it's possible the user only accessed this record or list view (LastReferencedDate) but didn't view it. |
| MigrationStatus | Type  textarea  Properties  Nillable  Description  The status of migrating the data from the Calculation Matrix object to the Decision Matrix Definition object. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The Decision Matrix name. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who currently owns this matrix. Default value is the user logged in to the API to perform the create action.  This is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| SubGroupKey | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  A subkey for grouping matrix rows in different versions, such as geographic region or product code. For example, if the GroupKey is `Country`, the SubGroupKey can be `State` or `Province`. |
| Type | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The Decision Matrix type. A Standard Decision Matrix has no special features. A Grouped Decision Matrix groups rows by one or two keys (GroupKey and SubGroupKey) such as geographic region or product code.  Possible values are:  - `Grouped` - `Standard` |
| UniqueName | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The unique identifier of the record, which is sourced from the value in the Name field of CalculationMatrix (decision matrix). For example, if the name of the calculation matrix is sample matrix, its UniqueName would be sample\_matrix. |
| UsageType | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  A decision matrix’s usage type.  Available in API version 59.0 and later.  Possible value is:  - `Bre`-Default   When Business Rules Engine is enabled on your Salesforce org, the default value is Bre. Other usage types may be available to you depending on your industry solution and permission sets. |

## Usage

Expression Sets, OmniScripts, and Integration Procedures can call Decision Matrices.
