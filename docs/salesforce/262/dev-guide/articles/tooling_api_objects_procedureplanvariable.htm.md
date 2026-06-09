---
page_id: tooling_api_objects_procedureplanvariable.htm
title: ProcedurePlanVariable
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/tooling_api_objects_procedureplanvariable.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_tooling_api_parent.htm
fetched_at: 2026-06-09
---

# ProcedurePlanVariable

Represents the setup for any adhoc user-defined variable that can be
linked to a procedure plan definition record. This object is available in API version
62.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

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
| DataType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The data type of the input procedure plan variable. |
| DefaultValue | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The default value for the user-defined procedure plan variable. |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The unique name of the procedure plan variable record.  This name must begin with a letter and use only alphanumeric characters and underscores. It can't include spaces, end with an underscore, or have two consecutive underscores. |
| Label | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The label of the procedure plan variable. |
| ProcedurePlanVersionId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The procedure plan version associated with the procedure plan variable record.  This field is a relationship field.  Relationship Name  ProcedurePlanVersion  Relationship Type  Master-detail  Refers To  ProcedurePlanDefinitionVersion (the master object) |
