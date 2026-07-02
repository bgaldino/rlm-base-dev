---
page_id: tooling_api_objects_contextdefinition.htm
title: ContextDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextdefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-06-25
---

# ContextDefinition

Represents information about a context definition. The context definition
describes the relationship between the node structures within a context. This object
is available in API version 59.0 and later.

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
| CanBeReferenceDefinition | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the context definition can be referred by other context definitions (`true`) or not (`false`).  The default value is `false`.  This field is available in API version 63.0 and later. |
| ClonedFrom | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The name of the context definition that's used to clone the current context definition. |
| ContextTtl | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Displays how long you’d like the data that’s loaded in the runtime context instances created by this context definition to stay in the cache.  The default value is 10 minutes. |
| Description | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The description of the context definition. |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The unique name of the context definition. |
| DisplayName | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The display name of the context definition. |
| HasSystemTags | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the context definition has system tags (`true`) or not (`false`).  The default value is `false`.  This field is available in API version 63.0 and later. |
| InheritedFrom | Type  string  Properties  Create, Filter, Nillable, Sort, Update  Description  The name of the parent context definition that's used to derive the current context definition. This field is available in API version 60.0 and later. |
| InheritedFromVersion | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The version number of the parent definition that's used to derive the current context definition. This field is available in API version 60.0 and later. |
| Language | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The language of the context definition. |
| ManageableState | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package  Possible values are:  - `beta`—Managed-Beta - `deleted`—Managed-Proposed-Deleted - `deprecated`—Managed-Proposed-Deprecated - `deprecatedEditable`—SecondGen-Installed-Deprecated - `installed`—Managed-Installed - `installedEditable`—SecondGen-Installed-Editable - `released`—Managed-Released - `unmanaged`—Unmanaged |
| MasterLabel | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The UI label of the context definition. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix that is associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the namespacePrefix\_\_componentName notation. |
| Title | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the context definition. |
