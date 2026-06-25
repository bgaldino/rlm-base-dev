---
page_id: tooling_api_objects_contextmappingintent.htm
title: ContextMappingIntent
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextmappingintent.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-06-25
---

# ContextMappingIntent

Represents the purpose associated to a context mapping. This object is
available in API version 61.0 and later.

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
| ContextMappingId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The context mapping that's associated with usage intent.  This field is a relationship field.  Relationship Name  ContextMapping  Relationship Type  Master-detail  Refers To  ContextMapping (the master object) |
| MappingIntent | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies the purpose to identify the type of context mapping required.  Possible values are:  - `association`—Association - `hydration`—Hydration - `persistence`—Persistence - `translation`—Translation |
