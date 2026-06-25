---
page_id: tooling_api_objects_contexttag.htm
title: ContextTag
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contexttag.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-06-25
---

# ContextTag

Represents a shortened name of an attribute or node instead of its fully
qualified tag structure name. This object is available in API version 59.0 and later.

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
| ContextAttributeId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The context attribute record that's associated with the context tag.  This field is a relationship field.  Relationship Name  ContextAttribute  Relationship Type  Lookup  Refers To  ContextAttribute |
| ContextNodeId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The context node record that's associated with the context tag.  This field is a relationship field.  Relationship Name  ContextNode  Relationship Type  Lookup  Refers To  ContextNode |
| Title | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The name of the context tag. |
| InheritedFrom | Type  string  Properties  Create, Filter, Nillable, Sort, Update  Description  The name of the parent context tag that's used to derive the current context tag. This field is available in API version 60.0 and later. |
