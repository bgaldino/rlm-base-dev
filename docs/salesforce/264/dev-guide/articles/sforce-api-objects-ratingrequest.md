---
page_id: sforce-api-objects-ratingrequest
title: RatingRequest
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-ratingrequest.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Rate Management
parent_page: rate-management-std-objects-parent
legacy_page_id: sforce_api_objects_ratingrequest.htm
fetched_at: 2026-11-25
---

# RatingRequest

Represents the common run-time parameters, such as context definition and rating procedure for a set of records in the rateable summary table. This object is available in API version 62.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### ContextDefinition

- **Type**: string

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: Context definition that’s used for context instance creation, which encapsulates all aggregated records that are stamped for the rating request.

### ContextMapping

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: Context mapping that’s used for context instance creation, which encapsulates all aggregated records that are stamped for the rating request. If no ID is provided, default context mapping is used.

### DoesExcludeWaterfall

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Indicates whether the waterfall isn’t generated for the rating request (`true`) or is generated (`false`). The default value is `false`. Available in API version 64.0 and later.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Timestamp for when the current user last referred to this record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Timestamp for when the current user last viewed a record related to this record.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Auto-generated identifier for the rating request record.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: ID of the user who created the record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### RatingProcedureName

- **Type**: string

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: Procedure name that’s used to rate the aggregated records that are stamped for rating request.

### Status

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: Status of the rating request.

Valid values are `Failed`, `Pending`, `RatingComplete`, `RatingInProgress`, or `ReadyForRating`.

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[RatingRequestFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[RatingRequestHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[RatingRequestShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-ratingrequest.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
