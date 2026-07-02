---
page_id: tooling_api_objects_procedureplandefinitionversion.htm
title: ProcedurePlanDefinitionVersion
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/tooling_api_objects_procedureplandefinitionversion.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_tooling_api_parent.htm
fetched_at: 2026-06-09
---

# ProcedurePlanDefinitionVersion

Represents the versions for a procedure plan definition. Multiple
versions under a procedure plan definition must be active at a time, which can be resolved
at run
time
using the rank field. This object is available in API version 62.0 and
later.

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
| ContextDefinition | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The context definition associated with the procedure plan definition record.  Valid values are:  - `11ODU00000007Zx2AI` - `11ODU000000084F2AQ` - `CollectionPlanEvent__stdctx` - `CommerceCartContextDefinition__stdctx` - `SalesTransactionContext__stdctx` - `TestContextService__stdctx` - `TestDynamicAttribute__stdctx` - `TestExtendedDefinition__stdctx` |
| DefaultReadContextMapping | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The default read context mapping used to read from the mapped object and populate the context definition. |
| DefaultSaveContextMapping | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The save context mapping used to save from the context definition and populate the mapped object. |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The unique name of the procedure plan definition version record.  This name must begin with a letter and use only alphanumeric characters and underscores. It can't include spaces, end with an underscore, or have two consecutive underscores. |
| EffectiveFrom | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The date and time when the procedure plan definition comes into effect. |
| EffectiveTo | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the procedure plan definition is no longer in effect. |
| InheritedFrom | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort  Description  The template from which this procedure plan definition is created. |
| IsActive | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates if this procedure plan definition version is active (`true`) or not (`false`).  The default value is `false`. |
| ProcedurePlanDefinitionId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The procedure plan definition associated with this procedure plan definition version record.  This field is a relationship field.  Relationship Name  ProcedurePlanDefinition  Relationship Type  Master-detail  Refers To  ProcedurePlanDefinition (the master object) |
| Rank | Type  int  Properties  Create, Filter, Group, Sort, Update  Description  The current rank of the procedure plan definition version that’s used to determine which procedure plan definition version is executed . |
