---
page_id: tooling_api_objects_contextdefinitionreference.htm
title: ContextDefinitionReference
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextdefinitionreference.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-06-25
---

# ContextDefinitionReference

Represents information about reference from one Context Definition to another
Context Definition.  This object is available in API version 60.0 and
later.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

| Field | Details |
| --- | --- |
| ContextDefinitionId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The context definition record that's associated with the context definition reference.  This field is a relationship field.  Relationship Name  ContextDefinition  Relationship Type  Master-detail  Refers To  ContextDefinition |
| InheritedFrom | Type  string  Properties  Create, Filter, Nillable, Sort, Update  Description  The name of the parent context definition that's used to derive the current context definition. This field is available in API version 60.0 and later. |
| ManageableState | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package.  Possible values are:  - `beta`—Managed-Beta - `deleted`—Managed-Proposed-Deleted - `deprecated`—Managed-Proposed-Deprecated - `deprecatedEditable`—SecondGen-Installed-Deprecated - `installed`—Managed-Installed - `installedEditable`—SecondGen-Installed-Editable - `released`—Managed-Released - `unmanaged`—Unmanaged |
| ReferenceContextDefinition | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies the referred context definition. |
