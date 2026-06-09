---
page_id: sforce_api_objects_procedureplancriterion.htm
title: ProcedurePlanCriterion
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_procedureplancriterion.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProcedurePlanCriterion

The procedure plan option associated with the procedure plan criterion
record. This object is available in API version 67.0 and later.

## Supported Calls

`create()`, `delete()`,
`describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| ActualValue | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The user-defined value that is compared to the value of the SObject field value. |
| DataType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The data type of the field from the selected object. |
| FieldPath | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The path of the field used in a procedure in relation to the object that the field belongs to. |
| ObjectField | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The object field value used to resolve the procedure plan option. |
| Operator | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies the operator used by the procedure plan criterion.  Possible values are:  - Equals - GreaterThan - GreaterThanOrEquals - In - IsNotNull - IsNull - LessThan - LessThanOrEquals - NotEquals - NotIn |
| ProcedurePlanOptionId | Type  reference  Properties  Create, Filter, Group, Sort  Description  This field is a relationship field.  Relationship Name  ProcedurePlanOption  Relationship Type  Master-detail  Refers To  ProcedurePlanOption (the master object) |
| Sequence | Type  int  Properties  Create, Filter, Group, Sort  Description  The sequence in which the conditions defined in the procedure plan criteria are processed. |
