---
page_id: sforce_api_objects_ratingrequest.htm
title: RatingRequest
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_ratingrequest.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_std_objects_parent.htm
fetched_at: 2026-06-09
---

# RatingRequest

Represents the common run-time parameters, such as context definition
and rating procedure for a set of records in the rateable summary table. This object
is available in API version 62.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| ContextDefinition | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Context definition that's used for context instance creation, which encapsulates all aggregated records that are stamped for the rating request. |
| ContextMapping | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Context mapping that's used for context instance creation, which encapsulates all aggregated records that are stamped for the rating request. If no ID is provided, default context mapping is used. |
| DoesExcludeWaterfall | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the waterfall isn't generated for the rating request (`true`) or is generated (`false`). The default value is `false`. Available in API version 64.0 and later. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Timestamp for when the current user last referred to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Auto-generated identifier for the rating request record. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  ID of the user who created the record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| RatingProcedureName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Procedure name that's used to rate the aggregated records that are stamped for rating request. |
| Status | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Status of the rating request.  Valid values are:  - `Failed` - `Pending` - `RatingComplete` - `RatingInProgress` - `ReadyForRating` |

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re
available in the same API versions as this object. Otherwise, they’re available in the
specified API version and later.

[RatingRequestFeed](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm)
:   Feed tracking is available for the object.

[RatingRequestHistory](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm)
:   History is available for tracked fields of the object.

[RatingRequestShare](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm)
:   Sharing is available for the object.
