---
page_id: tooling_api_objects_contextdefinitionsync.htm
title: ContextDefinitionSync
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextdefinitionsync.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-06-25
---

# ContextDefinitionSync

Stores information for the sync operation of the custom definition
with the standard definition. This object is available in API version 62.0 and
later.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

| Field | Details |
| --- | --- |
| ContextDefinitionName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The context definition the sync is running for. |
| EndDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the synchronization ends. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the context definition sync record. This is a default field created for a platform entity. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the owner who created the record. This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| StartDateTime | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The date and time when the synchronization starts. |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The status of the sync operation.  Valid values are:  - `failed` - `in_progress` - `success` |
| SynchronizationInformation | Type  textarea  Properties  Create, Nillable, Update  Description  The details of the context definition synchronization. |
