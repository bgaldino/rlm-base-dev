---
page_id: sforce_api_objects_expressionset.htm
title: ExpressionSet
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_expressionset.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_standard_objects.htm
fetched_at: 2026-06-25
---

# ExpressionSet

Represents information about an expression set. An expression set
performs a series of calculations using lookups and user-defined variables and
constants. This object is available in API version 55.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| ApiName | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The API name of the expression set. This field is unique within your organization. This is a required field. |
| Description | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The description of the expression set. |
| ExecutionScale | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies the scale of the input that an expression set processes. The scale determines where the expression set is executed.  Possible values are:  - `High` - `Low` |
| ExpressionSetDefinitionId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The expression set definition record associated with this expression set. This is a required field.  This is a relationship field.  Relationship Name  ExpressionSetDefinition  Relationship Type  Lookup  Refers To  ExpressionSetDefinition |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record, a record related to this record, or a list view. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, it's possible the user only accessed this record or list view (LastReferencedDate) but didn't view it. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the expression set. This is a required field. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who currently owns this expression set. Default value is the user logged in to the API to perform the create action  This is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| Type | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The type of the expression set.  Possible values are:  - `Custom` - `Standard` |
| UsageType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The type of industry that’s using the expression set.  Possible values are:  - `Bre`  Note Note When Business Rules Engine is enabled for a Salesforce instance, the default value is '`Bre`’. Other usage types may be available to you depending on your industry solution and permission sets. |
