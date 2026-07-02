---
page_id: tooling_api_objects_expressionsetobjectalias.htm
title: ExpressionSetObjectAlias
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_expressionsetobjectalias.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_tooling_objects_parent.htm
fetched_at: 2026-06-25
---

# ExpressionSetObjectAlias

Represents the alias of the source object that's used in an
expression set. This object is available in API version 56.0 and later.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `search()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Special Access Rules

To use this object, users must have the Modify All Data permission, and the
orgHasExpressionSet org permission.

## Fields

| Field | Details |
| --- | --- |
| DataType | Type  picklist  Properties  Defaulted on create, Filter, Group, Restricted picklist, Sort  Description  Specifies the data type of the object alias. This is a required field.  Possible values are:  - `JSON` - `sObject`  The default value is `sObject`. |
| DeveloperName | Type  string  Properties  Filter, Group, Sort  Description  The developer name of the expression set object alias. |
| FullName | Type  string  Properties  Create, Group, Nillable  Description  The name of the expression set object alias. |
| Language | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The language in which the expression set object alias is created.  Possible values are:  - `da`—Danish - `de`—German - `en_US`—English - `es`—Spanish - `es_MX`—Spanish   (Mexico) - `fi`—Finnish - `fr`—French - `it`—Italian - `ja`—Japanese - `ko`—Korean - `nl_NL`—Dutch - `no`—Norwegian - `pt_BR`—Portuguese   (Brazil) - `ru`—Russian - `sv`—Swedish - `th`—Thai - `zh_CN`—Chinese   (Simplified) - `zh_TW`—Chinese   (Traditional) |
| ManageableState | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package.  Possible values are:  - `beta`—Managed-Beta - `deleted`—Managed-Proposed-Deleted - `deprecated`—Managed-Proposed-Deprecated - `deprecatedEditable`—SecondGen-Installed-Deprecated - `installed`—Managed-Installed - `installedEditable`—SecondGen-Installed-Editable - `released`—Managed-Released - `unmanaged`—Unmanaged |
| MasterLabel | Type  string  Properties  Filter, Group, Sort  Description  The label of the expression set object alias. |
| Metadata | Type  complexvalue  Properties  Create, Nillable, Update  Description  Expression set object alias metadata. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. |
| ObjectAlias | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The alias that corresponds to the source object that's used in an expression set. In the context of an expression set, this alias in a group that contains the aliases of fields from the source object. The length of the object alias can’t exceed 40 characters. This is a required field. |
| ObjectApiName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The API name of the source object associated with the alias that's being used in an expression set. |
| UsageType | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The type of application associated with the industry that's using an expression set.  Possible values are:  - `Bre`–Default - `ProductCategoryQualification` - `ProductQualification` - `RecordAlert`  When Business Rules Engine is enabled for a Salesforce org, the default value is '`Bre`’. Other usage types may be available to you depending on your industry solution and permission sets. |
