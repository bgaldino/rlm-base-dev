---
page_id: tooling_api_objects_procedureplanoption.htm
title: ProcedurePlanOption
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/tooling_api_objects_procedureplanoption.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_tooling_api_parent.htm
fetched_at: 2026-06-09
---

# ProcedurePlanOption

Represents the selection criteria of how a procedure can be
configured for a selected procedure plan section record. This object is available in
API version 62.0 and later.

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
| ApexClassId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The Apex class associated with the procedure plan option record.  This field is a relationship field.  Relationship Name  ApexClass  Refers To  ApexClass |
| ApexClassName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The name of the Apex class associated with the procedure plan option record. |
| CriteriaLogic | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The computation logic for the various conditions applied to an option. |
| CtxDefinitionOutputFieldId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The context definition field that’s associated with the decision table.  This field is a relationship field.  Relationship Name  CtxDefinitionOutputField  Refers To  DecisionTableParameter |
| CtxMappingOutputFieldId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The context mapping field that’s associated with the decision table.  This field is a relationship field.  Relationship Name  CtxMappingOutputField  Refers To  DecisionTableParameter |
| DecisionTableId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The decision table associated with the pricing procedure.  This field is a relationship field.  Relationship Name  DecisionTable  Refers To  DecisionTable |
| ExpressionSetApiName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The API name of the expression set. |
| ExpressionSetDefinitionId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The expression set definition associated with the procedure plan option record.  This field is a relationship field.  Relationship Name  ExpressionSetDefinition  Refers To  ExpressionSetDefinition |
| ExpressionSetLabel | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The label of the expression set definition. |
| ExpressionSetOutputFieldId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The expression set output field that’s associated with the decision table.  This field is a relationship field.  Relationship Name  ExpressionSetOutputField  Refers To  DecisionTableParameter |
| PrimaryObject | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The procedure plan definition associated with the procedure plan option record. |
| Priority | Type  int  Properties  Create, Filter, Group, Sort  Description  The order in which the options are executed. |
| ProcedurePlanSectionId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The procedure plan section associated with the procedure plan option record.  This field is a relationship field.  Relationship Name  ProcedurePlanSection  Relationship Type  Master-detail  Refers To  ProcedurePlanSection (the master object) |
| ReadContextMapping | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The read context mapping used to read from the mapped object and populate the context definition. |
| SaveContextMapping | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The save context mapping used to save from the context definition and populate the mapped object. |
