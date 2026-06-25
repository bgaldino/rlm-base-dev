---
page_id: sforce_api_objects_calculationmatrixrow.htm
title: CalculationMatrixRow
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_calculationmatrixrow.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_standard_objects.htm
fetched_at: 2026-06-25
---

# CalculationMatrixRow

Defines a row in a Decision Matrix. The label for this object is Decision
Matrix Row. This object is available in API version 53.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`undelete()`,
`update()`,
`upsert()`

## Special Access Rules

Access to Decision Matrices requires Omnistudio licenses.

## Fields

| Field | Details |
| --- | --- |
| CalculationMatrixVersionId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The ID of the Decision Matrix Version to which this row belongs.  This is a relationship field.  Relationship Name  CalculationMatrixVersion  Relationship Type  Lookup  Refers To  CalculationMatrixVersion |
| EndDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The last date on which this row version is active. Applicable if IsVersionEnabled is `true`. |
| InputData | Type  textarea  Properties  Create, Nillable, Update  Description  The input columns and associated values for this row of the matrix. |
| IsVersionEnabled | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Specifies whether the associated matrix version is active. Derived from the associated Decision Matrix Version (CalculationMatrixVersion object).  The default value is `false`. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The row name. |
| OutputData | Type  textarea  Properties  Create, Nillable, Update  Description  The output columns and associated values for this row of the matrix. |
| StartDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The first date on which this row version is active. Applicable if IsVersionEnabled is `true`. |
