---
page_id: sforce_api_objects_expressionsetversion.htm
title: ExpressionSetVersion
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_expressionsetversion.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_standard_objects.htm
fetched_at: 2026-06-25
---

# ExpressionSetVersion

Represents information about a specific version of an expression set.
This object is also accessible through the UI API, which enables its use in components like
Lightning Web Components (LWC). This object is available in API version 55.0 and
later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| ApiName | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The API name of the expression set version. This is a required field and it requires a unique value. |
| Description | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The description of the expression set version, |
| DecimalScale | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The number of decimal places to apply to non-local resources such as context tags. |
| EndDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the expression set version becomes inactive. |
| ExpressionSetDefinitionVerId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The expression set definition version associated with this expression set version. This is a required field.  This is a relationship field.  Relationship Name  ExpressionSetDefinitionVer  Relationship Type  Lookup  Refers To  ExpressionSetDefinitionVersion |
| ExpressionSetId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the parent expression set record that’s associated with this expression set version. This is a required field.  This is a relationship field.  Relationship Name  ExpressionSet  Relationship Type  Lookup  Refers To  ExpressionSet |
| IsActive | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the expression set version is active (`true`) or not (`false`). This is a required field.  The default value is `false`. |
| IsLoopingEnabled | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether looping is active for this expression set version (`true`) or not (`false`).  The default value is `false`. |
| LatestSimulationResult | Type  textarea  Properties  Create, Nillable, Update  Description  The result of the simulation service that processes the input variables defined for the expression set version, in JSON format. |
| LoopEndVariableName | Type  textarea  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The name of the resource that’s used to determine which resource can be processed last in the loop. |
| LoopIncrementVariableName | Type  textarea  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The name of the variable that’s used to determine which resource can be processed next in the loop. |
| LoopStartVariableName | Type  textarea  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The name of the variable that’s processed when the loop starts. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the expression set version. This is a required field. |
| Rank | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The rank of the expression set version. An expression set version's rank is used to determine when the version is chosen for processing. When more than one enabled version matches an expression set call, and the start and end date time periods overlap, the version with the highest rank is chosen. |
| ShouldShowExplExternally | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the decision explanation is exposed to external users (true) or not (false).  The default value for this field is `false`.  This field is available in API version 56.0 and later. |
| StartDateTime | Type  dateTime  Properties  Create, Defaulted on create, Filter, Nillable, Sort, Update  Description  The date and time when the expression set version becomes active. |
| VersionNumber | Type  int  Properties  Create, Filter, Group, Sort, Update  Description  The version number of this expression set. This is a required field. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later

[ExpressionSetVersionFeed](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm "HTML (New Window)")
:   Feed tracking is available for the object.

[ExpressionSetVersionHistory](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm "HTML (New Window)")
:   History is available for tracked fields of the object.
