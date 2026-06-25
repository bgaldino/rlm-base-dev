---
page_id: tooling_api_objects_ctxattrhydrationctx.htm
title: CtxAttrHydrationCtx
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_ctxattrhydrationctx.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-06-25
---

# CtxAttrHydrationCtx

Represents the queries that fetch the data for a chosen attribute from the
input schema for context-to-context mapping This object is available in API version
61.0 and later.

## Supported Calls

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
| ContextAttributeMappingId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The context attribute mapping record that's associated with the attribute hydration detail.  This field is a relationship field.  Relationship Name  ContextAttributeMapping  Relationship Type  Master-detail  Refers To  ContextAttributeMapping (the master object) |
| ContextQueryAttribute | Type  string  Properties  Create, Filter, Sort, Update  Description  The attribute in context definition that's the source of context hydration. |
| InheritedFrom | Type  string  Properties  Create, Filter, Nillable, Sort, Update  Description  The name of the parent CtxAttrCtxHydrationDetail that's used to derive the current CtxAttrCtxHydrationDetail. |
