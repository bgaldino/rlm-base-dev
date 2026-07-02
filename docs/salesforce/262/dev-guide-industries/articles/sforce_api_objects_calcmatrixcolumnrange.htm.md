---
page_id: sforce_api_objects_calcmatrixcolumnrange.htm
title: CalcMatrixColumnRange
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_calcmatrixcolumnrange.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_standard_objects.htm
fetched_at: 2026-06-25
---

# CalcMatrixColumnRange

Represents information about a value in a decision matrix column when
the column is of the type number range or text range. This object is available in API
version 59.0 and later.

## Supported Calls

`create()`, `delete()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| CalculationMatrixColumnId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the decision matrix column associated with the column range value.  This field is a relationship field.  Relationship Name  CalculationMatrixColumn  Relationship Type  Lookup  Refers To  CalculationMatrixColumn |
| CalculationMatrixVersionId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The decision matrix version ID asociated with the column range value.  This field is a relationship field.  Relationship Name  CalculationMatrixVersion  Relationship Type  Lookup  Refers To  CalculationMatrixVersion |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the decision matrix column. |
| Occurrence | Type  int  Properties  Create, Filter, Group, Sort, Update  Description  The number of times a range value is used in a decision matrix version. |
| RangeStartValue | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The value that defines the start of a range. |
