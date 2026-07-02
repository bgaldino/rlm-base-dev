---
page_id: tooling_api_objects_expressionsetdefinition.htm
title: ExpressionSetDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_expressionsetdefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_tooling_objects_parent.htm
fetched_at: 2026-06-25
---

# ExpressionSetDefinition

Represents information about an expression set definition. This
object is available in API version 55.0 and later.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

| Field | Details |
| --- | --- |
| DeveloperName | Type  string  Properties  Filter, Group, Sort  Description  The developer name of the expression set definition. |
| FullName | Type  string  Properties  Create, Group, Nillable  Description  Full name of the associated metadata type in Metadata API. Query this field only if the query result contains no more than one record. Otherwise, an error is returned. If more than one record exists, use multiple queries to retrieve the records. This limit protects performance. |
| ExecutionScale | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the scale of the input that an expression set processes. The scale determines where the expression set is executed.  Possible values are:  - `High` - `Low` |
| Language | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The language in which the expression set definition is created.  Possible values are:  - `da`—Danish - `de`—German - `en_US`—English - `es`—Spanish - `es_MX`—Spanish   (Mexico) - `fi`—Finnish - `fr`—French - `it`—Italian - `ja`—Japanese - `ko`—Korean - `nl_NL`—Dutch - `no`—Norwegian - `pt_BR`—Portuguese   (Brazil) - `ru`—Russian - `sv`—Swedish - `th`—Thai - `zh_CN`—Chinese   (Simplified) - `zh_TW`—Chinese   (Traditional) |
| ManageableState | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package.  Possible values are:  - `beta`—Managed-Beta - `deleted`—Managed-Proposed-Deleted - `deprecated`—Managed-Proposed-Deprecated - `deprecatedEditable`—SecondGen-Installed-Deprecated - `installed`—Managed-Installed - `installedEditable`—SecondGen-Installed-Editable - `released`—Managed-Released - `unmanaged`—Unmanaged |
| MasterLabel | Type  string  Properties  Filter, Group, Sort  Description  The label of the expression set definition. |
| Metadata | Type  complexvalue  Properties  Create, Nillable, Update  Description  Expression set definition metadata. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. |
| Type | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The type of the expression set definition.  Possible values are:  - `Custom` - `Standard` |
