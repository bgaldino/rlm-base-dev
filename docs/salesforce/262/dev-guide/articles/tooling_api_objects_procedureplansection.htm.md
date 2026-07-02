---
page_id: tooling_api_objects_procedureplansection.htm
title: ProcedurePlanSection
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/tooling_api_objects_procedureplansection.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_tooling_api_parent.htm
fetched_at: 2026-06-09
---

# ProcedurePlanSection

Represents various procedure setup sections for a procedure plan
definition. Each section enables the setup of a procedure of a type that can be further
determined by using a rule-based criteria or it can be set based on a selected lookup
table. This object is available in API version 62.0 and later.

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
| Description | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The description of the procedure plan section. |
| IsInherited | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort  Description  Indicates if the section is inherited from a template (`true`) ot not (`false`).  The default value is `false`. |
| Phase | Type  string  Properties  Create, Filter, Nillable, Sort, Update  Description  The phase associated with the procedure plan section record. |
| ProcedurePlanVersionId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The procedure plan version associated with this procedure plan section record.  This field is a relationship field.  Relationship Name  ProcedurePlanVersion  Relationship Type  Master-detail  Refers To  ProcedurePlanDefinitionVersion (the master object) |
| ResolutionType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The type of resolution used to filter the procedure.  Valid values are:  - `Default` - `RuleBased` |
| SectionType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort  Description  The type of procedure section.  Valid values are:  - `Custom` - `PricingDiscoveryProcedure` - `PricingProcedure` - `ProductDiscoveryProcedure` |
| Sequence | Type  int  Properties  Create, Filter, Group, Sort, Update  Description  The sequence in which the procedures are processed. |
| SubSectionType | Type  string  Properties  Create, Filter, Group, Sort  Description  The procedure subsection added to the procedure plan definition. |
