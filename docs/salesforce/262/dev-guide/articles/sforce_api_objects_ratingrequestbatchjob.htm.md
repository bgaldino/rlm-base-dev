---
page_id: sforce_api_objects_ratingrequestbatchjob.htm
title: RatingRequestBatchJob
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_ratingrequestbatchjob.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_std_objects_parent.htm
fetched_at: 2026-06-09
---

# RatingRequestBatchJob

Represents a junction between the rating request and batch job
objects. This object is available in API version 62.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| BatchJobId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  ID of the batch job that triggered the rating request on the aggregated records.  This field is a relationship field.  Relationship Name  BatchJob  Refers To  BatchJob |
| ErrorCode | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Error code that defines the batch job failure.  Valid values are:  - `BadRequest` - `InternalError` |
| ErrorMessage | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Error message that describes the cause of the batch job failure. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Timestamp for when the current user last referred to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Name of the rating request batch job record. |
| RatingRequestId | Type  reference  Properties  Create, Filter, Group, Sort  Description  ID of the rating request record associated with the batch job.  This field is a relationship field.  Relationship Name  RatingRequest  Relationship Type  Master-detail  Refers To  RatingRequest (the master object) |

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re
available in the same API versions as this object. Otherwise, they’re available in the
specified API version and later.

[RatingRequestBatchJobFeed](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm)
:   Feed tracking is available for the object.

[RatingRequestBatchJobHistory](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm)
:   History is available for tracked fields of the object.
