---
page_id: tooling_api_objects_contextdefinitionversion.htm
title: ContextDefinitionVersion
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextdefinitionversion.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-06-25
---

# ContextDefinitionVersion

Represents information about the context definition version. Only one version
can be active at a time. This object is available in API version 59.0 and later.

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
| ContextDefinitionId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The context definition record associated with the context definition version.  This field is a relationship field.  Relationship Name  ContextDefinition  Relationship Type  Lookup  Refers To  ContextDefinition |
| EndDate | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the context definition version becomes inactive. |
| IsActive | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the context definition version is active (true) or not (false).  The default value is `false`. |
| ManageableState | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package.  Possible values are:  - `beta`—Managed-Beta - `deleted`—Managed-Proposed-Deleted - `deprecated`—Managed-Proposed-Deprecated - `deprecatedEditable`—SecondGen-Installed-Deprecated - `installed`—Managed-Installed - `installedEditable`—SecondGen-Installed-Editable - `released`—Managed-Released - `unmanaged`—Unmanaged |
| StartDate | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The date and time when the context definition version becomes active. |
| VersionNumber | Type  int  Properties  Create, Filter, Group, Sort, Update  Description  The context definition version number. |
