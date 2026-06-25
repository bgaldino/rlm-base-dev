---
page_id: tooling_api_objects_contextnodeattrdictionary.htm
title: ContextNodeAttrDictionary
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextnodeattrdictionary.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-06-25
---

# ContextNodeAttrDictionary

Represents
the
relationship between
the
ContextNodeMapping and ContextDictionary
objects
as a junction table. This object is available in API version 62.0
and later.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

| Field | Details |
| --- | --- |
| ContextAttrrDictIdentifier | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The developer name of the context attribute dictionary. |
| ContextNodeId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the context node.  This field is a relationship field.  Relationship Name  ContextNode  Relationship Type  Lookup  Refers To  ContextNode |
| ContextNodeMapingId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the context node mapping.  This field is a relationship field.  Relationship Name  ContextNodeMapping  Relationship Type  Lookup  Refers To  ContextNodeMapping |
| ContextNodeTagPrefix | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The tag prefix of the context node that's used to create the unique identifier of the parent context node. |
