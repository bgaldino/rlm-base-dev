---
page_id: tooling_api_objects_contextattribute.htm
title: ContextAttribute
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextattribute.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-06-25
---

# ContextAttribute

Represents information about an attribute used to describe a context node.
Each node can have one or many attributes associated with it.  This object is
available in API version 59.0 and later.

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
| ContextNodeId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The context node record that's associated with the context attribute.  This field is a relationship field.  Relationship Name  ContextNode  Relationship Type  Lookup  Refers To  ContextNode |
| DataType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies the type of data that's stored in the context attribute.  Possible values are:  - `boolean`Boolean - `currency`—Currency - `date`—Date - `datetime`—Datetime - `lookup`—Lookup - `number`—Number - `percent`—Percent - `picklist`—Picklist - `reference`—Reference - `string`—String    The default value is `string`. |
| DomainSet | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The list of node references to show a parent-child relationship between nodes in a definition. |
| FieldType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  List of node references to depict parent/child relation between the nodes in a definition  Possible values are:  - `input`—INPUT - `inputoutput`—INPUTOUTPUT - `output`—OUTPUT  The default value is `input`. |
| IsKey | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the attribute is a key attribute in the node (true) or not (false).  The default value is `false`. |
| IsTransient | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates if an attribute must be skipped in context persistence.  The default value is `false`. |
| IsValue | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates the attribute that identifies as a value in a node.  The default value is `false`. |
| ManageableState | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package.  Possible values are:  - `beta`—Managed-Beta - `deleted`—Managed-Proposed-Deleted - `deprecated`—Managed-Proposed-Deprecated - `deprecatedEditable`—SecondGen-Installed-Deprecated - `installed`—Managed-Installed - `installedEditable`—SecondGen-Installed-Editable - `released`—Managed-Released - `unmanaged`—Unmanaged |
| Title | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The name of the context attribute. |
| InheritedFrom | Type  string  Properties  Create, Filter, Nillable, Sort, Update  Description  The name of the parent attribute that's used to derive the current attribute. This field is available in API version 60.0 and later. |
